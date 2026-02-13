"""
AI Analyzer - Uses Anthropic API to analyze meeting transcripts against previous reports.

Replaces the manual Claude Code conversation step. Takes a parsed report and cleaned
transcript, sends them to Claude, and returns structured updates ready for report_generator.
"""

import json
import re

import anthropic


MODEL = "claude-sonnet-4-20250514"
MAX_TRANSCRIPT_CHARS = 100_000

SYSTEM_PROMPT = """\
You are a construction meeting minute analyst. Your task is to compare a new meeting \
transcript against the previous meeting report and produce structured updates.

## Input
You will receive:
1. **Previous Report** (JSON): the parsed structure of the last meeting report, including \
metadata, sections with numbered points, info exchange table, and planning table.
2. **Meeting Transcript** (text): the cleaned transcript of the new meeting.

## Task
Analyze the transcript and identify:

### 1. Point Updates (`point_updates`)
For each existing point in the report that was discussed in the new meeting, produce an update:
- `section`: the section name (must match exactly one of the section names in the report)
- `number`: the existing point number (e.g. "01.01", "07.02")
- `subject_lines`: list of new lines summarizing what was discussed (1-4 concise lines)
- `for_whom`: who is responsible (abbreviation like "MO", "ARCH", "BE", or full org name), \
or null if unchanged
- `due`: due date or status (e.g. "15/03/2026", "En cours", "Done"), or null if unchanged

### 2. New Points (`new_points`)
For topics discussed that don't correspond to any existing point:
- `section`: which section this belongs to (must match an existing section name)
- `number`: suggested point number following the section's numbering pattern
- `title`: short title for the new point (2-5 words)
- `subject_lines`: list of lines describing the topic (1-4 concise lines)
- `for_whom`: who is responsible
- `due`: due date or status

### 3. Info Exchange (`info_exchange`)
Updated list of action items / information exchanges:
- Keep existing items that are still relevant (update status if discussed)
- Add new action items from the transcript
- Each item: `{"from_whom": str, "status": str, "content": str, "due_date": str}`

### 4. Planning (`planning`)
Updated planning items:
- Keep existing planning items
- Add new milestones or schedule items discussed
- Each item: `{"content": str, "is_new": bool}`
- Set `is_new: true` for items that are new or modified in this meeting

### 5. Metadata
- `meeting_number`: previous meeting number + 1
- `date`: date of the new meeting (extract from transcript if possible, otherwise leave null)
- `distribution_date`: null (to be filled manually)
- `next_meeting`: next meeting text if discussed (e.g. "25/02/2026 at 11:00 - On site"), \
or null

## Rules
- Only include point_updates for points that were actually discussed in the transcript
- Use the SAME LANGUAGE as the report (if report is in French, write updates in French; \
if English, write in English)
- Keep updates concise and factual - summarize decisions and action items
- For point numbering on new points: use the pattern MeetingNumber.SequentialNumber \
(e.g. for meeting 13 the first new point would be "13.01")
- If a transcript section is unclear or garbled, skip it rather than guessing
- Preserve exact section names from the parsed report

## Output Format
Return ONLY a valid JSON object (no markdown, no explanation) with this structure:
{
  "meeting_number": <int>,
  "date": <str or null>,
  "distribution_date": null,
  "next_meeting": <str or null>,
  "point_updates": [...],
  "new_points": [...],
  "info_exchange": [...],
  "planning": [...]
}
"""


def _build_user_message(parsed_report, cleaned_text):
    """Build the user message with report JSON and transcript text."""
    # Summarize the report structure for the prompt
    report_summary = {
        "metadata": parsed_report.get("metadata", {}),
        "language": parsed_report.get("language", "EN"),
        "next_meeting": parsed_report.get("next_meeting"),
        "info_exchange": parsed_report.get("info_exchange", []),
        "planning": parsed_report.get("planning", []),
        "sections": [],
    }

    for section in parsed_report.get("sections", []):
        section_summary = {
            "section_name": section["section_name"],
            "points": [],
        }
        for point in section.get("points", []):
            point_summary = {
                "number": point["number"],
                "title": point["title"],
                "subject_paragraphs": [
                    p["text"] for p in point.get("subject_paragraphs", [])
                    if p.get("text", "").strip()
                ],
                "for_whom": [
                    fw for fw in point.get("for_whom_paragraphs", [])
                    if fw.strip()
                ],
                "due": [
                    d for d in point.get("due_paragraphs", [])
                    if d.strip()
                ],
            }
            section_summary["points"].append(point_summary)
        report_summary["sections"].append(section_summary)

    report_json = json.dumps(report_summary, indent=2, ensure_ascii=False)

    # Truncate transcript if too long
    transcript = cleaned_text
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        transcript = transcript[:MAX_TRANSCRIPT_CHARS]
        transcript += "\n\n[... TRANSCRIPT TRUNCATED due to length ...]"

    return f"""## Previous Meeting Report

```json
{report_json}
```

## New Meeting Transcript

{transcript}
"""


def validate_updates(updates):
    """Validate the structure of the updates dict.

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    if not isinstance(updates, dict):
        return False, ["Updates must be a dictionary"]

    # Check required keys
    required_keys = ["meeting_number", "point_updates", "new_points",
                     "info_exchange", "planning"]
    for key in required_keys:
        if key not in updates:
            errors.append(f"Missing required key: {key}")

    # Validate meeting_number
    if "meeting_number" in updates:
        if not isinstance(updates["meeting_number"], int):
            errors.append("meeting_number must be an integer")

    # Validate point_updates
    for i, pu in enumerate(updates.get("point_updates", [])):
        if not isinstance(pu, dict):
            errors.append(f"point_updates[{i}] must be a dict")
            continue
        for field in ["section", "number", "subject_lines"]:
            if field not in pu:
                errors.append(f"point_updates[{i}] missing '{field}'")
        if "subject_lines" in pu and not isinstance(pu["subject_lines"], list):
            errors.append(f"point_updates[{i}].subject_lines must be a list")

    # Validate new_points
    for i, np in enumerate(updates.get("new_points", [])):
        if not isinstance(np, dict):
            errors.append(f"new_points[{i}] must be a dict")
            continue
        for field in ["section", "number", "title", "subject_lines",
                       "for_whom", "due"]:
            if field not in np:
                errors.append(f"new_points[{i}] missing '{field}'")

    # Validate info_exchange
    for i, ie in enumerate(updates.get("info_exchange", [])):
        if not isinstance(ie, dict):
            errors.append(f"info_exchange[{i}] must be a dict")
            continue
        for field in ["from_whom", "status", "content", "due_date"]:
            if field not in ie:
                errors.append(f"info_exchange[{i}] missing '{field}'")

    # Validate planning
    for i, pl in enumerate(updates.get("planning", [])):
        if not isinstance(pl, dict):
            errors.append(f"planning[{i}] must be a dict")
            continue
        if "content" not in pl:
            errors.append(f"planning[{i}] missing 'content'")
        if "is_new" not in pl:
            errors.append(f"planning[{i}] missing 'is_new'")

    return len(errors) == 0, errors


def _extract_json_from_response(text):
    """Extract JSON from API response, handling potential markdown wrapping."""
    # Try direct parse first
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding the first { ... } block
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(text[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from API response")


def analyze_meeting(parsed_report, cleaned_text, api_key):
    """Analyze a meeting transcript against the previous report using Claude API.

    Args:
        parsed_report: dict from report_parser.parse_report()
        cleaned_text: formatted string from transcript_cleaner.format_clean_transcript()
        api_key: Anthropic API key

    Returns:
        dict: Updates structure ready for report_generator.generate_report(),
              or dict with "error" key on failure.
              Also includes "usage" key with token counts.
    """
    client = anthropic.Anthropic(api_key=api_key)
    user_message = _build_user_message(parsed_report, cleaned_text)

    response_text = None
    last_error = None
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            response_text = response.content[0].text
            updates = _extract_json_from_response(response_text)

            is_valid, errors = validate_updates(updates)
            if not is_valid and attempt == 0:
                last_error = f"Validation errors: {'; '.join(errors)}"
                continue

            # Add usage info
            updates["usage"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            if not is_valid:
                updates["validation_warnings"] = errors

            return updates

        except anthropic.APIError as e:
            last_error = f"API error: {str(e)}"
            if attempt == 0:
                continue
        except ValueError as e:
            last_error = str(e)
            if attempt == 0:
                continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            break

    return {
        "error": last_error,
        "raw_response": response_text,
    }
