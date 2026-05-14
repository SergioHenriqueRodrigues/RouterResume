import streamlit as st

from generate import DATA_MD


def render_tab_data(T: dict) -> None:
    """Render the Profile Data tab."""

    st.markdown(T["profile_title"])
    st.caption(T["profile_caption"])

    current = DATA_MD.read_text(encoding="utf-8") if DATA_MD.exists() else ""

    new_content = st.text_area(
        label="data_md",
        value=current,
        height=500,
        label_visibility="collapsed",
        placeholder=T["profile_placeholder"],
    )

    if st.button(T["save_btn"], type="primary"):
        DATA_MD.write_text(new_content, encoding="utf-8")
        st.success(T["save_success"])
        st.rerun()
