"""
Meeting Report Automation - CLI Entry Point

Orchestrates the parsing and cleaning steps. The review and generation
steps are handled interactively by Claude Code.

Usage:
    python run.py parse <report.docx>           Parse report to JSON
    python run.py clean <transcript.txt>         Clean transcript
    python run.py prepare <report.docx> <transcript.txt>  Parse + clean (full prep)
    python run.py generate <report.docx> <updates.json>   Generate new report
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from report_parser import parse_report
from transcript_cleaner import clean_transcript, format_clean_transcript
from report_generator import generate_report


def cmd_parse(args):
    """Parse a .docx report to JSON."""
    if not args:
        print("Usage: python run.py parse <report.docx> [output.json]")
        return 1

    docx_path = Path(args[0])
    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        return 1

    result = parse_report(docx_path)

    if len(args) >= 2:
        output_path = Path(args[1])
    else:
        output_path = Path('output') / f"{docx_path.stem}_parsed.json"

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Parsed: {docx_path.name}")
    print(f"  Meeting N{result['metadata'].get('meeting_number')}")
    print(f"  Date: {result['metadata'].get('date')}")
    print(f"  Language: {result['language']}")
    print(f"  Sections: {len(result['sections'])}")
    for s in result['sections']:
        print(f"    - {s['section_name']}: {len(s['points'])} points")
    print(f"  Output: {output_path}")
    return 0


def cmd_clean(args):
    """Clean a Leexi transcript."""
    if not args:
        print("Usage: python run.py clean <transcript.txt> [output.txt]")
        return 1

    input_path = Path(args[0])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return 1

    text = input_path.read_text(encoding='utf-8')
    result = clean_transcript(text)

    if len(args) >= 2:
        output_path = Path(args[1])
    else:
        output_path = Path('output') / f"{input_path.stem}_cleaned.txt"

    output_path.parent.mkdir(exist_ok=True)
    output_text = format_clean_transcript(result)
    output_path.write_text(output_text, encoding='utf-8')

    stats = result['stats']
    print(f"Cleaned: {input_path.name}")
    print(f"  Turns: {stats['raw_turns']} raw -> {stats['after_merging']} clean")
    print(f"  Noise removed: {stats['noise_removed']}")
    print(f"  Speakers: {', '.join(result['speakers'].keys())}")
    print(f"  Output: {output_path}")
    return 0


def cmd_prepare(args):
    """Parse report + clean transcript (full preparation step)."""
    if len(args) < 2:
        print("Usage: python run.py prepare <report.docx> <transcript.txt>")
        return 1

    # Run both
    print("=== Step 1: Parsing previous report ===")
    ret = cmd_parse([args[0]])
    if ret != 0:
        return ret

    print()
    print("=== Step 2: Cleaning transcript ===")
    ret = cmd_clean([args[1]])
    if ret != 0:
        return ret

    print()
    print("=== Preparation complete ===")
    print("Next: Review the parsed report and cleaned transcript,")
    print("then generate the review proposals in Claude Code.")
    return 0


def cmd_generate(args):
    """Generate a new report from previous + updates JSON."""
    if len(args) < 2:
        print("Usage: python run.py generate <previous_report.docx> <updates.json> [output.docx]")
        return 1

    previous_path = Path(args[0])
    updates_path = Path(args[1])

    if not previous_path.exists():
        print(f"Error: File not found: {previous_path}")
        return 1
    if not updates_path.exists():
        print(f"Error: File not found: {updates_path}")
        return 1

    with open(updates_path, 'r', encoding='utf-8') as f:
        updates = json.load(f)

    if len(args) >= 3:
        output_path = Path(args[2])
    else:
        # Auto-generate output name
        num = updates.get('meeting_number', '??')
        date = updates.get('date', datetime.now().strftime('%d/%m/%Y'))
        # Convert DD/MM/YYYY to YYYYMMDD for filename
        try:
            dt = datetime.strptime(date, '%d/%m/%Y')
            date_compact = dt.strftime('%Y%m%d')
        except ValueError:
            date_compact = date.replace('/', '')
        # Extract project name from source file
        stem = previous_path.stem
        project = stem.split('_')[0] if '_' in stem else 'Report'
        output_path = Path('output') / f"{project}_MoM-PV N{num:02d} {date_compact}.docx"

    output_path.parent.mkdir(exist_ok=True)
    generate_report(str(previous_path), str(output_path), updates)

    print(f"Generated: {output_path.name}")
    print(f"  Based on: {previous_path.name}")
    print(f"  Meeting N{updates.get('meeting_number')}")
    print(f"  Date: {updates.get('date')}")
    print(f"  Output: {output_path}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        'parse': cmd_parse,
        'clean': cmd_clean,
        'prepare': cmd_prepare,
        'generate': cmd_generate,
    }

    if command in commands:
        return commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
