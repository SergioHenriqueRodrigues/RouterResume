import os

import streamlit as st
import streamlit.components.v1 as components

from supabase_client import get_supabase
from db.profiles import get_profile
from db.reference_resumes import get_reference_resumes

_USER_KEYS = [
    "user", "access_token", "refresh_token",
    "profile_data", "ref_resumes",
    "api_key", "model",
    "saved_paths", "resume_text",
    "generation_error", "sidebar_test_result",
    "is_generating", "pending_job", "pending_key",
    "login_loading", "login_email", "login_password",
    "_toast", "_cookies_saved",
]

# ── SVG icons ──────────────────────────────────────────────────────────────────
_ICONS = {
    "success": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M20 6L9 17l-5-5"/></svg>'
    ),
    "error": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
    ),
    "warning": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    ),
}

_TOAST_SCRIPT = """
<script>
(function(){{
  var pd = window.parent.document;
  var css = window.parent.getComputedStyle(pd.documentElement);
  function hex2lum(h) {{
    h = h.replace('#','');
    if (h.length < 6) return 255;
    return 0.299*parseInt(h.substr(0,2),16) + 0.587*parseInt(h.substr(2,2),16) + 0.114*parseInt(h.substr(4,2),16);
  }}
  var bg = css.getPropertyValue('--bg').trim();
  var isDark = hex2lum(bg) < 128;

  var STYLES = {{
    success: {{
      bg:     css.getPropertyValue('--status-ok-bg').trim()     || (isDark ? 'rgba(34,197,94,.12)'  : '#EDFBF3'),
      border: css.getPropertyValue('--status-ok-border').trim() || (isDark ? '#2A6B40'              : '#A8DFBB'),
      text:   css.getPropertyValue('--status-ok-text').trim()   || (isDark ? '#6FDFAA'              : '#1E6B3E'),
    }},
    warning: {{
      bg:     css.getPropertyValue('--status-warn-bg').trim()     || (isDark ? 'rgba(245,158,11,.12)' : '#FFF8EC'),
      border: css.getPropertyValue('--status-warn-border').trim() || (isDark ? '#8A6400'              : '#F5C97A'),
      text:   css.getPropertyValue('--status-warn-text').trim()   || (isDark ? '#F5C97A'              : '#7A4E00'),
    }},
    error: {{
      bg:     isDark ? 'rgba(239,68,68,.13)' : 'rgba(239,68,68,.07)',
      border: '#ef4444',
      text:   isDark ? '#fca5a5' : '#b91c1c',
    }},
  }};

  var type = '{toast_type}';
  var s = STYLES[type] || STYLES.error;
  var icon = '{icon_svg}';
  var msg  = '{msg_safe}';

  var wrap = pd.getElementById('rr-toasts');
  if (!wrap) {{
    wrap = pd.createElement('div');
    wrap.id = 'rr-toasts';
    wrap.style.cssText = 'position:fixed;top:16px;right:16px;z-index:99999;display:flex;flex-direction:column-reverse;gap:8px;pointer-events:none;';
    pd.body.appendChild(wrap);
  }}

  var t = pd.createElement('div');
  t.style.cssText = [
    'background:'  + s.bg     + ';',
    'border-left:4px solid ' + s.border + ';',
    'color:'       + s.text   + ';',
    'padding:12px 14px;',
    'border-radius:8px;',
    'box-shadow:0 4px 20px rgba(0,0,0,.10);',
    'font-size:13.5px;font-family:inherit;',
    'line-height:1.5;',
    'min-width:220px;max-width:340px;',
    'display:flex;align-items:center;gap:10px;',
    'opacity:0;transform:translateX(12px);',
    'transition:opacity .2s,transform .2s;',
    'pointer-events:auto;cursor:pointer;',
  ].join('');
  t.innerHTML = icon + '<span>' + msg + '</span>';
  wrap.appendChild(t);

  requestAnimationFrame(function(){{ requestAnimationFrame(function(){{
    t.style.opacity='1'; t.style.transform='translateX(0)';
  }}); }});

  function dismiss() {{
    t.style.opacity='0'; t.style.transform='translateX(12px)';
    setTimeout(function(){{ t.remove(); }}, 220);
  }}
  setTimeout(dismiss, 4200);
  t.addEventListener('click', dismiss);
}})();
</script>
"""

_FORM_JS = """
<script>
(function() {
  var pd = window.parent.document;
  if (!pd.getElementById('rr-auth-styles')) {
    var s = pd.createElement('style');
    s.id = 'rr-auth-styles';
    s.textContent = '[data-testid="InputInstructions"] { display: none !important; }';
    pd.head.appendChild(s);
  }
  function setup() {
    pd.querySelectorAll('[data-testid="stForm"]').forEach(function(form) {
      var inputs = Array.from(form.querySelectorAll('input'));
      inputs.forEach(function(input, idx) {
        if (input._rrSetup) return;
        input._rrSetup = true;
        input.addEventListener('keydown', function(e) {
          if (e.key !== 'Enter') return;
          e.preventDefault();
          e.stopImmediatePropagation();
          var next = inputs[idx + 1];
          if (next) {
            next.focus();
          } else {
            var btn = form.querySelector('[data-testid="baseButton-primaryFormSubmit"]');
            if (!btn) {
              var allBtns = Array.from(form.querySelectorAll('button'));
              btn = allBtns[allBtns.length - 1];
            }
            if (btn) btn.click();
          }
        }, true);
      });
    });
  }
  setTimeout(setup, 600);
  new MutationObserver(function() { setTimeout(setup, 200); })
    .observe(pd.documentElement, { childList: true, subtree: true });
})();
</script>
"""



def render_new_password(T: dict, access_token: str, refresh_token: str) -> None:
    components.html(_FORM_JS, height=0)
    _flush_toast()
    st.markdown(
        '<p style="font-size:42px;font-weight:800;letter-spacing:-1.5px;'
        'text-align:center;margin:60px 0 4px 0">RouterResume</p>',
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"### {T['auth_new_password_title']}")
        with st.form("new_password_form"):
            new_pwd     = st.text_input(T["auth_new_password"], type="password")
            confirm_pwd = st.text_input(T["auth_confirm_password"], type="password")
            submitted   = st.form_submit_button(
                T["auth_save_password_btn"], use_container_width=True, type="primary"
            )
        if submitted:
            if not new_pwd:
                _queue_toast(T["auth_fill_all"], "warning")
                st.rerun()
            elif len(new_pwd) < 6:
                _queue_toast(T["auth_pwd_short"], "warning")
                st.rerun()
            elif new_pwd != confirm_pwd:
                _queue_toast(T["auth_passwords_mismatch"], "warning")
                st.rerun()
            else:
                try:
                    sb = get_supabase()
                    sb.auth.set_session(access_token, refresh_token)
                    sb.auth.update_user({"password": new_pwd})
                    sb.auth.sign_out()
                    _queue_toast(T["auth_password_updated"], "success")
                    st.query_params.clear()
                    st.rerun()
                except Exception:
                    _queue_toast(T["auth_password_update_error"], "error")
                    st.rerun()


def clear_user_session() -> None:
    for k in _USER_KEYS:
        st.session_state.pop(k, None)


def _load_user_data(user_id: str) -> None:
    clear_user_session()
    profile = get_profile(user_id)
    st.session_state["profile_data"]  = profile.get("data_md", "")
    st.session_state["ref_resumes"]   = get_reference_resumes(user_id)
    if profile.get("openrouter_key"):
        st.session_state["api_key"] = profile["openrouter_key"]
    if profile.get("ai_model"):
        st.session_state["model"] = profile["ai_model"]
    if profile.get("ui_lang"):
        st.session_state["ui_lang"] = profile["ui_lang"]
    if profile.get("ui_theme"):
        st.session_state["ui_theme"] = profile["ui_theme"]


def _queue_toast(msg: str, toast_type: str) -> None:
    st.session_state["_toast"] = (msg, toast_type)


def _flush_toast() -> None:
    t = st.session_state.pop("_toast", None)
    if not t:
        return
    msg, toast_type = t
    icon_svg = _ICONS.get(toast_type, _ICONS["error"]).replace("'", "\\'")
    msg_safe = msg.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    script = _TOAST_SCRIPT.format(
        toast_type=toast_type,
        icon_svg=icon_svg,
        msg_safe=msg_safe,
    )
    components.html(script, height=0)


def _parse_login_error(e: Exception, T: dict) -> str:
    msg = str(e).lower()
    if "invalid login credentials" in msg or "invalid_credentials" in msg:
        return T.get("auth_wrong_credentials", T["auth_login_error"])
    if "email not confirmed" in msg or "email_not_confirmed" in msg:
        return T.get("auth_email_not_confirmed", T["auth_login_error"])
    if "too many requests" in msg or "rate limit" in msg:
        return T.get("auth_rate_limit", T["auth_login_error"])
    return T["auth_login_error"]


def render_auth(T: dict) -> None:
    components.html(_FORM_JS, height=0)
    _flush_toast()

    st.markdown(
        '<p style="font-size:42px;font-weight:800;letter-spacing:-1.5px;'
        'text-align:center;margin:60px 0 4px 0">RouterResume</p>',
        unsafe_allow_html=True,
    )

    # ── execute login before rendering the form ────────────────────────────────
    if st.session_state.get("login_loading"):
        _email = st.session_state.pop("login_email", "")
        _pwd   = st.session_state.pop("login_password", "")
        st.session_state["login_loading"] = False
        try:
            res = get_supabase().auth.sign_in_with_password(
                {"email": _email, "password": _pwd}
            )
            _load_user_data(res.user.id)
            st.session_state["user"]          = res.user
            st.session_state["access_token"]  = res.session.access_token
            st.session_state["refresh_token"] = res.session.refresh_token
            st.rerun()
        except Exception as e:
            msg = _parse_login_error(e, T)
            detail = str(e)
            if detail and detail.lower() not in msg.lower():
                msg = f"{msg} ({detail[:120]})"
            _queue_toast(msg, "error")
            st.rerun()
        return

    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab_login, tab_signup = st.tabs([T["auth_login"], T["auth_signup"]])

        with tab_login:
            show_reset = st.session_state.get("show_reset_form", False)

            if show_reset:
                st.markdown(f"**{T['auth_reset_title']}**")
                with st.form("reset_form"):
                    email_r   = st.text_input(T["auth_email"])
                    submitted_r = st.form_submit_button(
                        T["auth_reset_btn"], use_container_width=True, type="primary"
                    )
                if submitted_r:
                    if not email_r:
                        _queue_toast(T["auth_fill_email"], "warning")
                        st.rerun()
                    else:
                        try:
                            site_url = os.getenv("SITE_URL", "http://localhost:8501")
                            get_supabase().auth.reset_password_for_email(
                                email_r, {"redirect_to": site_url}
                            )
                            _queue_toast(T["auth_reset_sent"], "success")
                            st.session_state["show_reset_form"] = False
                        except Exception:
                            _queue_toast(T["auth_reset_error"], "error")
                        st.rerun()
                if st.button(T["auth_back"], use_container_width=True):
                    st.session_state["show_reset_form"] = False
                    st.rerun()
            else:
                with st.form("login_form"):
                    email = st.text_input(T["auth_email"])
                    password = st.text_input(T["auth_password"], type="password")
                    submitted = st.form_submit_button(
                        T["auth_login_btn"],
                        use_container_width=True,
                        type="primary",
                    )

                if submitted:
                    if not email or not password:
                        _queue_toast(T["auth_fill_all"], "warning")
                        st.rerun()
                    else:
                        st.session_state["login_email"]    = email
                        st.session_state["login_password"] = password
                        st.session_state["login_loading"]  = True
                        st.rerun()

                if st.button(
                    T["auth_forgot_password"],
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state["show_reset_form"] = True
                    st.rerun()

        with tab_signup:
            with st.form("signup_form"):
                email_s = st.text_input(T["auth_email"], key="signup_email")
                pwd_s = st.text_input(T["auth_password"], type="password", key="signup_pwd")
                submitted_s = st.form_submit_button(
                    T["auth_signup_btn"], use_container_width=True, type="primary"
                )

            if submitted_s:
                if not email_s or not pwd_s:
                    _queue_toast(T["auth_fill_all"], "warning")
                elif len(pwd_s) < 6:
                    _queue_toast(T["auth_pwd_short"], "warning")
                else:
                    try:
                        res = get_supabase().auth.sign_up(
                            {"email": email_s, "password": pwd_s}
                        )
                        if res.user:
                            _queue_toast(T["auth_signup_success"], "success")
                        else:
                            _queue_toast(T["auth_signup_error"], "error")
                    except Exception:
                        _queue_toast(T["auth_signup_error"], "error")
                st.rerun()

