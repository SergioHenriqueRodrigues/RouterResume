import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))

from generate import OLD_RESUMES_DIR, OUTPUT_DIR
from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.tabs.tab_generate import render_tab_generate
from ui.tabs.tab_history import render_tab_history
from ui.tabs.tab_data import render_tab_data
from ui.tabs.tab_resumes import render_tab_resumes
from ui.i18n import UI_STRINGS
from ui.auth import render_auth, render_new_password, _flush_toast
from supabase_client import restore_session
from streamlit_cookies_controller import CookieController
from db.profiles import get_profile
from db.reference_resumes import get_reference_resumes

_HASH_TO_QUERY_JS = """
<script>
(function() {
  var pd = window.parent;
  var hash = pd.location.hash;
  if (hash && hash.length > 1) {
    var params = new URLSearchParams(hash.substring(1));
    var at   = params.get('access_token');
    var type = params.get('type');
    if (at && (type === 'bearer' || type === 'recovery')) {
      var rt = params.get('refresh_token') || '';
      pd.history.replaceState({}, '',
        '?access_token=' + encodeURIComponent(at) +
        '&refresh_token=' + encodeURIComponent(rt) +
        '&type=' + encodeURIComponent(type)
      );
      pd.location.reload();
    }
  }
})();
</script>
"""

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
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── styles ─────────────────────────────────────────────────────────────────────
inject_styles(st.session_state["ui_theme"])

# ── hash → query params (OAuth / password recovery callbacks) ──────────────────
components.html(_HASH_TO_QUERY_JS, height=0)

# Password recovery: show new-password form before cookie logic
_qp = st.query_params
if _qp.get("type") == "recovery" and _qp.get("access_token"):
    _T = UI_STRINGS[st.session_state.get("ui_lang", "pt")]
    render_new_password(_T, _qp.get("access_token"), _qp.get("refresh_token", ""))
    st.stop()

# ── cookie manager ─────────────────────────────────────────────────────────────
_cookie = CookieController()
# None = component hasn't reported back yet; {} = reported but no cookies
_cookies_loading = st.session_state.get("cookies") is None

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
            # Refresh cookies whenever tokens are renewed by Supabase
            if _at_new != _at:
                _cookie.set("rr_at", _at_new, max_age=2592000)
                _cookie.set("rr_rt", _rt_new, max_age=2592000)
        else:
            _cookie.remove("rr_at")
            _cookie.remove("rr_rt")

# Save tokens to cookies after fresh login (only once per session)
if (st.session_state.get("user")
        and st.session_state.get("access_token")
        and not st.session_state.get("_cookies_saved")):
    _cookie.set("rr_at", st.session_state["access_token"], max_age=2592000)
    _cookie.set("rr_rt", st.session_state["refresh_token"], max_age=2592000)
    st.session_state["_cookies_saved"] = True

# ── load cloud data after login (once per session) ────────────────────────────
if st.session_state.get("user") and "profile_data" not in st.session_state:
    uid     = st.session_state["user"].id
    profile = get_profile(uid)
    st.session_state["profile_data"] = profile.get("data_md", "")
    st.session_state["ref_resumes"]  = get_reference_resumes(uid)
    if profile.get("openrouter_key"):
        st.session_state["api_key"] = profile["openrouter_key"]
    if profile.get("ai_model"):
        st.session_state["model"] = profile["ai_model"]
    if profile.get("ui_lang"):
        st.session_state["ui_lang"] = profile["ui_lang"]
    if profile.get("ui_theme"):
        st.session_state["ui_theme"] = profile["ui_theme"]

# ── auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    if _cookies_loading:
        # First render: wait for cookie component to report back before showing auth
        st.stop()
    lang = st.session_state.get("ui_lang", "pt")
    T = UI_STRINGS[lang]
    render_auth(T)
    st.stop()

# ── reload ref_resumes before sidebar so the count is always current ──────────
if st.session_state.get("user") and "ref_resumes" not in st.session_state:
    st.session_state["ref_resumes"] = get_reference_resumes(st.session_state["user"].id)

# ── sidebar ────────────────────────────────────────────────────────────────────
_flush_toast()
lang, fmt, model, api_key, T = render_sidebar()

# ── tab navigation (restores active tab after full reruns from within tabs) ────
_nav_tab = st.session_state.pop("_nav_tab", None)
if _nav_tab is not None:
    components.html(
        f"<script>(function(){{"
        f"var idx={_nav_tab},tries=0;"
        f"function click(){{"
        f"var t=window.parent.document.querySelectorAll('[data-baseweb=\"tab\"]');"
        f"if(t[idx]){{t[idx].click();return;}}"
        f"if(++tries<40)requestAnimationFrame(click);}}"
        f"requestAnimationFrame(click);"
        f"}})();</script>",
        height=0,
    )

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
