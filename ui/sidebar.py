import streamlit as st
import streamlit.components.v1 as components

from ui.i18n import UI_STRINGS
from generate import LANGUAGES, read_data_md, read_old_resumes, validate_api_key


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
  }
})();
</script>
""", height=0)


def render_sidebar() -> tuple[str, str, str, str]:
    """
    Render the full sidebar.

    Returns:
        lang   – resume language string (e.g. "pt-br")
        fmt    – output format ("docx" | "pdf" | "all")
        model  – AI model name string
        T      – translation dict for the active UI language
    """
    _inject_sidebar_toggle()

    ui_lang  = st.session_state.get("ui_lang", "pt")
    ui_theme = st.session_state.get("ui_theme", "system")
    T        = UI_STRINGS[ui_lang]

    is_generating = st.session_state.get("is_generating", False)

    with st.sidebar:
        st.markdown(
            f'<p style="font-size:32px;font-weight:800;letter-spacing:-1px;color:var(--text);'
            f'line-height:1.1;margin:0 0 8px 0; padding:0 0 20px 0;">{T["title"]}</p>',
            unsafe_allow_html=True,
        )

        col_lang, col_theme, _ = st.columns([3, 2, 1])

        with col_lang:
            ui_lang_options = {"pt": "🇧🇷 Português", "en": "🇺🇸 English", "es": "🇪🇸 Español"}
            selected_lang = st.selectbox(
                "lang",
                options=list(ui_lang_options.keys()),
                format_func=lambda k: ui_lang_options[k],
                index=list(ui_lang_options.keys()).index(ui_lang),
                label_visibility="collapsed",
                key="lang_select",
                disabled=is_generating,
            )
            if selected_lang != ui_lang:
                st.session_state["ui_lang"] = selected_lang
                if "theme_select" in st.session_state:
                    del st.session_state["theme_select"]
                st.rerun()

        with col_theme:
            theme_opts_keys   = ["light", "dark", "system"]
            theme_opts_labels = {
                "light":  T["theme_light"],
                "dark":   T["theme_dark"],
                "system": T["theme_system"],
            }
            selected_theme = st.selectbox(
                "theme",
                options=theme_opts_keys,
                format_func=lambda k: theme_opts_labels[k],
                index=theme_opts_keys.index(ui_theme),
                label_visibility="collapsed",
                key="theme_select",
                disabled=is_generating,
            )
            if selected_theme != ui_theme:
                st.session_state["ui_theme"] = selected_theme
                st.rerun()

        st.markdown("---")

        # ── status indicators ──────────────────────────────────────────────────
        raw_data        = read_data_md()
        old_resumes_text = read_old_resumes()
        n_resumes       = old_resumes_text.count("[Resume:")

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

        st.markdown("---")

        # ── options ────────────────────────────────────────────────────────────
        lang_labels = {
            "1": "🇧🇷 Português (Brasil)",
            "2": "🇺🇸 English",
            "3": "🇪🇸 Español",
        }
        lang_choice = st.selectbox(
            T["resume_language"],
            list(lang_labels.keys()),
            format_func=lambda k: lang_labels[k],
            disabled=is_generating,
        )
        lang = LANGUAGES[lang_choice]

        fmt_labels = {
            "docx": T["fmt_docx"],
            "pdf":  T["fmt_pdf"],
            "all":  T["fmt_both"],
        }
        fmt = st.selectbox(
            T["output_format"],
            list(fmt_labels.keys()),
            format_func=lambda k: fmt_labels[k],
            disabled=is_generating,
        )

        model = st.text_input(T["ai_model"], value="", help=T["model_help"], disabled=is_generating)
        hint = T["model_not_found"] if model else T["model_empty_hint"]
        st.markdown(
            f'<div class="model-hint">{hint} '
            f'<a href="https://openrouter.ai/models?q=free" target="_blank">openrouter.ai/models?q=free</a></div>',
            unsafe_allow_html=True,
        )

        with st.form("api_key_form", border=False):
            api_key_input = st.text_input(
                T["api_key_label"],
                value=st.session_state.get("api_key", ""),
                type="password",
                help=T["api_key_help"],
                disabled=is_generating,
            )
            if st.form_submit_button(T["api_key_btn"], use_container_width=True, icon=":material/save:", disabled=is_generating):
                if api_key_input:
                    if validate_api_key(api_key_input):
                        st.session_state["api_key"] = api_key_input
                    else:
                        st.error(T["api_key_invalid"])

        api_key = st.session_state.get("api_key", "")

    return lang, fmt, model, api_key, T
