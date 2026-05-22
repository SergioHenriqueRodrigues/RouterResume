import base64
import re
from datetime import datetime

import streamlit as st

from generate import OUTPUT_DIR
from ui.components import render_file_card
from ui.auth import _queue_toast, _flush_toast
from db.generations import get_generations, get_generation_files, delete_generation

_ALLOWED = {".pdf", ".docx"}
_MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


def _parse_stem(stem: str) -> tuple[str, str]:
    m = re.search(r"(\d{8})_(\d{4})", stem)
    if m:
        raw_name = stem[: m.start()].rstrip("_").replace("_", " ").title() or stem
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
            return raw_name, dt.strftime("%d/%m/%Y  %H:%M")
        except ValueError:
            pass
    return stem, ""


@st.fragment
def _render_cloud_history(T: dict) -> None:
    _flush_toast()
    user = st.session_state["user"]

    try:
        rows = get_generations(user.id)
    except Exception:
        _queue_toast(T["error_load"], "error")
        _flush_toast()
        return

    if not rows:
        st.info(T["history_empty"])
        return

    for row in rows:
        gen_id   = row["id"]
        filename = row.get("filename") or "resume"
        model    = row.get("model") or ""
        created  = row.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = dt.strftime("%d/%m/%Y  %H:%M")
        except Exception:
            date_str = created[:16] if created else ""

        display_name, _ = _parse_stem(filename)
        subtitle = f"{date_str} · {model}" if model else date_str

        with st.container(border=True):
            col_info, col_dl, col_del = st.columns([5, 2, 1])

            with col_info:
                st.markdown(
                    f'<p style="margin:0;line-height:1.35">'
                    f'<span class="file-name">{display_name}</span>'
                    f'<span class="file-size" style="margin-left:6px">· {subtitle}</span>'
                    f'</p>',
                    unsafe_allow_html=True,
                )

            with col_dl:
                try:
                    files_data = get_generation_files(gen_id)
                except Exception:
                    files_data = {}

                btns = []
                if files_data.get("file_docx"):
                    btns.append(("DOCX", base64.b64decode(files_data["file_docx"]), "docx"))
                if files_data.get("file_pdf"):
                    btns.append(("PDF", base64.b64decode(files_data["file_pdf"]), "pdf"))

                if btns:
                    dl_cols = st.columns(len(btns))
                    for bc, (label, data, ext) in zip(dl_cols, btns):
                        with bc:
                            st.download_button(
                                label=label,
                                data=data,
                                file_name=f"{filename}.{ext}",
                                mime=_MIME[ext],
                                use_container_width=True,
                                key=f"dl_{gen_id}_{ext}",
                            )

            with col_del:
                if st.button("", key=f"del_{gen_id}", icon=":material/delete:", help=T["history_delete_help"]):
                    try:
                        delete_generation(gen_id)
                    except Exception:
                        _queue_toast(T["error_delete"], "error")
                    st.rerun(scope="fragment")


def _render_local_history(T: dict) -> None:
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
                try:
                    if f.exists():
                        f.unlink()
                except Exception:
                    _queue_toast(T["error_delete"], "error")
            st.rerun()


def render_tab_history(T: dict) -> None:
    st.markdown(f"### {T['history_title']}")
    if st.session_state.get("user"):
        _render_cloud_history(T)
    else:
        _render_local_history(T)
