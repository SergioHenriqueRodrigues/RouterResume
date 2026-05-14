import os
import datetime

import streamlit as st

from generate import (
    read_data_md, read_old_resumes,
    build_prompt, call_model, save_docx, save_pdf,
    OUTPUT_DIR,
)


def render_tab_generate(lang: str, fmt: str, model: str, api_key: str, T: dict) -> None:
    """Render the Generate tab."""

    raw_data         = read_data_md()
    old_resumes_text = read_old_resumes()
    n_resumes        = old_resumes_text.count("[Resume:")

    has_data    = bool(raw_data.strip())
    has_resumes = n_resumes > 0
    can_generate = has_data and has_resumes

    st.markdown(f"### {T['job_label']}")
    job = st.text_area(
        label="job",
        placeholder=T["job_placeholder"],
        height=260,
        label_visibility="collapsed",
    )

    if not has_data and not has_resumes:
        st.warning(T["no_data_and_resumes_error"])
    elif not has_data:
        st.warning(T["no_data_error"])
    elif not has_resumes:
        st.warning(T["no_resumes_error"])

    col1, _, _ = st.columns([2, 1, 1])
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
        else:
            resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
            if not resolved_key:
                st.error(T["no_api_key_error"])
            else:
                os.environ["OPENROUTER_API_KEY"] = resolved_key
                with st.status(T["status_generating"], expanded=True) as status:
                    st.write(T["status_reading"].format(chars=len(raw_data)))
                    st.write(T["status_resumes"].format(n=n_resumes))
                    st.write(T["status_calling"].format(model=model))
    
                    try:
                        prompt = build_prompt(raw_data, old_resumes_text, job.strip(), lang)
                        ui_stub = {
                            "calling_api":      "Calling",
                            "api_key_error":    "",
                            "api_key_hint":     "",
                            "api_key_hint2":    "",
                            "api_error":        "API error",
                            "api_empty":        "Empty response",
                            "api_unexpected":   "Unexpected response",
                        }
                        resume = call_model(prompt, model, ui_stub)
    
                        ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                        base_name = f"routerresume_{ts}"
                        ui_doc    = {
                            "docx_missing": "python-docx not installed",
                            "pdf_missing":  "reportlab not installed",
                        }
    
                        saved_paths = []
                        if fmt in ("docx", "all"):
                            p = save_docx(resume, base_name, lang, ui_doc)
                            if p:
                                saved_paths.append(p)
                        if fmt in ("pdf", "all"):
                            p = save_pdf(resume, base_name, lang, ui_doc)
                            if p:
                                saved_paths.append(p)
    
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
    
    # ── download buttons ───────────────────────────────────────────────────────
    if st.session_state.get("saved_paths"):
        st.markdown("---")
        st.markdown(T["download_title"])
        dl_cols = st.columns(len(st.session_state["saved_paths"]))
        for col, path in zip(dl_cols, st.session_state["saved_paths"]):
            with col:
                mime = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if path.suffix == ".docx"
                    else "application/pdf"
                )
                st.download_button(
                    label=f"⬇ {path.name}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime=mime,
                    use_container_width=True,
                )

    # ── preview ────────────────────────────────────────────────────────────────
    if "resume_text" in st.session_state:
        with st.expander(T["preview_title"], expanded=True):
            st.markdown(
                f'<div class="preview-box">{st.session_state["resume_text"]}</div>',
                unsafe_allow_html=True,
            )
