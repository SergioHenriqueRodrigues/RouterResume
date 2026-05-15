from datetime import datetime

import streamlit as st

from generate import DATA_MD


def render_tab_data(T: dict) -> None:
    current = DATA_MD.read_text(encoding="utf-8") if DATA_MD.exists() else ""

    st.markdown(T["profile_title"])

    new_content = st.text_area(
        label="data_md",
        value=current,
        height=500,
        label_visibility="collapsed",
        placeholder=T["profile_placeholder"],
    )

    # Live char count + last saved time
    chars     = len(new_content)
    chars_str = T["profile_chars"].format(chars=chars)
    if DATA_MD.exists():
        mtime    = datetime.fromtimestamp(DATA_MD.stat().st_mtime)
        date_str = mtime.strftime("%d/%m %H:%M")
        caption  = f"{chars_str} · {T['profile_saved_at'].format(date=date_str)}"
    else:
        caption = chars_str

    col_meta, col_btn = st.columns([3, 1])
    with col_meta:
        st.caption(caption)
    with col_btn:
        if st.button(T["save_btn"], type="primary", icon=":material/save:", use_container_width=True):
            DATA_MD.write_text(new_content, encoding="utf-8")
            st.success(T["save_success"])
            st.rerun()
