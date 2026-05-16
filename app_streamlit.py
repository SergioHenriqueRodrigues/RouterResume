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

# ── restore session if tokens exist ───────────────────────────────────────────
if "access_token" in st.session_state and "user" not in st.session_state:
    ok = restore_session(
        st.session_state["access_token"],
        st.session_state.get("refresh_token", ""),
    )
    if not ok:
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)

# ── load cloud data after login (once per session) ────────────────────────────
if st.session_state.get("user") and "profile_data" not in st.session_state:
    uid = st.session_state["user"].id
    st.session_state["profile_data"] = get_profile_data(uid)
    st.session_state["ref_resumes"] = get_reference_resumes(uid)

# ── auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
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
