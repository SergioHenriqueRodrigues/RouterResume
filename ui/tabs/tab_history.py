import re
from datetime import datetime

import streamlit as st

from generate import OUTPUT_DIR
from ui.components import render_file_card

_ALLOWED = {".pdf", ".docx"}


def _parse_stem(stem: str) -> tuple[str, str]:
    """Return (display_name, date_str) from a filename stem."""
    m = re.search(r"(\d{8})_(\d{4})", stem)
    if m:
        raw_name = stem[: m.start()].rstrip("_").replace("_", " ").title() or stem
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
            return raw_name, dt.strftime("%d/%m/%Y  %H:%M")
        except ValueError:
            pass
    return stem, ""


def render_tab_history(T: dict) -> None:
    st.markdown(f"### {T['history_title']}")

    if not OUTPUT_DIR.exists():
        st.info(T["history_empty"])
        return

    files = [
        f for f in OUTPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in _ALLOWED
    ]

    if not files:
        st.info(T["history_empty"])
        return

    # group by stem, sorted newest first by mtime
    groups: dict[str, list] = {}
    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
        groups.setdefault(f.stem, []).append(f)

    for stem, group_files in groups.items():
        name, date_str = _parse_stem(stem)

        if render_file_card(
            display_name=name,
            subtitle=date_str,
            download_files=group_files,
            delete_key=f"del_{stem}",
            delete_help=T["history_delete_help"],
        ):
            for f in group_files:
                if f.exists():
                    f.unlink()
            st.rerun()
