import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from generate import OLD_RESUMES_DIR, OUTPUT_DIR
from ui.i18n import UI_STRINGS
from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.tabs.tab_generate import render_tab_generate
from ui.tabs.tab_resumes import render_tab_resumes
from ui.tabs.tab_data import render_tab_data

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

# ── sidebar ────────────────────────────────────────────────────────────────────
lang, fmt, model, api_key, T = render_sidebar()

# ── main tabs ──────────────────────────────────────────────────────────────────
tab_gen, tab_resumes, tab_data = st.tabs([T["tab_generate"], T["tab_resumes"], T["tab_data"]])

with tab_gen:
    render_tab_generate(lang, fmt, model, api_key, T)

with tab_resumes:
    render_tab_resumes(T)

with tab_data:
    render_tab_data(T)
