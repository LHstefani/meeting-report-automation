"""
Meeting Transcript Cleaner - Parses and cleans meeting transcripts.

Supports two formats:
1. Leexi format: Speaker turns with timestamps ("Name at MM:SS - MM:SS")
2. Plain text: Free-flowing transcript without speaker labels (e.g. workshop notes)

Processing steps (Leexi):
- Parses speaker turns with timestamps
- Removes noise: garbled text, "Thank you" spam, very short filler turns
- Normalizes speaker names
- Merges consecutive turns from same speaker

Processing steps (Plain text):
- Parses optional header (title, attendance)
- Splits into paragraphs
- Passes through meeting notes/agenda if present at end
"""

import re
import sys
from pathlib import Path


# Pattern for speaker line: "Name at MM:SS - MM:SS" or "Name at 1hMM:SS - 1hMM:SS"
SPEAKER_PATTERN = re.compile(
    r'^(.+?)\s+at\s+(\d+h?\d{1,2}:\d{2})\s*-\s*(\d+h?\d{1,2}:\d{2})$'
)

# Noise phrases that appear as transcription artifacts
NOISE_PHRASES = [
    "thank you", "bye", "gracias", "merci beaucoup",
    "au revoir", "muy bien", "right", "hi",
    "okay", "ok", "yep", "oui", "non",
    "hmm", "ummm", "um", "euh",
    "see you", "thanks a lot", "da",
    "sí, sí", "yeah, yeah", "c'est bon",
]

# Garbled multilingual artifacts from AI transcription
GARBLED_PATTERNS = [
    r'Amén\.\s*Ahora',  # Spanish artifacts
    r'Жесть',  # Russian artifacts
    r'Nipon\s+Odeyanou',  # Garbled
    r'Strowman',  # Misheard names
    r'Soyez\s+sémaux',  # Garbled
    r'non-coïncidence',  # Garbled filler
    r'Mélissante',  # Garbled
]


def parse_timestamp(ts_str):
    """Convert timestamp string to total seconds.

    Handles formats: "MM:SS", "1hMM:SS", "1h19:23"
    """
    match = re.match(r'(\d+)h(\d{1,2}):(\d{2})', ts_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        return hours * 3600 + minutes * 60 + seconds

    parts = ts_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0


def format_timestamp(seconds):
    """Format seconds back to readable timestamp."""
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h}h{m:02d}:{s:02d}"
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def parse_transcript(text):
    """Parse raw transcript text into structured speaker turns.

    Returns list of {speaker, start, end, start_seconds, end_seconds, text} dicts.
    """
    lines = text.split('\n')
    turns = []
    current_turn = None

    for line in lines:
        line = line.rstrip()

        # Check if this is a speaker line
        match = SPEAKER_PATTERN.match(line)
        if match:
            # Save previous turn
            if current_turn is not None:
                current_turn['text'] = current_turn['text'].strip()
                turns.append(current_turn)

            speaker = match.group(1).strip()
            start = match.group(2)
            end = match.group(3)

            current_turn = {
                'speaker': speaker,
                'start': start,
                'end': end,
                'start_seconds': parse_timestamp(start),
                'end_seconds': parse_timestamp(end),
                'text': '',
            }
        elif current_turn is not None:
            # Append text to current turn
            if line.strip():
                if current_turn['text']:
                    current_turn['text'] += ' '
                current_turn['text'] += line.strip()

    # Don't forget the last turn
    if current_turn is not None:
        current_turn['text'] = current_turn['text'].strip()
        turns.append(current_turn)

    return turns


def is_noise_turn(turn, min_word_count=3):
    """Check if a turn is noise (very short, filler, or garbled).

    A turn is noise if:
    - Empty text
    - Text is purely a known noise phrase
    - Very short (< min_word_count words) AND matches noise patterns
    - Duration is 0 seconds (same start/end timestamp)
    """
    text = turn['text'].strip()
    if not text:
        return True

    text_lower = text.lower().rstrip('.!?,; ')

    # Check if entire text is a noise phrase
    for phrase in NOISE_PHRASES:
        if text_lower == phrase:
            return True

    # Check for repeated "Thank you" spam
    cleaned = re.sub(r'(?:thank you|merci|bye|gracias)[.\s]*', '', text_lower, flags=re.IGNORECASE)
    if not cleaned.strip():
        return True

    # Very short turns that are just filler
    words = text.split()
    if len(words) <= 2 and turn['end_seconds'] - turn['start_seconds'] <= 2:
        # Check if it's a meaningful short response
        if text_lower not in ('oui,', 'non,', 'ok.', 'oui.', 'non.'):
            return True

    return False


def clean_turn_text(text):
    """Remove inline noise from turn text while preserving meaningful content."""
    # Remove trailing/leading noise phrases
    # Remove isolated "Thank you", "Bye", etc. that appear mid-sentence as artifacts
    noise_inline = [
        r'\bThank you\.?\s*',
        r'\bBye\.?\s*',
        r'\bGracias\.?\s*',
        r'\bMerci\.?\s*(?!beaucoup)',  # Keep "Merci beaucoup" if part of meaningful sentence
        r'\bRight\.?\s*',
        r'\bYeah,?\s+yeah,?\s*',
        r'\bWow\.?\s*',
        r'\bDa\.?\s*',
    ]

    cleaned = text
    for pattern in noise_inline:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Remove garbled artifacts
    for pattern in GARBLED_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up multiple spaces and trailing punctuation artifacts
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    cleaned = cleaned.strip()

    # Remove leading/trailing isolated punctuation
    cleaned = re.sub(r'^[,.\s]+', '', cleaned)
    cleaned = re.sub(r'[,\s]+$', '', cleaned.rstrip('.')) + '.' if cleaned else ''
    if cleaned == '.':
        cleaned = ''

    return cleaned


def merge_consecutive_turns(turns):
    """Merge consecutive turns from the same speaker.

    If the same speaker has multiple consecutive turns (perhaps interrupted
    by noise turns that were removed), merge them into one.
    """
    if not turns:
        return turns

    merged = [turns[0].copy()]
    for turn in turns[1:]:
        if turn['speaker'] == merged[-1]['speaker']:
            # Merge: extend text and end time
            merged[-1]['text'] += ' ' + turn['text']
            merged[-1]['end'] = turn['end']
            merged[-1]['end_seconds'] = turn['end_seconds']
        else:
            merged.append(turn.copy())

    return merged


def extract_speaker_names(turns):
    """Build a map of all speakers found in the transcript.

    Returns dict of {speaker_name: turn_count}.
    """
    speakers = {}
    for turn in turns:
        name = turn['speaker']
        speakers[name] = speakers.get(name, 0) + 1
    return speakers


def is_leexi_format(text):
    """Detect if the transcript is in Leexi format (speaker + timestamp lines).

    Returns True if at least 3 speaker pattern lines found, indicating Leexi format.
    """
    matches = SPEAKER_PATTERN.findall(text)
    return len(matches) >= 3


def parse_plain_transcript(text):
    """Parse a plain text transcript (no speaker labels/timestamps).

    Extracts:
    - Header info (title line, attendance if present)
    - Body paragraphs (splitting on blank lines)
    - Trailing meeting notes/agenda (if present)
    """
    lines = text.split('\n')

    header_lines = []
    body_lines = []
    notes_lines = []
    in_notes = False

    # Parse header: first non-empty lines until first blank line
    header_done = False
    for line in lines:
        stripped = line.strip()

        if not header_done:
            if not stripped and header_lines:
                header_done = True
            elif stripped:
                header_lines.append(stripped)
            continue

        # Detect meeting notes/agenda section at the end
        # These typically start with "Agenda", "Notes:", "###" or similar markers
        if not in_notes and re.match(
            r'^(?:Agenda|Notes?|###|\*\*\*|---)', stripped, re.IGNORECASE
        ):
            in_notes = True

        if in_notes:
            notes_lines.append(line)
        else:
            body_lines.append(line)

    # Split body into paragraphs (groups of non-empty lines separated by blank lines)
    paragraphs = []
    current_para = []
    for line in body_lines:
        if line.strip():
            current_para.append(line.strip())
        elif current_para:
            paragraphs.append(' '.join(current_para))
            current_para = []
    if current_para:
        paragraphs.append(' '.join(current_para))

    # Parse attendance from header if present
    attendance = {}
    for hl in header_lines:
        # Pattern: "Organization: Name1, Name2"
        att_match = re.match(r'^(.+?):\s*(.+)$', hl)
        if att_match and not re.match(r'^Transcript', hl, re.IGNORECASE):
            org = att_match.group(1).strip()
            names = [n.strip() for n in att_match.group(2).split(',')]
            attendance[org] = names

    # Extract title from first header line
    title = header_lines[0] if header_lines else "Meeting Transcript"

    return {
        'title': title,
        'attendance': attendance,
        'paragraphs': paragraphs,
        'notes': '\n'.join(notes_lines) if notes_lines else None,
    }


def clean_plain_transcript(text):
    """Clean a plain text transcript (non-Leexi format).

    Returns a structure compatible with the Leexi clean output.
    """
    parsed = parse_plain_transcript(text)

    # Build pseudo-turns from paragraphs (one turn per paragraph, no speaker)
    turns = []
    for i, para in enumerate(parsed['paragraphs']):
        if not para.strip():
            continue
        turns.append({
            'speaker': 'Discussion',
            'start': f'{i:02d}:00',
            'end': f'{i:02d}:00',
            'start_seconds': i * 60,
            'end_seconds': i * 60,
            'text': para,
        })

    return {
        'turns': turns,
        'speakers': {'Discussion': len(turns)},
        'duration_seconds': 0,
        'format': 'plain_text',
        'title': parsed['title'],
        'attendance': parsed['attendance'],
        'notes': parsed['notes'],
        'stats': {
            'raw_turns': len(parsed['paragraphs']),
            'noise_removed': 0,
            'after_cleaning': len(turns),
            'after_merging': len(turns),
        }
    }


def format_plain_transcript(result):
    """Format a cleaned plain text transcript for output."""
    lines = []
    lines.append(f"=== CLEANED TRANSCRIPT ===")
    lines.append(f"Format: Plain text")
    lines.append(f"Title: {result.get('title', 'Unknown')}")

    attendance = result.get('attendance', {})
    if attendance:
        lines.append("Attendance:")
        for org, names in attendance.items():
            lines.append(f"  {org}: {', '.join(names)}")

    lines.append(f"Paragraphs: {result['stats']['after_merging']}")
    lines.append("")

    for turn in result['turns']:
        lines.append(turn['text'])
        lines.append("")

    notes = result.get('notes')
    if notes:
        lines.append("=== MEETING NOTES / AGENDA ===")
        lines.append(notes)

    return '\n'.join(lines)


def clean_transcript(text, speaker_map=None):
    """Full cleaning pipeline for a meeting transcript.

    Auto-detects format (Leexi or plain text) and applies appropriate cleaning.

    Args:
        text: Raw transcript text
        speaker_map: Optional dict mapping speaker labels to real names
                     e.g. {"Speaker 3": "Thibault Fayt"} (Leexi only)

    Returns:
        dict with:
        - turns: list of cleaned turns
        - speakers: dict of speaker names and turn counts
        - duration_seconds: total duration
        - stats: cleaning statistics
        - format: 'leexi' or 'plain_text'
    """
    # Auto-detect format
    if not is_leexi_format(text):
        return clean_plain_transcript(text)

    # Step 1: Parse raw turns (Leexi format)
    raw_turns = parse_transcript(text)
    total_raw = len(raw_turns)

    # Step 2: Apply speaker name mapping
    if speaker_map:
        for turn in raw_turns:
            if turn['speaker'] in speaker_map:
                turn['speaker'] = speaker_map[turn['speaker']]

    # Step 3: Filter noise turns
    clean_turns = []
    noise_count = 0
    for turn in raw_turns:
        if is_noise_turn(turn):
            noise_count += 1
            continue

        # Clean the text content
        turn['text'] = clean_turn_text(turn['text'])
        if turn['text']:  # Only keep if text remains after cleaning
            clean_turns.append(turn)
        else:
            noise_count += 1

    # Step 4: Merge consecutive same-speaker turns
    merged_turns = merge_consecutive_turns(clean_turns)

    # Step 5: Build statistics
    speakers = extract_speaker_names(merged_turns)
    duration = max(t['end_seconds'] for t in merged_turns) if merged_turns else 0

    return {
        'turns': merged_turns,
        'speakers': speakers,
        'duration_seconds': duration,
        'format': 'leexi',
        'stats': {
            'raw_turns': total_raw,
            'noise_removed': noise_count,
            'after_cleaning': len(clean_turns),
            'after_merging': len(merged_turns),
        }
    }


def format_clean_transcript(result):
    """Format cleaned transcript for output as readable text.

    Auto-dispatches between Leexi and plain text formats.
    """
    if result.get('format') == 'plain_text':
        return format_plain_transcript(result)

    lines = []
    lines.append(f"=== CLEANED TRANSCRIPT ===")
    lines.append(f"Duration: {format_timestamp(result['duration_seconds'])}")
    lines.append(f"Speakers: {', '.join(result['speakers'].keys())}")
    lines.append(f"Stats: {result['stats']['raw_turns']} raw -> "
                 f"{result['stats']['noise_removed']} noise removed -> "
                 f"{result['stats']['after_merging']} clean turns")
    lines.append("")

    for turn in result['turns']:
        lines.append(f"[{turn['start']} - {turn['end']}] {turn['speaker']}:")
        lines.append(f"  {turn['text']}")
        lines.append("")

    return '\n'.join(lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python transcript_cleaner.py <transcript.txt> [output.txt]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8')
    result = clean_transcript(text)

    output = format_clean_transcript(result)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
        output_path.write_text(output, encoding='utf-8')
        print(f"Cleaned transcript saved to: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
