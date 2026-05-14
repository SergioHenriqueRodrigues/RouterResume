import streamlit as st

_MIME = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt":  "text/plain",
    ".md":   "text/markdown",
}


def render_file_card(
    display_name: str,
    subtitle: str,
    download_files: list,
    delete_key: str,
    delete_help: str = "",
) -> bool:
    """Slim card: info left | downloads center | delete right (fixed position).

    Returns True if the delete button was clicked.
    """
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
            if download_files:
                dl_cols = st.columns(len(download_files))
                for bc, f in zip(dl_cols, download_files):
                    with bc:
                        st.download_button(
                            label=f.suffix.upper().lstrip("."),
                            data=f.read_bytes(),
                            file_name=f.name,
                            mime=_MIME.get(f.suffix.lower(), "application/octet-stream"),
                            use_container_width=True,
                            key=f"dl_{f.name}",
                        )

        with col_del:
            clicked = st.button(
                "", key=delete_key, icon=":material/delete:", help=delete_help
            )

    return clicked
