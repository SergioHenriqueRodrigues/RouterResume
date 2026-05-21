import json
import time
import urllib.request
import urllib.error

import streamlit as st
import streamlit.components.v1 as components

from ui.i18n import UI_STRINGS
from ui.tabs.tab_how_to import _CONTENT as _HOW_TO_CONTENT
from generate import LANGUAGES, read_data_md, read_old_resumes, validate_api_key


def _render_profile_content(lang: str) -> None:
    T        = UI_STRINGS[lang]
    tab_prof, tab_how = st.tabs([T["profile_tab"], T["how_to_expander"]])

    with tab_prof:
        ui_lang_options = {"pt": "🇧🇷 Português", "en": "🇺🇸 English", "es": "🇪🇸 Español"}
        selected_lang = st.selectbox(
            T["language_label"],
            options=list(ui_lang_options.keys()),
            format_func=lambda k: ui_lang_options[k],
            index=list(ui_lang_options.keys()).index(lang),
            key="modal_lang_select",
        )

        theme_opts_keys   = ["light", "dark", "system"]
        theme_opts_labels = {k: T[f"theme_{k}"] for k in theme_opts_keys}
        current_theme     = st.session_state.get("ui_theme", "system")
        selected_theme = st.selectbox(
            T["theme_label"],
            options=theme_opts_keys,
            format_func=lambda k: theme_opts_labels[k],
            index=theme_opts_keys.index(current_theme),
            key="modal_theme_select",
        )

        if st.button(T["save_btn"], type="primary", use_container_width=True):
            st.session_state["ui_lang"]  = selected_lang
            st.session_state["ui_theme"] = selected_theme
            user = st.session_state.get("user")
            if user:
                try:
                    from db.profiles import save_ui_preferences
                    save_ui_preferences(user.id, selected_lang, selected_theme)
                except Exception:
                    pass
            st.rerun()

    with tab_how:
        st.markdown(_HOW_TO_CONTENT.get(lang, _HOW_TO_CONTENT["en"]))


@st.dialog("Configurações", width="large")
def _show_profile_modal_pt() -> None:
    _render_profile_content("pt")


@st.dialog("Settings", width="large")
def _show_profile_modal_en() -> None:
    _render_profile_content("en")


@st.dialog("Configuración", width="large")
def _show_profile_modal_es() -> None:
    _render_profile_content("es")


def _inject_sidebar_toggle() -> None:
    """Inject custom open/close sidebar buttons via JS."""
    components.html("""
<script>
(function() {
  var pd = window.parent.document;
  if (!pd.getElementById('open-sidebar-btn')) {
    var style = pd.createElement('style');
    style.textContent = [
      '#open-sidebar-btn {',
      '  position: fixed; top: 10px; left: 10px; z-index: 999999;',
      '  background: transparent; border: none; border-radius: 6px;',
      '  width: 30px; height: 30px;',
      '  display: none; align-items: center; justify-content: center;',
      '  cursor: pointer; opacity: 0.6; transition: opacity 0.15s;',
      '}',
      '#open-sidebar-btn:hover { opacity: 1; }',
      '#close-sidebar-btn {',
      '  position: absolute; top: 8px; right: 8px; z-index: 999999;',
      '  background: transparent; border: none; border-radius: 6px;',
      '  width: 30px; height: 30px;',
      '  display: none; align-items: center; justify-content: center;',
      '  cursor: pointer; opacity: 0.6; transition: opacity 0.15s;',
      '}',
      '#close-sidebar-btn:hover { opacity: 1; }'
    ].join('');
    pd.head.appendChild(style);

    var btn = pd.createElement('button');
    btn.id = 'open-sidebar-btn';
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A8A098" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
    pd.body.appendChild(btn);

    var closeBtn = pd.createElement('button');
    closeBtn.id = 'close-sidebar-btn';
    closeBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>';

    function isSidebarOpen() {
      var sb = pd.querySelector('[data-testid="stSidebar"]');
      if (!sb) return true;
      if (sb.getAttribute('aria-expanded') === 'false') return false;
      return sb.getBoundingClientRect().width > 60;
    }
    function clickNative() {
      var native =
        pd.querySelector('[data-testid="stSidebarCollapsedControl"] button') ||
        pd.querySelector('[data-testid="collapsedControl"] button') ||
        pd.querySelector('[data-testid="stSidebarCollapseButton"] button');
      if (native) {
        var prev = native.style.display;
        native.style.setProperty('display', 'block', 'important');
        native.click();
        native.style.display = prev;
      }
    }
    function update() {
      var open = isSidebarOpen();
      btn.style.display = open ? 'none' : 'flex';
      closeBtn.style.display = open ? 'flex' : 'none';
      var sb = pd.querySelector('[data-testid="stSidebar"]');
      if (sb && !sb.contains(closeBtn)) { sb.style.position = 'relative'; sb.appendChild(closeBtn); }
    }
    btn.addEventListener('click', function() { clickNative(); setTimeout(update, 400); });
    closeBtn.addEventListener('click', function() { clickNative(); setTimeout(update, 400); });
    new MutationObserver(update).observe(pd.documentElement, {
      childList: true, subtree: true, attributes: true,
      attributeFilter: ['aria-expanded', 'class', 'style']
    });
    update();
    setTimeout(update, 800);

    function fixApiKeyInput() {
      pd.querySelectorAll('input[aria-label="OpenRouter API Key"]').forEach(function(el) {
        el.setAttribute('autocomplete', 'off');
      });
    }
    new MutationObserver(fixApiKeyInput).observe(pd.documentElement, { childList: true, subtree: true });
    fixApiKeyInput();
  }
})();
</script>
""", height=0)


_ICON_SLIDERS = (
    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="4" y1="6" x2="20" y2="6"/>'
    '<line x1="4" y1="12" x2="20" y2="12"/>'
    '<line x1="4" y1="18" x2="20" y2="18"/>'
    '<circle cx="9" cy="6" r="2.5" fill="currentColor" stroke="none"/>'
    '<circle cx="16" cy="12" r="2.5" fill="currentColor" stroke="none"/>'
    '<circle cx="11" cy="18" r="2.5" fill="currentColor" stroke="none"/>'
    '</svg>'
)
_ICON_KEY = (
    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="7.5" cy="15.5" r="4.5"/>'
    '<path d="M11.3 11.7L20 3"/>'
    '<path d="M18 5l2 2"/>'
    '<path d="M15 8l2 2"/>'
    '</svg>'
)


def _section_label(text: str, icon: str = "") -> None:
    icon_html = (
        f'<span style="display:inline-flex;align-items:center;color:var(--text-muted)">{icon}</span>'
        if icon else ""
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;margin:10px 0 8px 0">'
        f'{icon_html}'
        f'<span style="font-size:0.70rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;color:var(--text-muted)">{text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _run_connection_test(api_key: str, model: str, T: dict) -> None:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say 'OK'"}],
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            reply = data["choices"][0]["message"]["content"]
            if not reply:
                st.session_state["sidebar_test_result"] = ("error", T["test_key_err_model"].format(model=model, detail="no content returned"))
            else:
                st.session_state["sidebar_test_result"] = ("ok", T["test_key_ok"].format(reply=reply))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            detail = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            detail = body
        if e.code in (401, 403):
            msg = T["test_key_err_key"].format(code=e.code, detail=detail)
        elif e.code == 402:
            msg = T["test_key_err_credits"].format(detail=detail)
        elif e.code == 404:
            msg = T["test_key_err_model"].format(model=model, detail=detail)
        elif e.code == 429:
            msg = T["test_key_err_ratelimit"].format(detail=detail)
        else:
            msg = T["test_key_fail"].format(code=e.code, detail=detail)
        st.session_state["sidebar_test_result"] = ("error", msg)
    except Exception as e:
        st.session_state["sidebar_test_result"] = ("error", T["test_key_fail"].format(code="?", detail=str(e)))


def render_sidebar() -> tuple:
    _inject_sidebar_toggle()

    ui_lang  = st.session_state.get("ui_lang", "pt")
    ui_theme = st.session_state.get("ui_theme", "system")
    T        = UI_STRINGS[ui_lang]

    is_generating = st.session_state.get("is_generating", False)

    with st.sidebar:
        user = st.session_state.get("user")

        # ── Título + botão de configurações ────────────────────────────────────
        col_title, col_cfg = st.columns([5, 1])
        with col_title:
            st.markdown(
                f'<p style="font-size:32px;font-weight:800;letter-spacing:-1px;color:var(--text);'
                f'line-height:1.1;margin:0 0 0 0">{T["title"]}</p>',
                unsafe_allow_html=True,
            )
        with col_cfg:
            if user:
                if st.button("", icon=":material/settings:", help=T["profile_modal_title"], key="profile_btn"):
                    if ui_lang == "en":
                        _show_profile_modal_en()
                    elif ui_lang == "es":
                        _show_profile_modal_es()
                    else:
                        _show_profile_modal_pt()

        # ── Nome / email ────────────────────────────────────────────────────────
        if user:
            email = getattr(user, "email", "") or ""
            st.markdown(
                f'<p style="font-size:0.82rem;color:var(--text-muted);margin:-26px 0 6px 0">'
                f'{T["auth_logged_as"]} <strong>{email}</strong></p>',
                unsafe_allow_html=True,
            )

        # ── Seção: Geração ─────────────────────────────────────────────────────
        st.markdown("---")
        _section_label(T["section_generation"], _ICON_SLIDERS)

        lang_labels = {"1": "🇧🇷 Português (Brasil)", "2": "🇺🇸 English", "3": "🇪🇸 Español"}
        lang_choice = st.selectbox(
            T["resume_language"],
            list(lang_labels.keys()),
            format_func=lambda k: lang_labels[k],
            disabled=is_generating,
        )
        lang = LANGUAGES[lang_choice]

        fmt_labels = {"docx": T["fmt_docx"], "pdf": T["fmt_pdf"], "all": T["fmt_both"]}
        fmt = st.selectbox(
            T["output_format"],
            list(fmt_labels.keys()),
            format_func=lambda k: fmt_labels[k],
            disabled=is_generating,
        )

        # ── Seção: API Key ─────────────────────────────────────────────────────
        st.markdown("---")
        _section_label(T["section_api_key"], _ICON_KEY)

        with st.form("api_key_form", border=False):
            api_key_input = st.text_input(
                T["api_key_label"],
                value=st.session_state.get("api_key", ""),
                type="password",
                disabled=is_generating,
            )
            model_input = st.text_input(
                T["ai_model"],
                value=st.session_state.get("model", ""),
                help=T["model_help"],
                disabled=is_generating,
            )
            hint = T["model_not_found"] if model_input else T["model_empty_hint"]
            st.markdown(
                f'<div class="model-hint">{hint} '
                f'<a href="https://openrouter.ai/models?q=free" target="_blank">openrouter.ai/models?q=free</a></div>',
                unsafe_allow_html=True,
            )
            if st.form_submit_button(
                T["api_key_btn"],
                use_container_width=True,
                icon=":material/save:",
                disabled=is_generating,
            ):
                if api_key_input:
                    if validate_api_key(api_key_input):
                        st.session_state["api_key"] = api_key_input
                        st.session_state["model"]   = model_input
                        st.session_state.pop("sidebar_test_result", None)
                        user = st.session_state.get("user")
                        if user:
                            from db.profiles import save_api_settings
                            try:
                                save_api_settings(user.id, api_key_input, model_input)
                            except Exception:
                                pass
                    else:
                        st.error(T["api_key_invalid"])

        api_key  = st.session_state.get("api_key", "")
        model    = st.session_state.get("model", "")
        can_test = bool(api_key) and validate_api_key(api_key) and bool(model) and not is_generating

        if st.button(
            T["test_key_btn"],
            use_container_width=True,
            icon=":material/wifi_tethering:",
            disabled=not can_test,
        ):
            with st.spinner(T["test_key_testing"]):
                _run_connection_test(api_key, model, T)

        test_result = st.session_state.get("sidebar_test_result")
        if test_result:
            status, msg = test_result
            css_class = "test-ok" if status == "ok" else "test-error"
            st.markdown(
                f'<div class="{css_class}">{msg}</div>',
                unsafe_allow_html=True,
            )

        # ── Status ─────────────────────────────────────────────────────────────
        st.markdown("---")
        if st.session_state.get("user"):
            raw_data  = st.session_state.get("profile_data", "")
            n_resumes = len(st.session_state.get("ref_resumes", []))
        else:
            raw_data         = read_data_md()
            old_resumes_text = read_old_resumes()
            n_resumes        = old_resumes_text.count("[Resume:")

        if raw_data.strip():
            st.markdown(
                f'<div class="status-ok">{T["status_ok_data"].format(chars=len(raw_data))}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-warn">{T["status_warn_data"]}</div>',
                unsafe_allow_html=True,
            )

        if n_resumes > 0:
            st.markdown(
                f'<div class="status-ok">{T["status_ok_resumes"].format(n=n_resumes)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-warn">{T["status_warn_resumes"]}</div>',
                unsafe_allow_html=True,
            )

        # ── Sair ───────────────────────────────────────────────────────────────
        if user:
            st.markdown("---")
            if st.button(
                T["auth_logout"],
                icon=":material/logout:",
                use_container_width=True,
                key="logout_btn",
            ):
                from supabase_client import get_supabase
                from ui.auth import clear_user_session
                try:
                    get_supabase().auth.sign_out()
                except Exception:
                    pass
                st.session_state["_clear_cookies"] = True
                clear_user_session()
                st.rerun()
            _logout_label = json.dumps(T["auth_logout"])
            components.html(
                f"<script>(function(){{"
                f"function s(){{"
                f"var pd=window.parent.document;"
                f"pd.querySelectorAll('[data-testid=\"stSidebar\"] button').forEach(function(b){{"
                f"if(b.textContent.trim()==={_logout_label}){{"
                f"b.style.setProperty('background','#dc2626','important');"
                f"b.style.setProperty('color','#ffffff','important');"
                f"b.style.setProperty('border-color','#dc2626','important');"
                f"}}}});}}"
                f"s();new MutationObserver(function(){{setTimeout(s,60);}}).observe("
                f"window.parent.document.documentElement,{{childList:true,subtree:true}});"
                f"}})();</script>",
                height=0,
            )

    return lang, fmt, model, api_key, T
