import re
import streamlit as st
from pathlib import Path

from generate import OLD_RESUMES_DIR
from ui.components import render_file_card

ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}
MAX_UPLOAD_MB = 5


def _sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name or "file"


def render_tab_resumes(T: dict) -> None:
    OLD_RESUMES_DIR.mkdir(exist_ok=True)

    col_up, col_list = st.columns([1, 1], gap="large")

    # ── upload column ──────────────────────────────────────────────────────────
    with col_up:
        st.markdown(T["upload_title"])
        uploaded = st.file_uploader(
            T["upload_label"],
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"uploader_{st.session_state.get('uploader_key', 0)}",
        )

        has_files = bool(uploaded)
        if has_files:
            st.info(f"{len(uploaded)} {T['upload_select']}")

        if st.button(
            T["upload_btn"],
            type="primary",
            use_container_width=True,
            disabled=not has_files,
            icon=":material/upload:",
        ):
            saved_count = 0
            for f in uploaded:
                size_mb = f.size / (1024 * 1024)
                if size_mb > MAX_UPLOAD_MB:
                    st.warning(T["upload_too_large"].format(
                        name=f.name, size=size_mb, limit=MAX_UPLOAD_MB
                    ))
                    continue
                safe_name = _sanitize_filename(f.name)
                dest = OLD_RESUMES_DIR / safe_name
                dest.write_bytes(f.read())
                saved_count += 1
            st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
            if saved_count:
                st.success(T["upload_success"].format(n=saved_count))
            st.rerun()

    # ── saved files column ─────────────────────────────────────────────────────
    with col_list:
        st.markdown(T["saved_files"])

        files = []
        if OLD_RESUMES_DIR.exists():
            files = [
                f for f in sorted(OLD_RESUMES_DIR.iterdir())
                if f.is_file() and f.suffix.lower() in ALLOWED_EXTS
            ]

        if not files:
            st.info(T["no_resumes"])
        else:
            for f in files:
                size = f.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"

                if render_file_card(
                    display_name=f.name,
                    subtitle=size_str,
                    download_files=[f],
                    delete_key=f"del_{f.name}",
                    delete_help=T["history_delete_help"],
                ):
                    f.unlink()
                    st.rerun()
