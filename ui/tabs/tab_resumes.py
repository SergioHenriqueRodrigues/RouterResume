import streamlit as st
from pathlib import Path

from generate import OLD_RESUMES_DIR, sanitize_filename
from ui.components import render_file_card
from ui.auth import _queue_toast, _flush_toast
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


def _render_cloud_resumes(T: dict) -> None:
    resumes = st.session_state.get("ref_resumes", [])
    deleting_id = st.session_state.pop("_deleting_ref_id", None)

    if not resumes:
        st.info(T["no_resumes"])
        return

    for r in resumes:
        rid      = r["id"]
        filename = r["filename"]
        size     = r.get("file_size") or 0
        size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
        ext      = Path(filename).suffix.lower()
        busy     = (rid == deleting_id)

        with st.container(border=True):
            col_info, col_dl, col_del = st.columns([5, 2, 1])
            with col_info:
                st.markdown(
                    f'<p style="margin:0;line-height:1.35;{"opacity:.4" if busy else ""}">'
                    f'<span class="file-name">{filename}</span>'
                    f'<span class="file-size" style="margin-left:6px">· {size_str}</span>'
                    f'</p>',
                    unsafe_allow_html=True,
                )
            with col_dl:
                if not busy:
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
                else:
                    st.download_button(
                        label="...",
                        data=b"",
                        file_name=filename,
                        use_container_width=True,
                        disabled=True,
                        key=f"dl_ref_{rid}",
                    )
            with col_del:
                if st.button(
                    "",
                    key=f"del_ref_{rid}",
                    icon=":material/delete:",
                    help=T["history_delete_help"],
                    disabled=busy,
                ):
                    st.session_state["_deleting_ref_id"] = rid
                    st.rerun(scope="fragment")

    if deleting_id:
        try:
            delete_reference_resume(deleting_id)
            st.session_state["ref_resumes"] = [
                x for x in resumes if x["id"] != deleting_id
            ]
        except Exception:
            _queue_toast(T["error_delete"], "error")
        st.rerun(scope="fragment")


@st.fragment
def render_tab_resumes(T: dict) -> None:
    _flush_toast()
    uploading = st.session_state.pop("_uploading", False)
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
        T["uploading"] if uploading else T["upload_btn"],
        type="primary",
        use_container_width=True,
        disabled=uploading or not has_files,
        icon=":material/hourglass_empty:" if uploading else ":material/upload:",
    ):
        st.session_state["_uploading"] = True
        st.rerun(scope="fragment")

    st.markdown("---")
    st.markdown(T["saved_files"])

    if user:
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
                    try:
                        f.unlink()
                    except Exception:
                        _queue_toast(T["error_delete"], "error")
                    st.session_state["_nav_tab"] = 3
                    st.rerun()

    if uploading:
        saved_count = 0
        for f in uploaded:
            size_mb = f.size / (1024 * 1024)
            if size_mb > MAX_UPLOAD_MB:
                _queue_toast(T["upload_too_large"].format(
                    name=f.name, size=size_mb, limit=MAX_UPLOAD_MB
                ), "warning")
                continue
            safe_name = sanitize_filename(f.name)
            content = f.read()
            try:
                if user:
                    upload_reference_resume(user.id, safe_name, content)
                    st.session_state.pop("ref_resumes", None)
                else:
                    dest = OLD_RESUMES_DIR / safe_name
                    dest.write_bytes(content)
                saved_count += 1
            except Exception:
                _queue_toast(T["error_upload"], "error")

        st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
        if saved_count:
            _queue_toast(T["upload_success"].format(n=saved_count), "success")
        st.session_state["_nav_tab"] = 3
        st.rerun()
