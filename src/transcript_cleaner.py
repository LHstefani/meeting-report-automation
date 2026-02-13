"""
Leexi Transcript Cleaner - Parses and cleans meeting transcripts.

Processes Leexi-generated .txt transcripts:
- Parses speaker turns with timestamps
- Removes noise: garbled text, "Thank you" spam, very short filler turns
- Normalizes speaker names
- Merges consecutive turns from same speaker
- Outputs clean structured transcript
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


def clean_transcript(text, speaker_map=None):
    """Full cleaning pipeline for a Leexi transcript.

    Args:
        text: Raw transcript text
        speaker_map: Optional dict mapping speaker labels to real names
                     e.g. {"Speaker 3": "Thibault Fayt"}

    Returns:
        dict with:
        - turns: list of cleaned turns
        - speakers: dict of speaker names and turn counts
        - duration_seconds: total duration
        - stats: cleaning statistics
    """
    # Step 1: Parse raw turns
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
        'stats': {
            'raw_turns': total_raw,
            'noise_removed': noise_count,
            'after_cleaning': len(clean_turns),
            'after_merging': len(merged_turns),
        }
    }


def format_clean_transcript(result):
    """Format cleaned transcript for output as readable text."""
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
