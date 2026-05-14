import re
from datetime import datetime

import streamlit as st

from generate import OUTPUT_DIR

_ALLOWED = {".pdf", ".docx"}
_MIME = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


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
        col_date, col_dl, col_del = st.columns([4, 3, 1])

        with col_date:
            name, date_str = _parse_stem(stem)
            st.markdown(
                f"**{name}**<br>"
                f'<span style="font-size:0.85em;opacity:0.65;">{date_str}</span>',
                unsafe_allow_html=True,
            )

        with col_dl:
            dl_cols = st.columns(len(group_files))
            for bc, f in zip(dl_cols, group_files):
                with bc:
                    st.download_button(
                        label=f.suffix.upper().lstrip("."),
                        data=f.read_bytes(),
                        file_name=f.name,
                        mime=_MIME.get(f.suffix.lower(), "application/octet-stream"),
                        icon=":material/download:",
                        use_container_width=True,
                        key=f"hist_dl_{f.name}",
                    )

        with col_del:
            if st.button(
                "",
                key=f"hist_del_{stem}",
                icon=":material/delete:",
                help=T["history_delete_help"],
            ):
                for f in group_files:
                    if f.exists():
                        f.unlink()
                st.rerun()

        st.divider()
