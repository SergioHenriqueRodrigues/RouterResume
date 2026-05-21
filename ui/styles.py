import streamlit as st

THEME_CSS = {
    "light": """
        :root {
            --bg: #EDEBE6; --surface: #E4E0D9; --border: #CEC8BF;
            --text: #1A1814; --text-muted: #555; --text-faint: #aaa;
            --card-bg: #E4E0D9; --card-border: #BCB5AB;
            --preview-bg: #F2EFE9; --preview-border: #D4CEC6;
            --status-ok-bg: #EDFBF3; --status-ok-border: #A8DFBB; --status-ok-text: #1E6B3E;
            --status-warn-bg: #FFF8EC; --status-warn-border: #F5C97A; --status-warn-text: #7A4E00;
            --btn-hover-bg: #3A3530; --btn-hover-text: #F0EDE8;
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
            --btn-hover-bg: #4A453F; --btn-hover-text: #F0EDE8;
        }
    """,
    "system": """
        :root {
            --bg: #EDEBE6; --surface: #E4E0D9; --border: #CEC8BF;
            --text: #1A1814; --text-muted: #555; --text-faint: #aaa;
            --card-bg: #E4E0D9; --card-border: #BCB5AB;
            --preview-bg: #F2EFE9; --preview-border: #D4CEC6;
            --status-ok-bg: #EDFBF3; --status-ok-border: #A8DFBB; --status-ok-text: #1E6B3E;
            --status-warn-bg: #FFF8EC; --status-warn-border: #F5C97A; --status-warn-text: #7A4E00;
            --btn-hover-bg: #3A3530; --btn-hover-text: #F0EDE8;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #1A1814; --surface: #242018; --border: #3A342C;
                --text: #F0EDE8; --text-muted: #A8A098; --text-faint: #666;
                --card-bg: #242018; --card-border: #3A342C;
                --preview-bg: #1E1C18; --preview-border: #3A342C;
                --status-ok-bg: #0D2B1A; --status-ok-border: #2A6B40; --status-ok-text: #6FDFAA;
                --status-warn-bg: #2B1E00; --status-warn-border: #8A6400; --status-warn-text: #F5C97A;
                --btn-hover-bg: #4A453F; --btn-hover-text: #F0EDE8;
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
  [data-testid="stAppDeployButton"],
  [data-testid="stDeployButton"],
  [data-testid="stToolbarActions"],
  [data-testid="stBottom"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"] { display: none !important; }

  h1 { font-weight: 600 !important; letter-spacing: -0.5px !important; }
  h3 { font-weight: 500 !important; color: var(--text-muted) !important; margin-bottom: 0 !important; }
  [data-testid="stMarkdownContainer"] h1 a,
  [data-testid="stMarkdownContainer"] h2 a,
  [data-testid="stMarkdownContainer"] h3 a,
  [data-testid="stMarkdownContainer"] h4 a { display: none !important; }

  [data-testid="stSidebar"] { background: var(--bg) !important; border-right: 1px solid var(--border) !important; min-width: 385px !important; }
  [data-testid="stSidebar"] h1 { font-size: 32px !important; font-weight: 800 !important; letter-spacing: -1px !important; color: var(--text) !important; margin-bottom: 8px !important; }
  [data-testid="stSidebar"] hr { border-color: var(--border) !important; margin: 6px 0 !important; }

  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
  }

  .status-ok   { background: var(--status-ok-bg); border: 1px solid var(--status-ok-border); color: var(--status-ok-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }
  .status-warn { background: var(--status-warn-bg); border: 1px solid var(--status-warn-border); color: var(--status-warn-text); padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }
  .status-nav  { cursor: pointer; user-select: none; transition: filter 0.13s, transform 0.1s; }
  .status-nav:hover { filter: brightness(0.88); transform: translateX(2px); }

  .file-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
  .file-name { font-family: monospace; font-size: 13px; font-weight: 600; color: var(--text); }
  .file-size { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

  .preview-box { background: var(--preview-bg); border: 1px solid var(--preview-border); border-radius: 8px; padding: 20px; font-family: monospace; font-size: 12.5px; line-height: 1.75; white-space: pre-wrap; max-height: 500px; overflow-y: auto; color: var(--text); }

  .stButton > button { border-radius: 6px !important; font-weight: 500 !important; }
  [data-testid="baseButton-secondary"]:hover,
  [data-testid="baseButton-secondaryFormSubmit"]:hover,
  [data-testid="stSidebar"] .stButton > button:not([data-testid="baseButton-primary"]):hover,
  [data-testid="stSidebar"] .stFormSubmitButton > button:hover {
    background: var(--btn-hover-bg) !important;
    border-color: var(--btn-hover-bg) !important;
    color: var(--btn-hover-text) !important;
  }
  [data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
  }
  [data-testid="stSidebar"] [data-testid="stSpinner"] * {
    color: var(--text) !important;
    border-top-color: var(--text) !important;
  }
  .test-ok {
    background: #14532d; color: #bbf7d0;
    border: 1px solid #16a34a;
    padding: 8px 12px; border-radius: 6px;
    font-size: 12.5px; line-height: 1.4; word-break: break-word;
  }
  .test-error {
    background: #7f1d1d; color: #fecaca;
    border: 1px solid #dc2626;
    padding: 8px 12px; border-radius: 6px;
    font-size: 12.5px; line-height: 1.4; word-break: break-word;
  }
  div[data-testid="stDownloadButton"] > button { width: 100% !important; }


  [data-testid="stSidebar"] .stSelectbox,
  [data-testid="stSidebar"] .stTextInput,
  [data-testid="stSidebar"] .stMarkdown p { margin-bottom: 0px !important; }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { gap: 0px !important; }
  [data-testid="stSidebar"] .block-container { gap: 0px !important; }

  [data-testid="stSidebar"] [data-testid="InputInstructions"],
  [data-testid="stSidebar"] [data-testid="stTextInput"] small { display: none !important; }

  .model-hint { font-size: 11px; color: var(--text-muted); line-height: 1.4; }
  [data-testid="stSidebar"] .stMarkdown:has(.model-hint) { margin-top: -14px !important; margin-bottom: 16px !important; }
  .model-hint a { color: #5B8EF5; text-decoration: none; }
  .model-hint a:hover { text-decoration: underline; }

  /* ── file cards ──────────────────────────────────────────────────────────── */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card-bg) !important;
    border-color: var(--card-border) !important;
    margin-bottom: 6px !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 6px 12px !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"],
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding-bottom: 0 !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 6px !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] button {
    height: 30px !important;
    min-height: unset !important;
    padding: 0 10px !important;
    font-size: 12px !important;
    line-height: 1 !important;
  }
  /* delete = last column of the outer row in each card */
  [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button {
    background: #DC2626 !important;
    color: #fff !important;
    border-color: transparent !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:hover {
    background: #B91C1C !important;
  }
</style>
"""


def inject_styles(theme: str) -> None:
    """Inject theme variables and global CSS into the page."""
    st.markdown(f"<style>{THEME_CSS[theme]}</style>", unsafe_allow_html=True)
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
