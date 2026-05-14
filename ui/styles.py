import streamlit as st

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

GLOBAL_CSS = """
<style>
  #MainMenu { display: none !important; }
  footer { display: none !important; }
  header { background: transparent !important; }

  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"] { display: none !important; }

  h1 { font-weight: 600 !important; letter-spacing: -0.5px !important; }
  h3 { font-weight: 500 !important; color: var(--text-muted) !important; margin-bottom: 0 !important; }

  [data-testid="stSidebar"] { background: var(--bg) !important; border-right: 1px solid var(--border) !important; }
  [data-testid="stSidebar"] h1 { font-size: 32px !important; font-weight: 800 !important; letter-spacing: -1px !important; color: var(--text) !important; margin-bottom: 8px !important; }
  [data-testid="stSidebar"] hr { border-color: var(--border) !important; }

  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
  }

  .status-ok   { background: var(--status-ok-bg); border: 1px solid var(--status-ok-border); color: var(--status-ok-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }
  .status-warn { background: var(--status-warn-bg); border: 1px solid var(--status-warn-border); color: var(--status-warn-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }

  .file-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
  .file-name { font-family: monospace; font-size: 13px; font-weight: 600; color: var(--text); }
  .file-size { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

  .preview-box { background: var(--preview-bg); border: 1px solid var(--preview-border); border-radius: 8px; padding: 20px; font-family: monospace; font-size: 12.5px; line-height: 1.75; white-space: pre-wrap; max-height: 500px; overflow-y: auto; color: var(--text); }

  .stButton > button { border-radius: 6px !important; font-weight: 500 !important; }
  div[data-testid="stDownloadButton"] > button { width: 100% !important; }

  .del-btn-wrap { display: flex; align-items: center; height: 100%; padding-bottom: 8px; }
  .del-btn-wrap .stButton > button {
    background: #DC2626 !important; color: #fff !important;
    border: none !important; border-radius: 6px !important;
    padding: 6px 10px !important; font-size: 14px !important;
    line-height: 1 !important; height: 40px !important;
    min-height: unset !important; width: 100% !important;
  }
  .del-btn-wrap .stButton > button:hover { background: #B91C1C !important; }

  [data-testid="stSidebar"] .stSelectbox,
  [data-testid="stSidebar"] .stTextInput,
  [data-testid="stSidebar"] .stMarkdown p { margin-bottom: 0px !important; }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { gap: 0px !important; }
  [data-testid="stSidebar"] .block-container { gap: 0px !important; }

  .model-hint { font-size: 11px; color: var(--text-muted); margin-top: 2px; line-height: 1.4; }
  .model-hint a { color: #5B8EF5; text-decoration: none; }
  .model-hint a:hover { text-decoration: underline; }
</style>
"""


def inject_styles(theme: str) -> None:
    """Inject theme variables and global CSS into the page."""
    st.markdown(f"<style>{THEME_CSS[theme]}</style>", unsafe_allow_html=True)
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
