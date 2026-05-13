import streamlit as st
import sys, os, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import (
    LANGUAGES, read_data_md, read_old_resumes,
    build_prompt, call_model, save_docx, save_pdf,
    OUTPUT_DIR, DATA_MD, OLD_RESUMES_DIR, MODEL
)

OLD_RESUMES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}

# ── UI translations ────────────────────────────────────────────────────────────

UI_STRINGS = {
    "pt": {
        "title": "RouterResume",
        "options": "Opções",
        "resume_language": "Idioma do currículo",
        "output_format": "Formato de saída",
        "ai_model": "Modelo de IA",
        "model_help": "Modelos gratuitos em openrouter.ai/models",
        "model_not_found": "Se o modelo não estiver funcionando, procure modelos gratuitos disponíveis em:",
        "tab_generate": "Gerar",
        "tab_resumes": "Currículos Antigos",
        "tab_data": "Dados do Perfil",
        "job_label": "Cole a descrição da vaga",
        "job_placeholder": "Cole aqui o texto completo da vaga — título, empresa, requisitos, responsabilidades, tudo...",
        "generate_btn": "Gerar currículo",
        "no_job_error": "Por favor, cole uma descrição de vaga antes.",
        "no_api_error": "OPENROUTER_API_KEY não configurada. Defina no ambiente e reinicie.",
        "no_data_error": "Preencha seus **Dados do Perfil** antes de gerar um currículo.",
        "no_resumes_error": "Adicione ao menos um **Currículo Antigo** para melhorar os resultados.",
        "no_data_and_resumes_error": "Preencha seus **Dados do Perfil** e adicione ao menos um **Currículo Antigo** antes de gerar.",
        "status_reading": "Lendo dados do perfil... ({chars:,} caracteres)",
        "status_resumes": "Currículos antigos: {n} arquivo(s)",
        "status_calling": "Chamando OpenRouter ({model})...",
        "status_done": "Concluído!",
        "status_title_ok": "Currículo gerado!",
        "status_title_fail": "Falhou",
        "status_generating": "Gerando seu currículo...",
        "api_fail": "Chamada à API falhou. Verifique o nome do modelo ou a chave.",
        "error_prefix": "Erro: ",
        "download_title": "### Download",
        "preview_title": "Pré-visualização",
        "upload_title": "### Enviar currículos",
        "upload_label": "Solte os arquivos aqui",
        "upload_success": "{n} arquivo(s) enviado(s)",
        "saved_files": "### Arquivos salvos",
        "no_resumes": "Nenhum currículo ainda. Envie alguns à esquerda.",
        "profile_title": "### Seus dados brutos de perfil",
        "profile_caption": "Adicione qualquer coisa sobre você — sem formato obrigatório. Quanto mais, melhor.",
        "profile_placeholder": "Jogue aqui tudo: experiências, habilidades, educação, projetos, conquistas...",
        "save_btn": "Salvar data.md",
        "save_success": "Salvo!",
        "status_ok_data": "data.md — {chars:,} caracteres",
        "status_warn_data": "data.md está vazio",
        "status_ok_resumes": "{n} currículo(s) antigo(s)",
        "status_warn_resumes": "Nenhum currículo antigo",
        "theme_label": "Tema",
        "lang_ui_label": "Idioma da interface",
        "theme_light": "Claro",
        "theme_dark": "Escuro",
        "theme_system": "Sistema",
        "fmt_docx": "DOCX (Word)",
        "fmt_pdf": "PDF",
        "fmt_both": "Ambos",
        "upload_btn": "Enviar arquivos",
        "upload_select": "arquivo(s) selecionado(s). Clique em Enviar para salvar.",
    },
    "en": {
        "title": "RouterResume",
        "options": "Options",
        "resume_language": "Resume language",
        "output_format": "Output format",
        "ai_model": "AI model",
        "model_help": "Free models at openrouter.ai/models",
        "model_not_found": "If the model is not responding, look for available free models at:",
        "tab_generate": "Generate",
        "tab_resumes": "Old Resumes",
        "tab_data": "Profile Data",
        "job_label": "Paste the job description",
        "job_placeholder": "Paste the full job posting here — title, company, requirements, responsibilities, everything...",
        "generate_btn": "Generate resume",
        "no_job_error": "Please paste a job description first.",
        "no_api_error": "OPENROUTER_API_KEY not set. Set it in your environment and restart.",
        "no_data_error": "Fill in your **Profile Data** before generating a resume.",
        "no_resumes_error": "Add at least one **Old Resume** to improve the results.",
        "no_data_and_resumes_error": "Fill in your **Profile Data** and add at least one **Old Resume** before generating.",
        "status_reading": "Reading profile data... ({chars:,} chars)",
        "status_resumes": "Old resumes: {n} file(s)",
        "status_calling": "Calling OpenRouter ({model})...",
        "status_done": "Done!",
        "status_title_ok": "Resume generated!",
        "status_title_fail": "Failed",
        "status_generating": "Generating your resume...",
        "api_fail": "API call failed. Check model name or API key.",
        "error_prefix": "Error: ",
        "download_title": "### Download",
        "preview_title": "Preview",
        "upload_title": "### Upload resumes",
        "upload_label": "Drop files here",
        "upload_success": "{n} file(s) uploaded",
        "saved_files": "### Saved files",
        "no_resumes": "No old resumes yet. Upload some on the left.",
        "profile_title": "### Your raw profile data",
        "profile_caption": "Add anything about yourself — no format required. The more you add, the better the generated resumes.",
        "profile_placeholder": "Dump anything here: experiences, skills, education, projects, achievements...",
        "save_btn": "Save data.md",
        "save_success": "Saved!",
        "status_ok_data": "data.md — {chars:,} chars",
        "status_warn_data": "data.md is empty",
        "status_ok_resumes": "{n} old resume(s)",
        "status_warn_resumes": "No old resumes",
        "theme_label": "Theme",
        "lang_ui_label": "Interface language",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_system": "System",
        "fmt_docx": "DOCX (Word)",
        "fmt_pdf": "PDF",
        "fmt_both": "Both",
        "upload_btn": "Upload files",
        "upload_select": "file(s) selected. Click Upload to save.",
    },
    "es": {
        "title": "RouterResume",
        "options": "Opciones",
        "resume_language": "Idioma del currículum",
        "output_format": "Formato de salida",
        "ai_model": "Modelo de IA",
        "model_help": "Modelos gratuitos en openrouter.ai/models",
        "model_not_found": "Si el modelo no responde, busca modelos gratuitos disponibles en:",
        "tab_generate": "Generar",
        "tab_resumes": "CV Anteriores",
        "tab_data": "Datos del Perfil",
        "job_label": "Pega la descripción del puesto",
        "job_placeholder": "Pega aquí el texto completo de la oferta — título, empresa, requisitos, responsabilidades, todo...",
        "generate_btn": "Generar currículum",
        "no_job_error": "Por favor, pega una descripción de trabajo primero.",
        "no_api_error": "OPENROUTER_API_KEY no configurada. Configúrala en tu entorno y reinicia.",
        "no_data_error": "Completa tus **Datos del Perfil** antes de generar un currículum.",
        "no_resumes_error": "Agrega al menos un **CV Anterior** para mejorar los resultados.",
        "no_data_and_resumes_error": "Completa tus **Datos del Perfil** y agrega al menos un **CV Anterior** antes de generar.",
        "status_reading": "Leyendo datos del perfil... ({chars:,} caracteres)",
        "status_resumes": "CV anteriores: {n} archivo(s)",
        "status_calling": "Llamando a OpenRouter ({model})...",
        "status_done": "¡Listo!",
        "status_title_ok": "¡Currículum generado!",
        "status_title_fail": "Falló",
        "status_generating": "Generando tu currículum...",
        "api_fail": "Falló la llamada a la API. Verifica el modelo o la clave.",
        "error_prefix": "Error: ",
        "download_title": "### Descargar",
        "preview_title": "Vista previa",
        "upload_title": "### Subir currículums",
        "upload_label": "Suelta los archivos aquí",
        "upload_success": "{n} archivo(s) subido(s)",
        "saved_files": "### Archivos guardados",
        "no_resumes": "Sin currículums aún. Sube algunos a la izquierda.",
        "profile_title": "### Tus datos de perfil en bruto",
        "profile_caption": "Agrega cualquier cosa sobre ti — sin formato obligatorio. Cuanto más, mejor.",
        "profile_placeholder": "Vuelca aquí todo: experiencias, habilidades, educación, proyectos, logros...",
        "save_btn": "Guardar data.md",
        "save_success": "¡Guardado!",
        "status_ok_data": "data.md — {chars:,} caracteres",
        "status_warn_data": "data.md está vacío",
        "status_ok_resumes": "{n} CV(s) anterior(es)",
        "status_warn_resumes": "Sin CVs anteriores",
        "theme_label": "Tema",
        "lang_ui_label": "Idioma de la interfaz",
        "theme_light": "Claro",
        "theme_dark": "Oscuro",
        "theme_system": "Sistema",
        "fmt_docx": "DOCX (Word)",
        "fmt_pdf": "PDF",
        "fmt_both": "Ambos",
        "upload_btn": "Subir archivos",
        "upload_select": "archivo(s) seleccionado(s). Haz clic en Subir para guardar.",
    },
}

# ── page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RouterResume",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── session state defaults ─────────────────────────────────────────────────────

if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = "pt"
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "system"
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

ui_lang  = st.session_state["ui_lang"]
ui_theme = st.session_state["ui_theme"]
T        = UI_STRINGS[ui_lang]

# ── theme CSS ──────────────────────────────────────────────────────────────────

THEME_CSS = {
    "light": """
        :root {
            --bg: #FAFAF8; --surface: #F0EDE8; --border: #E8E4DE;
            --text: #1A1814; --text-muted: #555; --text-faint: #aaa;
            --card-bg: #F0EDE8; --card-border: #C8C2BA;
            --preview-bg: #FDFCFA; --preview-border: #E0DBD4;
            --status-ok-bg: #EDFBF3; --status-ok-border: #A8DFBB; --status-ok-text: #1E6B3E;
            --status-warn-bg: #FFF8EC; --status-warn-border: #F5C97A; --status-warn-text: #7A4E00;
        }
    """,
    "dark": """
        :root {
            --bg: #1A1814; --surface: #242018; --border: #3A342C;
            --text: #F0EDE8; --text-muted: #A8A098; --text-faint: #666;
            --card-bg: #242018; --card-border: #3A342C;
            --preview-bg: #1E1C18; --preview-border: #3A342C;
            --status-ok-bg: #0D2B1A; --status-ok-border: #2A6B40; --status-ok-text: #6FDFAA;
            --status-warn-bg: #2B1E00; --status-warn-border: #8A6400; --status-warn-text: #F5C97A;
        }
    """,
    "system": """
        :root {
            --bg: #FAFAF8; --surface: #F0EDE8; --border: #E8E4DE;
            --text: #1A1814; --text-muted: #555; --text-faint: #aaa;
            --card-bg: #F0EDE8; --card-border: #C8C2BA;
            --preview-bg: #FDFCFA; --preview-border: #E0DBD4;
            --status-ok-bg: #EDFBF3; --status-ok-border: #A8DFBB; --status-ok-text: #1E6B3E;
            --status-warn-bg: #FFF8EC; --status-warn-border: #F5C97A; --status-warn-text: #7A4E00;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #1A1814; --surface: #242018; --border: #3A342C;
                --text: #F0EDE8; --text-muted: #A8A098; --text-faint: #666;
                --card-bg: #242018; --card-border: #3A342C;
                --preview-bg: #1E1C18; --preview-border: #3A342C;
                --status-ok-bg: #0D2B1A; --status-ok-border: #2A6B40; --status-ok-text: #6FDFAA;
                --status-warn-bg: #2B1E00; --status-warn-border: #8A6400; --status-warn-text: #F5C97A;
            }
        }
    """,
}

st.markdown(f"<style>{THEME_CSS[ui_theme]}</style>", unsafe_allow_html=True)

st.markdown(f"""
<style>
  /* Hide streamlit chrome */
  #MainMenu {{ display: none !important; }}
  footer {{ display: none !important; }}
  header {{ background: transparent !important; }}

  /* Hide Streamlit's own sidebar toggle buttons — usamos o nosso */
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"] {{
    display: none !important;
  }}

  /* ── Botão customizado de abrir sidebar ── */
  #open-sidebar-btn {{
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 999999;
    background: #5B8EF5;
    border: none;
    border-radius: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: background 0.15s;
  }}
  #open-sidebar-btn:hover {{ background: #4a7de8; }}
  #open-sidebar-btn svg {{ stroke: #fff; fill: none; }}

  /* Sidebar dividers */
  [data-testid="stSidebar"] hr {{
    border-color: var(--border) !important;
  }}
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-child .stColumns {{
    margin-top: 0 !important;
    padding-top: 0 !important;
  }}
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-child .stSelectbox > div > div {{
    min-height: 32px !important;
    font-size: 12px !important;
  }}

  /* Clean typography */
  h1 {{ font-weight: 600 !important; letter-spacing: -0.5px !important; }}
  h3 {{ font-weight: 500 !important; color: var(--text-muted) !important; margin-bottom: 0 !important; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{ background: var(--bg) !important; border-right: 1px solid var(--border) !important; }}
  [data-testid="stSidebar"] h1 {{ font-size: 18px !important; color: var(--text) !important; }}

  /* Sidebar labels */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label {{
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
  }}

  /* Status badges */
  .status-ok   {{ background: var(--status-ok-bg); border: 1px solid var(--status-ok-border); color: var(--status-ok-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }}
  .status-warn {{ background: var(--status-warn-bg); border: 1px solid var(--status-warn-border); color: var(--status-warn-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }}

  /* File cards */
  .file-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }}
  .file-name {{ font-family: monospace; font-size: 13px; font-weight: 600; color: var(--text); }}
  .file-size {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}

  /* Preview box */
  .preview-box {{ background: var(--preview-bg); border: 1px solid var(--preview-border); border-radius: 8px; padding: 20px; font-family: monospace; font-size: 12.5px; line-height: 1.75; white-space: pre-wrap; max-height: 500px; overflow-y: auto; color: var(--text); }}

  /* Stbutton tweaks */
  .stButton > button {{ border-radius: 6px !important; font-weight: 500 !important; }}
  div[data-testid="stDownloadButton"] > button {{ width: 100% !important; }}

  /* Delete button */
  .del-btn-wrap {{ display: flex; align-items: center; height: 100%; padding-bottom: 8px; }}
  .del-btn-wrap .stButton > button {{
    background: #DC2626 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 6px 10px !important;
    font-size: 14px !important;
    line-height: 1 !important;
    height: 40px !important;
    min-height: unset !important;
    width: 100% !important;
  }}
  .del-btn-wrap .stButton > button:hover {{ background: #B91C1C !important; }}

  /* Sidebar options — tight gap */
  [data-testid="stSidebar"] .stSelectbox,
  [data-testid="stSidebar"] .stTextInput,
  [data-testid="stSidebar"] .stMarkdown p {{ margin-bottom: 0px !important; }}
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{ gap: 0px !important; }}
  [data-testid="stSidebar"] .block-container {{ gap: 0px !important; }}

  /* Model hint link */
  .model-hint {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; line-height: 1.4; }}
  .model-hint a {{ color: #5B8EF5; text-decoration: none; }}
  .model-hint a:hover {{ text-decoration: underline; }}
</style>
""", unsafe_allow_html=True)

# ── botão customizado para abrir o sidebar ────────────────────────────────────
import streamlit.components.v1 as components

components.html("""
<script>
(function() {
  var pd = window.parent.document;

  // Injeta o botão e o estilo diretamente no documento pai
  if (!pd.getElementById('open-sidebar-btn')) {
    var style = pd.createElement('style');
    style.id = 'open-sidebar-btn-style';
    style.textContent = [
      '#open-sidebar-btn {',
      '  position: fixed; top: 10px; left: 10px; z-index: 999999;',
      '  background: transparent; border: none; border-radius: 6px;',
      '  width: 30px; height: 30px;',
      '  display: none; align-items: center; justify-content: center;',
      '  cursor: pointer; opacity: 0.6; transition: opacity 0.15s;',
      '}',
      '#open-sidebar-btn:hover { opacity: 1; }'
    ].join('');
    pd.head.appendChild(style);

    var btn = pd.createElement('button');
    btn.id = 'open-sidebar-btn';
    btn.title = 'Abrir menu';
    btn.setAttribute('aria-label', 'Abrir menu');
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A8A098" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
    pd.body.appendChild(btn);

    // Botão de FECHAR dentro do sidebar
    var closeStyle = pd.createElement('style');
    closeStyle.textContent = [
      '#close-sidebar-btn {',
      '  position: absolute; top: 8px; right: 8px; z-index: 999999;',
      '  background: transparent; border: none; border-radius: 6px;',
      '  width: 30px; height: 30px;',
      '  display: none; align-items: center; justify-content: center;',
      '  cursor: pointer; opacity: 0.6; transition: opacity 0.15s;',
      '}',
      '#close-sidebar-btn:hover { opacity: 1; }'
    ].join('');
    pd.head.appendChild(closeStyle);

    var closeBtn = pd.createElement('button');
    closeBtn.id = 'close-sidebar-btn';
    closeBtn.title = 'Fechar menu';
    closeBtn.setAttribute('aria-label', 'Fechar menu');
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

      // Garante que o closeBtn está dentro do sidebar
      var sb = pd.querySelector('[data-testid="stSidebar"]');
      if (sb && !sb.contains(closeBtn)) {
        sb.style.position = 'relative';
        sb.appendChild(closeBtn);
      }
    }

    btn.addEventListener('click', function() {
      clickNative();
      setTimeout(update, 400);
    });

    closeBtn.addEventListener('click', function() {
      clickNative();
      setTimeout(update, 400);
    });

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

# ── sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"# 🛣️ {T['title']}")

    # ── topo do sidebar: [lang] [tema] [fechar] na mesma linha ──────────────
    col_lang, col_theme, col_close = st.columns([3, 2, 1])
    with col_lang:
        ui_lang_options = {"pt": "🇧🇷 Português", "en": "🇺🇸 English", "es": "🇪🇸 Español"}
        selected_lang = st.selectbox(
            "lang",
            options=list(ui_lang_options.keys()),
            format_func=lambda k: ui_lang_options[k],
            index=list(ui_lang_options.keys()).index(ui_lang),
            label_visibility="collapsed",
            key="lang_select",
        )
        if selected_lang != ui_lang:
            st.session_state["ui_lang"] = selected_lang
            if "theme_select" in st.session_state:
                del st.session_state["theme_select"]
            st.rerun()
    with col_theme:
        theme_opts_keys = ["light", "dark", "system"]
        theme_opts_labels = {
            "light":  T["theme_light"],
            "dark":   T["theme_dark"],
            "system": T["theme_system"],
        }
        selected_theme = st.selectbox(
            "theme",
            options=theme_opts_keys,
            format_func=lambda k: theme_opts_labels[k],
            index=theme_opts_keys.index(st.session_state["ui_theme"]),
            label_visibility="collapsed",
            key="theme_select",
        )
        if selected_theme != ui_theme:
            st.session_state["ui_theme"] = selected_theme
            st.rerun()
    with col_close:
        # espaço reservado — o botão fechar (JS) fica posicionado em absolute right
        st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Status
    raw_data = read_data_md()
    old_resumes_text = read_old_resumes()
    n_resumes = old_resumes_text.count("[Resume:")

    if raw_data.strip():
        st.markdown(f'<div class="status-ok">{T["status_ok_data"].format(chars=len(raw_data))}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-warn">{T["status_warn_data"]}</div>', unsafe_allow_html=True)

    if n_resumes > 0:
        st.markdown(f'<div class="status-ok">{T["status_ok_resumes"].format(n=n_resumes)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-warn">{T["status_warn_resumes"]}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Options
    st.markdown(f"### {T['options']}")

    lang_labels = {"1": "🇧🇷 Português (Brasil)", "2": "🇺🇸 English", "3": "🇪🇸 Español"}
    lang_choice = st.selectbox(T["resume_language"], list(lang_labels.keys()), format_func=lambda k: lang_labels[k])
    lang = LANGUAGES[lang_choice]

    fmt_labels = {"docx": T["fmt_docx"], "pdf": T["fmt_pdf"], "all": T["fmt_both"]}
    fmt = st.selectbox(T["output_format"], list(fmt_labels.keys()), format_func=lambda k: fmt_labels[k])

    model = st.text_input(T["ai_model"], value=MODEL, help=T["model_help"])

    st.markdown(
        f'<div class="model-hint">{T["model_not_found"]} '
        f'<a href="https://openrouter.ai/models?q=free" target="_blank">openrouter.ai/models?q=free</a></div>',
        unsafe_allow_html=True
    )

# ── main tabs ──────────────────────────────────────────────────────────────────

tab_gen, tab_resumes, tab_data = st.tabs([T["tab_generate"], T["tab_resumes"], T["tab_data"]])

# ── TAB: GENERATE ─────────────────────────────────────────────────────────────

with tab_gen:
    st.markdown(f"### {T['job_label']}")
    job = st.text_area(
        label="job",
        placeholder=T["job_placeholder"],
        height=260,
        label_visibility="collapsed",
    )

    has_data    = bool(raw_data.strip())
    has_resumes = n_resumes > 0
    can_generate = has_data and has_resumes

    if not has_data and not has_resumes:
        st.warning(T["no_data_and_resumes_error"])
    elif not has_data:
        st.warning(T["no_data_error"])
    elif not has_resumes:
        st.warning(T["no_resumes_error"])

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        generate_btn = st.button(
            T["generate_btn"],
            type="primary",
            use_container_width=True,
            disabled=not can_generate,
        )

    if generate_btn:
        if not job.strip():
            st.error(T["no_job_error"])
        elif not os.environ.get("OPENROUTER_API_KEY"):
            st.error(T["no_api_error"])
        else:
            with st.status(T["status_generating"], expanded=True) as status:
                st.write(T["status_reading"].format(chars=len(raw_data)))
                st.write(T["status_resumes"].format(n=n_resumes))
                st.write(T["status_calling"].format(model=model))

                try:
                    prompt = build_prompt(raw_data, old_resumes_text, job.strip(), lang)
                    ui_stub = {
                        "calling_api": "Calling", "api_key_error": "", "api_key_hint": "",
                        "api_key_hint2": "", "api_error": "API error",
                        "api_empty": "Empty response", "api_unexpected": "Unexpected response",
                    }
                    resume = call_model(prompt, model, ui_stub)

                    ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    base_name = f"routerresume_{ts}"
                    ui_doc    = {"docx_missing": "python-docx not installed", "pdf_missing": "reportlab not installed"}

                    saved_paths = []
                    if fmt in ("docx", "all"):
                        p = save_docx(resume, base_name, lang, ui_doc)
                        if p: saved_paths.append(p)
                    if fmt in ("pdf", "all"):
                        p = save_pdf(resume, base_name, lang, ui_doc)
                        if p: saved_paths.append(p)

                    st.write(T["status_done"])
                    status.update(label=T["status_title_ok"], state="complete")

                    st.session_state["resume_text"] = resume
                    st.session_state["saved_paths"] = saved_paths

                except SystemExit:
                    status.update(label=T["status_title_fail"], state="error")
                    st.error(T["api_fail"])
                except Exception as e:
                    status.update(label=T["status_title_fail"], state="error")
                    st.error(f"{T['error_prefix']}{e}")

    # Download + preview
    if "saved_paths" in st.session_state and st.session_state["saved_paths"]:
        st.markdown("---")
        st.markdown(T["download_title"])
        dl_cols = st.columns(len(st.session_state["saved_paths"]))
        for col, path in zip(dl_cols, st.session_state["saved_paths"]):
            with col:
                mime = ("application/vnd.openxmlformats-officedocument"
                        ".wordprocessingml.document" if path.suffix == ".docx" else "application/pdf")
                st.download_button(
                    label=f"⬇ {path.name}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime=mime,
                    use_container_width=True,
                )

    if "resume_text" in st.session_state:
        with st.expander(T["preview_title"], expanded=True):
            st.markdown(
                f'<div class="preview-box">{st.session_state["resume_text"]}</div>',
                unsafe_allow_html=True
            )

# ── TAB: OLD RESUMES ──────────────────────────────────────────────────────────

with tab_resumes:
    col_up, col_list = st.columns([1, 1], gap="large")

    with col_up:
        st.markdown(T["upload_title"])
        uploaded = st.file_uploader(
            T["upload_label"],
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"uploader_{st.session_state['uploader_key']}",
        )
        has_files = bool(uploaded)
        if has_files:
            st.info(f"{len(uploaded)} {T['upload_select']}")
        if st.button(T["upload_btn"], type="primary", use_container_width=True, disabled=not has_files):
            saved_count = 0
            for f in uploaded:
                dest = OLD_RESUMES_DIR / f.name
                dest.write_bytes(f.read())
                saved_count += 1
            st.session_state["uploader_key"] += 1
            st.success(T["upload_success"].format(n=saved_count))
            st.rerun()

    with col_list:
        st.markdown(T["saved_files"])
        files = []
        if OLD_RESUMES_DIR.exists():
            files = [f for f in sorted(OLD_RESUMES_DIR.iterdir())
                     if f.is_file() and f.suffix.lower() in ALLOWED_EXTS]

        if not files:
            st.info(T["no_resumes"])
        else:
            for f in files:
                size = f.stat().st_size
                size_str = f"{size/1024:.1f} KB" if size >= 1024 else f"{size} B"
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f'<div class="file-card">'
                        f'<div><div class="file-name">📄 {f.name}</div>'
                        f'<div class="file-size">{size_str}</div></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown('<div class="del-btn-wrap">', unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{f.name}", help=f"Remove {f.name}"):
                        f.unlink()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB: PROFILE DATA ─────────────────────────────────────────────────────────

with tab_data:
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