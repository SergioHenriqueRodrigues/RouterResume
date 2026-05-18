import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from generate import OLD_RESUMES_DIR, OUTPUT_DIR
from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.tabs.tab_generate import render_tab_generate
from ui.tabs.tab_history import render_tab_history
from ui.tabs.tab_data import render_tab_data
from ui.tabs.tab_resumes import render_tab_resumes
from ui.i18n import UI_STRINGS
from ui.auth import render_auth
from supabase_client import restore_session
from streamlit_cookies_controller import CookieController
from db.profiles import get_profile_data
from db.reference_resumes import get_reference_resumes

# ── bootstrap dirs ─────────────────────────────────────────────────────────────
OLD_RESUMES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── session state defaults ─────────────────────────────────────────────────────
st.session_state.setdefault("ui_lang", "pt")
st.session_state.setdefault("ui_theme", "system")
st.session_state.setdefault("uploader_key", 0)

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RouterResume",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── styles ─────────────────────────────────────────────────────────────────────
inject_styles(st.session_state["ui_theme"])

# ── cookie manager ─────────────────────────────────────────────────────────────
# True only on the very first render — cookies haven't been read from the browser yet
_cookies_loading = "cookies" not in st.session_state
_cookie = CookieController()

# Clear cookies when logout is triggered
if st.session_state.pop("_clear_cookies", False):
    _cookie.remove("rr_at")
    _cookie.remove("rr_rt")

# Restore session from cookies after page refresh
if "user" not in st.session_state:
    _at = _cookie.get("rr_at")
    _rt = _cookie.get("rr_rt")
    if _at and _rt:
        result = restore_session(_at, _rt)
        if result:
            _user, _at_new, _rt_new = result
            st.session_state["user"] = _user
            st.session_state["access_token"] = _at_new
            st.session_state["refresh_token"] = _rt_new
        else:
            _cookie.remove("rr_at")
            _cookie.remove("rr_rt")

# Save tokens to cookies after fresh login (rerun so main app only renders after cookies are saved)
if (st.session_state.get("user")
        and st.session_state.get("access_token")
        and not _cookie.get("rr_at")):
    _cookie.set("rr_at", st.session_state["access_token"], max_age=2592000)
    _cookie.set("rr_rt", st.session_state["refresh_token"], max_age=2592000)
    st.rerun()

# ── load cloud data after login (once per session) ────────────────────────────
if st.session_state.get("user") and "profile_data" not in st.session_state:
    uid = st.session_state["user"].id
    st.session_state["profile_data"] = get_profile_data(uid)
    st.session_state["ref_resumes"] = get_reference_resumes(uid)

# ── auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    if _cookies_loading:
        # First render: wait for cookie component to report back before showing auth
        st.stop()
    lang = st.session_state.get("ui_lang", "pt")
    T = UI_STRINGS[lang]
    render_auth(T)
    st.stop()

# ── sidebar ────────────────────────────────────────────────────────────────────
lang, fmt, model, api_key, T = render_sidebar()

# ── main tabs ──────────────────────────────────────────────────────────────────
tab_gen, tab_history, tab_data, tab_resumes = st.tabs([
    T["tab_generate"], T["tab_history"], T["tab_data"], T["tab_resumes"],
])

with tab_gen:
    render_tab_generate(lang, fmt, model, api_key, T)

with tab_history:
    render_tab_history(T)

with tab_data:
    render_tab_data(T)

with tab_resumes:
    render_tab_resumes(T)
