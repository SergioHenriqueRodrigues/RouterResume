import streamlit as st

from generate import OLD_RESUMES_DIR

ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}


def render_tab_resumes(T: dict) -> None:
    """Render the Old Resumes tab."""

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
        ):
            saved_count = 0
            for f in uploaded:
                dest = OLD_RESUMES_DIR / f.name
                dest.write_bytes(f.read())
                saved_count += 1
            st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
            st.success(T["upload_success"].format(n=saved_count))
            st.rerun()

    # ── file list column ───────────────────────────────────────────────────────
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
                size     = f.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"

                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f'<div class="file-card">'
                        f'<div><div class="file-name">📄 {f.name}</div>'
                        f'<div class="file-size">{size_str}</div></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown('<div class="del-btn-wrap">', unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{f.name}", help=f"Remove {f.name}"):
                        f.unlink()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
