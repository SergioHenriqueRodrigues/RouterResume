import re
import streamlit as st
from pathlib import Path

from generate import OLD_RESUMES_DIR
from ui.components import render_file_card
from db.reference_resumes import (
    upload_reference_resume,
    get_reference_resume_bytes,
    delete_reference_resume,
)

ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}
MAX_UPLOAD_MB = 5
_MIME = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt":  "text/plain",
    ".md":   "text/markdown",
}


def _sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name or "file"


def _render_cloud_resumes(T: dict) -> None:
    resumes = st.session_state.get("ref_resumes", [])

    if not resumes:
        st.info(T["no_resumes"])
        return

    for r in resumes:
        rid      = r["id"]
        filename = r["filename"]
        size     = r.get("file_size") or 0
        size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
        ext      = Path(filename).suffix.lower()

        with st.container(border=True):
            col_info, col_dl, col_del = st.columns([5, 2, 1])
            with col_info:
                st.markdown(
                    f'<p style="margin:0;line-height:1.35">'
                    f'<span class="file-name">{filename}</span>'
                    f'<span class="file-size" style="margin-left:6px">· {size_str}</span>'
                    f'</p>',
                    unsafe_allow_html=True,
                )
            with col_dl:
                raw = get_reference_resume_bytes(rid)
                if raw:
                    st.download_button(
                        label=ext.upper().lstrip("."),
                        data=raw,
                        file_name=filename,
                        mime=_MIME.get(ext, "application/octet-stream"),
                        use_container_width=True,
                        key=f"dl_ref_{rid}",
                    )
            with col_del:
                if st.button("", key=f"del_ref_{rid}", icon=":material/delete:", help=T["history_delete_help"]):
                    delete_reference_resume(rid)
                    st.session_state["ref_resumes"] = [
                        x for x in st.session_state.get("ref_resumes", []) if x["id"] != rid
                    ]
                    st.rerun(scope="fragment")


@st.fragment
def render_tab_resumes(T: dict) -> None:
    user = st.session_state.get("user")
    OLD_RESUMES_DIR.mkdir(exist_ok=True)

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
        with st.spinner(T["uploading"]):
            saved_count = 0
            for f in uploaded:
                size_mb = f.size / (1024 * 1024)
                if size_mb > MAX_UPLOAD_MB:
                    st.warning(T["upload_too_large"].format(
                        name=f.name, size=size_mb, limit=MAX_UPLOAD_MB
                    ))
                    continue
                safe_name = _sanitize_filename(f.name)
                content = f.read()
                if user:
                    upload_reference_resume(user.id, safe_name, content)
                    st.session_state.pop("ref_resumes", None)
                else:
                    dest = OLD_RESUMES_DIR / safe_name
                    dest.write_bytes(content)
                saved_count += 1

        st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
        if saved_count:
            st.success(T["upload_success"].format(n=saved_count))
        st.rerun(scope="fragment")

    st.markdown("---")
    st.markdown(T["saved_files"])

    if user:
        # Reload ref_resumes if cleared
        if "ref_resumes" not in st.session_state:
            from db.reference_resumes import get_reference_resumes
            st.session_state["ref_resumes"] = get_reference_resumes(user.id)
        _render_cloud_resumes(T)
    else:
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
                    st.rerun(scope="fragment")
