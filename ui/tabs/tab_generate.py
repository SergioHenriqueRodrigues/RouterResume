import base64
import datetime
import os
import re
import threading
import time
import unicodedata

import streamlit as st
import streamlit.components.v1 as components

from generate import (
    read_data_md, read_old_resumes,
    build_prompt, call_model, save_docx, save_pdf,
    validate_job_description,
    OUTPUT_DIR,
)


_GENERIC_LINE = re.compile(
    r"^(about|sobre|acerca\s+de|job\s+desc|descri[çc][aã]o|description|"
    r"responsibilities|responsabilidades|requirements|requisitos|"
    r"overview|sum[aá]rio|summary|oferta|puesto|vaga|cargo|role|position|"
    r"we\s+are|we'?re|our\s+team|nossa\s+empresa|nuestra\s+empresa)",
    re.IGNORECASE,
)

def _job_slug(job_text: str) -> str:
    for raw in job_text.splitlines():
        line = re.sub(r"[#*_`|]", "", raw).strip()  # strip markdown
        if not line or _GENERIC_LINE.match(line) or len(line) > 80:
            continue
        normalized = unicodedata.normalize("NFKD", line.lower())
        ascii_str  = normalized.encode("ascii", "ignore").decode("ascii")
        slug       = re.sub(r"[^\w\s]", "", ascii_str)
        slug       = re.sub(r"\s+", "_", slug).strip("_")
        return slug[:40] or "resume"
    return "resume"


def render_tab_generate(lang: str, fmt: str, model: str, api_key: str, T: dict) -> None:
    raw_data         = read_data_md()
    old_resumes_text = read_old_resumes()
    n_resumes        = old_resumes_text.count("[Resume:")

    has_data     = bool(raw_data.strip())
    has_resumes  = n_resumes > 0
    can_generate = has_data and bool(model)

    is_generating = st.session_state.get("is_generating", False)

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
        st.info(T["no_resumes_hint"])

    col1, col2, _ = st.columns([2, 1, 1])
    with col1:
        generate_btn = st.button(
            T["generate_btn"],
            type="primary",
            use_container_width=True,
            disabled=not can_generate or is_generating,
            icon=":material/rocket_launch:",
        )
    with col2:
        cancel_btn = st.button(
            T["cancel_btn"],
            use_container_width=True,
            disabled=not is_generating,
            icon=":material/cancel:",
        )

    if cancel_btn:
        st.session_state["is_generating"] = False
        st.session_state.pop("pending_job", None)
        st.session_state.pop("pending_key", None)
        st.rerun()

    if generate_btn and not is_generating:
        valid, err_key = validate_job_description(job)
        if not valid:
            st.error(T[err_key])
        else:
            resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
            if not resolved_key:
                st.error(T["no_api_key_error"])
            else:
                st.session_state["is_generating"] = True
                st.session_state["pending_job"]   = job.strip()
                st.session_state["pending_key"]   = resolved_key
                st.session_state.pop("generation_error", None)
                st.rerun()

    # ── error from previous generation ────────────────────────────────────────
    if st.session_state.get("generation_error"):
        st.error(st.session_state["generation_error"])

    # ── run generation after rerun (button is already disabled) ───────────────
    if is_generating and "pending_job" in st.session_state:
        resolved_key = st.session_state.pop("pending_key", "")
        job_text     = st.session_state.pop("pending_job", "")
        os.environ["OPENROUTER_API_KEY"] = resolved_key

        with st.status(T["status_generating"], expanded=True) as status:
            st.write(T["status_reading"].format(chars=len(raw_data)))
            st.write(T["status_resumes"].format(n=n_resumes))

            try:
                prompt = build_prompt(raw_data, old_resumes_text, job_text, lang)
                start  = time.time()

                _result: list = [None]
                _error:  list = [None]

                def _run():
                    try:
                        _result[0] = call_model(prompt, model)
                    except Exception as exc:
                        _error[0] = exc

                _thread = threading.Thread(target=_run, daemon=True)
                _thread.start()

                progress = st.progress(0, text=T["status_calling"].format(model=model))
                _fake = 0.0
                while _thread.is_alive():
                    time.sleep(0.35)
                    if _fake < 25:
                        _fake += 2.2
                    elif _fake < 60:
                        _fake += 0.9
                    elif _fake < 78:
                        _fake += 0.45
                    elif _fake < 88:
                        _fake += 0.22
                    else:
                        _fake += 0.12
                    progress.progress(min(int(_fake), 95), text=T["status_calling"].format(model=model))

                _thread.join()
                if _error[0]:
                    raise _error[0]

                elapsed = round(time.time() - start)
                progress.progress(100, text=T["status_elapsed"].format(secs=elapsed))
                resume  = _result[0]

                ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                base_name = f"{_job_slug(job_text)}_{ts}"

                saved_paths = []
                if fmt in ("docx", "all"):
                    p = save_docx(resume, base_name, lang)
                    if p:
                        saved_paths.append(p)
                if fmt in ("pdf", "all"):
                    p = save_pdf(resume, base_name, lang)
                    if p:
                        saved_paths.append(p)

                st.session_state["is_generating"] = False
                st.session_state["resume_text"]   = resume
                st.session_state["saved_paths"]   = saved_paths
                st.rerun()

            except Exception as e:
                st.session_state["is_generating"] = False
                st.session_state["generation_error"] = f"{T['error_prefix']}{e}"
                st.rerun()

    # ── download buttons ───────────────────────────────────────────────────────
    if st.session_state.get("saved_paths"):
        all_paths = st.session_state["saved_paths"]
        existing  = [p for p in all_paths if p.exists()]
        deleted   = [p for p in all_paths if not p.exists()]

        st.markdown("---")
        st.markdown(T["download_title"])

        if deleted and not existing:
            st.warning(T["download_deleted"])
        else:
            if deleted:
                st.warning(T["download_deleted"])
            dl_cols = st.columns(len(existing))
            for col, path in zip(dl_cols, existing):
                with col:
                    mime = (
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        if path.suffix == ".docx"
                        else "application/pdf"
                    )
                    st.download_button(
                        label=path.name,
                        data=path.read_bytes(),
                        file_name=path.name,
                        mime=mime,
                        use_container_width=True,
                        icon=":material/download:",
                    )

    # ── preview ────────────────────────────────────────────────────────────────
    if "resume_text" in st.session_state:
        with st.expander(T["preview_title"], expanded=True):
            pdf_paths = [
                p for p in st.session_state.get("saved_paths", [])
                if p.suffix == ".pdf" and p.exists()
            ]
            if pdf_paths:
                b64 = base64.b64encode(pdf_paths[0].read_bytes()).decode()
                components.html(
                    f"""
                    <iframe id="pdf-frame" width="100%" height="900"
                        style="border:none;border-radius:8px;"></iframe>
                    <script>
                    (function(){{
                        var b64="{b64}";
                        var bin=atob(b64);
                        var buf=new Uint8Array(bin.length);
                        for(var i=0;i<bin.length;i++) buf[i]=bin.charCodeAt(i);
                        var blob=new Blob([buf],{{type:"application/pdf"}});
                        document.getElementById("pdf-frame").src=URL.createObjectURL(blob);
                    }})();
                    </script>
                    """,
                    height=920,
                )
            else:
                st.caption(T["preview_caption"])
                st.markdown(
                    f'<div class="preview-box">{st.session_state["resume_text"]}</div>',
                    unsafe_allow_html=True,
                )
