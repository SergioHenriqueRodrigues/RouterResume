from datetime import datetime

import streamlit as st

from generate import DATA_MD
from db.profiles import save_profile_data
from ui.auth import _queue_toast


def render_tab_data(T: dict) -> None:
    user = st.session_state.get("user")

    if user:
        current = st.session_state.get("profile_data", "")
    else:
        current = DATA_MD.read_text(encoding="utf-8") if DATA_MD.exists() else ""

    st.markdown(T["profile_title"])

    new_content = st.text_area(
        label="data_md",
        value=current,
        height=500,
        label_visibility="collapsed",
        placeholder=T["profile_placeholder"],
    )

    chars     = len(new_content)
    chars_str = T["profile_chars"].format(chars=chars)
    if user:
        caption = chars_str
    elif DATA_MD.exists():
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
            saved = False
            with st.spinner(T["saving"]):
                try:
                    if user:
                        save_profile_data(user.id, new_content)
                        st.session_state["profile_data"] = new_content
                    else:
                        DATA_MD.write_text(new_content, encoding="utf-8")
                    saved = True
                except Exception:
                    _queue_toast(T["error_save"], "error")
            if saved:
                st.success(T["save_success"])
            st.session_state["_nav_tab"] = 2
            st.rerun()
