"""
Meeting Report Automation - Streamlit Web Application

3-step flow:
1. Upload previous report (.docx) and transcript (.txt) → auto parse, clean, AI analyze
2. Review & edit proposals (metadata, point updates, new points, info exchange, planning)
3. Generate & download new report
"""

import re
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Add src/ to path so we can import existing modules
SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

from report_parser import parse_report
from transcript_cleaner import clean_transcript, format_clean_transcript
from report_generator import generate_report
from ai_analyzer import analyze_meeting


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Meeting Report Automation",
    page_icon="📋",
    layout="wide",
)


# ---------------------------------------------------------------------------
# API key handling
# ---------------------------------------------------------------------------
def get_api_key():
    """Get Anthropic API key from Streamlit secrets or sidebar input."""
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
        if key:
            return key
    except (KeyError, FileNotFoundError):
        pass

    # Only show sidebar input if secrets aren't configured (local dev)
    with st.sidebar:
        st.markdown("### API Configuration")
        key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Required for AI analysis. Get one at console.anthropic.com",
        )
        return key if key else None


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "parsed_report" not in st.session_state:
    st.session_state.parsed_report = None
if "cleaned_result" not in st.session_state:
    st.session_state.cleaned_result = None
if "cleaned_text" not in st.session_state:
    st.session_state.cleaned_text = None
if "proposals" not in st.session_state:
    st.session_state.proposals = None
if "report_bytes" not in st.session_state:
    st.session_state.report_bytes = None


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
LOGO_PATH = Path(__file__).parent / "LOGO" / "Immo Pro - logo.png"

col_logo, col_title = st.columns([1, 4])
with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
with col_title:
    st.title("Meeting Report Automation")
    st.caption("Upload files → review AI proposals → download new report")

# Progress indicator
step_labels = ["Upload & Analyze", "Review & Edit", "Download"]
cols = st.columns(3)
for i, (col, label) in enumerate(zip(cols, step_labels)):
    step_num = i + 1
    if step_num < st.session_state.step:
        col.markdown(f"~~**{step_num}. {label}**~~")
    elif step_num == st.session_state.step:
        col.markdown(f"**:blue[{step_num}. {label}]**")
    else:
        col.markdown(f"{step_num}. {label}")

st.divider()


# ---------------------------------------------------------------------------
# Step 1: Upload → Parse → Clean → AI Analyze (all automatic)
# ---------------------------------------------------------------------------
if st.session_state.step == 1:
    st.header("Step 1: Upload & Analyze")

    api_key = get_api_key()

    col1, col2 = st.columns(2)
    with col1:
        report_file = st.file_uploader(
            "Previous Meeting Report",
            type=["docx"],
            help="The .docx report from the last meeting",
        )
    with col2:
        transcript_file = st.file_uploader(
            "Meeting Transcript (Leexi)",
            type=["txt"],
            help="The .txt transcript exported from Leexi",
        )

    if not api_key:
        st.warning("Please enter your Anthropic API key in the sidebar.")

    if report_file and transcript_file and api_key:
        if st.button("Analyze Meeting", type="primary", use_container_width=True):
            try:
                # --- Parse report ---
                with st.spinner("Parsing previous report..."):
                    with tempfile.NamedTemporaryFile(
                        suffix=".docx", delete=False
                    ) as tmp:
                        tmp.write(report_file.getvalue())
                        tmp_path = tmp.name

                    parsed = parse_report(tmp_path)
                    st.session_state.parsed_report = parsed
                    st.session_state.temp_report_path = tmp_path
                    st.session_state.uploaded_report_name = report_file.name

                # --- Clean transcript ---
                with st.spinner("Cleaning transcript..."):
                    transcript_text = transcript_file.getvalue().decode("utf-8")
                    result = clean_transcript(transcript_text)
                    st.session_state.cleaned_result = result
                    st.session_state.cleaned_text = format_clean_transcript(result)

                # --- Show summary ---
                meta = parsed.get("metadata", {})
                sections = parsed.get("sections", [])
                total_points = sum(len(s.get("points", [])) for s in sections)
                stats = result.get("stats", {})
                duration = result.get("duration_seconds", 0)

                st.info(
                    f"Parsed **Meeting N{meta.get('meeting_number', '?')}** "
                    f"({meta.get('date', '?')}) — "
                    f"{len(sections)} sections, {total_points} points | "
                    f"Transcript: {stats.get('after_merging', 0)} turns, "
                    f"~{duration // 60} min"
                )

                # --- AI Analysis ---
                with st.spinner("AI analyzing transcript against report... (30-60 seconds)"):
                    proposals = analyze_meeting(
                        parsed,
                        st.session_state.cleaned_text,
                        api_key,
                    )

                if "error" in proposals:
                    st.error(f"AI analysis failed: {proposals['error']}")
                    if proposals.get("raw_response"):
                        with st.expander("Raw API response"):
                            st.code(proposals["raw_response"])
                else:
                    st.session_state.proposals = proposals

                    usage = proposals.get("usage", {})
                    input_t = usage.get("input_tokens", 0)
                    output_t = usage.get("output_tokens", 0)
                    cost = (input_t * 3 / 1_000_000) + (output_t * 15 / 1_000_000)
                    st.success(
                        f"Analysis complete! "
                        f"({input_t:,} input + {output_t:,} output tokens, ~${cost:.3f})"
                    )

                    st.session_state.step = 2
                    st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")
    elif report_file and transcript_file and not api_key:
        pass  # warning already shown above
    else:
        st.info("Please upload both files to continue.")


# ---------------------------------------------------------------------------
# Step 2: Review & Edit Proposals
# ---------------------------------------------------------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Review & Edit Proposals")

    proposals = st.session_state.proposals
    parsed = st.session_state.parsed_report
    section_names = [s["section_name"] for s in parsed.get("sections", [])]

    # Build a lookup of existing points for context display
    existing_points = {}
    for section in parsed.get("sections", []):
        for point in section.get("points", []):
            existing_points[point["number"]] = {
                "title": point["title"],
                "section": section["section_name"],
                "subject": "\n".join(
                    p["text"] for p in point.get("subject_paragraphs", [])
                    if p.get("text", "").strip()
                ),
            }

    tab_meta, tab_updates, tab_new, tab_info, tab_planning = st.tabs(
        ["Metadata", "Point Updates", "New Points", "Info Exchange", "Planning"]
    )

    # --- Tab 1: Metadata ---
    with tab_meta:
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Meeting Number",
                value=proposals.get("meeting_number", 1),
                min_value=1,
                key="meta_meeting_num",
            )
            st.text_input(
                "Date (DD/MM/YYYY)",
                value=proposals.get("date") or "",
                key="meta_date",
            )
        with col2:
            st.text_input(
                "Distribution Date (DD/MM/YYYY)",
                value=proposals.get("distribution_date") or "",
                key="meta_dist_date",
            )
            st.text_input(
                "Next Meeting Date (DD/MM/YYYY)",
                value=proposals.get("next_meeting") or "",
                key="meta_next_meeting",
                help="Only the date — time and location are preserved from the previous report",
            )
            st.text_input(
                "Next Meeting Time (HH:MM)",
                value=proposals.get("next_meeting_time") or "",
                key="meta_next_meeting_time",
                help="e.g. 11:00 — leave empty to keep the previous time",
            )

    # --- Tab 2: Point Updates ---
    with tab_updates:
        point_updates = proposals.get("point_updates", [])
        if not point_updates:
            st.info("No updates to existing points proposed.")
        else:
            st.markdown(f"**{len(point_updates)} update(s) proposed**")

        for i, pu in enumerate(point_updates):
            point_num = pu.get("number", f"?{i}")
            existing = existing_points.get(point_num, {})

            with st.expander(
                f"Update: {point_num} — {existing.get('title', pu.get('section', '?'))}",
                expanded=(i < 3),
            ):
                st.checkbox(
                    "Include this update",
                    value=True,
                    key=f"pu_include_{i}",
                )

                if existing.get("subject"):
                    st.caption("Existing content:")
                    st.text(existing["subject"][:500])

                st.caption("Proposed update:")
                st.text_area(
                    "Content",
                    value="\n".join(pu.get("subject_lines", [])),
                    key=f"pu_content_{i}",
                    height=100,
                    label_visibility="collapsed",
                )

                c1, c2 = st.columns(2)
                with c1:
                    st.text_input(
                        "For Whom",
                        value=pu.get("for_whom") or "",
                        key=f"pu_forwho_{i}",
                    )
                with c2:
                    st.text_input(
                        "Due",
                        value=pu.get("due") or "",
                        key=f"pu_due_{i}",
                    )

    # --- Tab 3: New Points ---
    with tab_new:
        new_points = proposals.get("new_points", [])
        if not new_points:
            st.info("No new points proposed.")
        else:
            st.markdown(f"**{len(new_points)} new point(s) proposed**")
            st.caption(
                "New points will be automatically numbered "
                f"{st.session_state.get('meta_meeting_num', '?')}.01, "
                f"{st.session_state.get('meta_meeting_num', '?')}.02, ... "
                "in section order (first to last page)."
            )

        for i, np_item in enumerate(new_points):
            with st.expander(
                f"New: {np_item.get('title', '?')} ({np_item.get('section', '?')})",
                expanded=(i < 3),
            ):
                st.checkbox(
                    "Include this point",
                    value=True,
                    key=f"np_include_{i}",
                )
                st.text_input(
                    "Title",
                    value=np_item.get("title", ""),
                    key=f"np_title_{i}",
                )
                st.selectbox(
                    "Section",
                    options=section_names,
                    index=(
                        section_names.index(np_item["section"])
                        if np_item.get("section") in section_names
                        else 0
                    ),
                    key=f"np_section_{i}",
                )
                st.text_area(
                    "Content",
                    value="\n".join(np_item.get("subject_lines", [])),
                    key=f"np_content_{i}",
                    height=100,
                )
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input(
                        "For Whom",
                        value=np_item.get("for_whom", ""),
                        key=f"np_forwho_{i}",
                    )
                with c2:
                    st.text_input(
                        "Due",
                        value=np_item.get("due", ""),
                        key=f"np_due_{i}",
                    )

    # --- Tab 4: Info Exchange ---
    with tab_info:
        ie_items = proposals.get("info_exchange", [])
        st.markdown(f"**{len(ie_items)} item(s)** — Edit, add, or remove rows below.")

        ie_data = [
            {
                "From": item.get("from_whom", ""),
                "Status": item.get("status", ""),
                "Content": item.get("content", ""),
                "Due Date": item.get("due_date", ""),
            }
            for item in ie_items
        ]
        if not ie_data:
            ie_data = [{"From": "", "Status": "", "Content": "", "Due Date": ""}]

        edited_ie = st.data_editor(
            ie_data,
            num_rows="dynamic",
            use_container_width=True,
            key="ie_editor",
        )

    # --- Tab 5: Planning ---
    with tab_planning:
        pl_items = proposals.get("planning", [])
        st.markdown(f"**{len(pl_items)} item(s)** — Edit, add, or remove rows below.")

        pl_data = [
            {
                "Content": item.get("content", ""),
                "Is New": item.get("is_new", False),
            }
            for item in pl_items
        ]
        if not pl_data:
            pl_data = [{"Content": "", "Is New": False}]

        edited_pl = st.data_editor(
            pl_data,
            num_rows="dynamic",
            use_container_width=True,
            key="pl_editor",
        )

    # --- Generate Button ---
    st.divider()
    if st.button("Generate Report", type="primary", use_container_width=True):
        meeting_date = st.session_state.meta_date
        meeting_num = st.session_state.meta_meeting_num

        # Build final updates dict from form state
        final_updates = {
            "meeting_number": meeting_num,
            "date": meeting_date,
            "distribution_date": st.session_state.meta_dist_date or None,
            "next_meeting": st.session_state.meta_next_meeting or None,
            "next_meeting_time": st.session_state.meta_next_meeting_time or None,
        }

        # Collect approved point updates — add meeting_date for header
        final_point_updates = []
        for i, pu in enumerate(proposals.get("point_updates", [])):
            if st.session_state.get(f"pu_include_{i}", True):
                content_text = st.session_state.get(f"pu_content_{i}", "")
                lines = [l for l in content_text.split("\n") if l.strip()]
                fw = st.session_state.get(f"pu_forwho_{i}", "") or None
                d = st.session_state.get(f"pu_due_{i}", "") or None
                final_point_updates.append({
                    "section": pu.get("section", ""),
                    "number": pu.get("number", ""),
                    "subject_lines": lines,
                    "for_whom": fw,
                    "due": d,
                    "meeting_date": meeting_date,
                })
        final_updates["point_updates"] = final_point_updates

        # Collect approved new points — re-number by section order
        raw_new_points = []
        for i, np_item in enumerate(proposals.get("new_points", [])):
            if st.session_state.get(f"np_include_{i}", True):
                content_text = st.session_state.get(f"np_content_{i}", "")
                lines = [l for l in content_text.split("\n") if l.strip()]
                section = st.session_state.get(
                    f"np_section_{i}", np_item.get("section", "")
                )
                raw_new_points.append({
                    "section": section,
                    "title": st.session_state.get(
                        f"np_title_{i}", np_item.get("title", "")
                    ),
                    "subject_lines": lines,
                    "for_whom": st.session_state.get(f"np_forwho_{i}", ""),
                    "due": st.session_state.get(f"np_due_{i}", ""),
                    "meeting_date": meeting_date,
                })

        # Sort new points by their section's position in the report
        # then assign sequential numbers: MeetingNum.01, .02, .03...
        section_order = {name: idx for idx, name in enumerate(section_names)}
        raw_new_points.sort(
            key=lambda p: section_order.get(p["section"], 999)
        )
        for seq, np_data in enumerate(raw_new_points, start=1):
            np_data["number"] = f"{meeting_num:02d}.{seq:02d}"

        final_updates["new_points"] = raw_new_points

        # Collect info exchange from data editor
        final_ie = []
        for row in edited_ie:
            if any(str(v).strip() for v in row.values()):
                final_ie.append({
                    "from_whom": row.get("From", ""),
                    "status": row.get("Status", ""),
                    "content": row.get("Content", ""),
                    "due_date": row.get("Due Date", ""),
                })
        final_updates["info_exchange"] = final_ie if final_ie else None

        # Collect planning from data editor
        final_pl = []
        for row in edited_pl:
            if str(row.get("Content", "")).strip():
                final_pl.append({
                    "content": row.get("Content", ""),
                    "is_new": bool(row.get("Is New", False)),
                })
        final_updates["planning"] = final_pl if final_pl else None

        st.session_state.final_updates = final_updates
        st.session_state.step = 3
        st.rerun()


# ---------------------------------------------------------------------------
# Step 3: Generate & Download
# ---------------------------------------------------------------------------
elif st.session_state.step == 3:
    st.header("Step 3: Download Report")

    try:
        with st.spinner("Generating report..."):
            report_name = st.session_state.get("uploaded_report_name", "report.docx")
            base_name = Path(report_name).stem
            meeting_num = st.session_state.final_updates.get("meeting_number", "")

            # Increment the N-number and update the date in the filename
            out_stem = base_name
            if re.search(r'N\d+', out_stem):
                out_stem = re.sub(r'N\d+', f'N{meeting_num}', out_stem, count=1)
            else:
                out_stem = f"{out_stem}_N{meeting_num}"

            # Replace YYYYMMDD date with new meeting date
            meeting_date = st.session_state.final_updates.get("date", "")
            if meeting_date and re.match(r'\d{2}/\d{2}/\d{4}', meeting_date):
                dd, mm, yyyy = meeting_date.split("/")
                new_date_str = f"{yyyy}{mm}{dd}"
                out_stem = re.sub(r'\d{8}', new_date_str, out_stem, count=1)

            out_name = f"{out_stem}.docx"

            with tempfile.NamedTemporaryFile(
                suffix=".docx", delete=False
            ) as tmp_out:
                out_path = tmp_out.name

            generate_report(
                st.session_state.temp_report_path,
                out_path,
                st.session_state.final_updates,
            )

            with open(out_path, "rb") as f:
                st.session_state.report_bytes = f.read()
            st.session_state.report_filename = out_name

        st.success("Report generated successfully!")

        st.download_button(
            label=f"Download {out_name}",
            data=st.session_state.report_bytes,
            file_name=out_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True,
        )

        st.balloons()

        # Summary
        updates = st.session_state.final_updates
        st.markdown("### Summary")
        st.markdown(f"- **Meeting N{updates.get('meeting_number', '?')}** — {updates.get('date', '')}")
        pu_count = len(updates.get("point_updates", []))
        np_count = len(updates.get("new_points", []))
        st.markdown(f"- **{pu_count} point update(s)**, **{np_count} new point(s)**")
        ie_count = len(updates.get("info_exchange") or [])
        pl_count = len(updates.get("planning") or [])
        st.markdown(f"- **{ie_count} info exchange item(s)**, **{pl_count} planning item(s)**")

    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

    st.divider()
    if st.button("Start New Report", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
