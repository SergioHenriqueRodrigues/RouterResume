import base64
import re
from datetime import datetime

import streamlit as st

from generate import OUTPUT_DIR
from ui.components import render_file_card
from ui.auth import _queue_toast, _flush_toast
from db.generations import get_generations, get_generation_files, delete_generation

_ALLOWED = {".pdf", ".docx"}
_MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}
_PAGE_SIZE = 10


def _parse_stem(stem: str) -> tuple[str, str]:
    m = re.search(r"(\d{8})_(\d{4})", stem)
    if m:
        raw_name = stem[: m.start()].rstrip("_").replace("_", " ").title() or stem
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
            return raw_name, dt.strftime("%d/%m/%Y  %H:%M")
        except ValueError:
            pass
    return stem, ""


@st.fragment
def _render_cloud_history(T: dict) -> None:
    _flush_toast()
    user = st.session_state["user"]
    confirming_id = st.session_state.pop("_confirm_del_id", None)

    if "history_rows" not in st.session_state:
        try:
            st.session_state["history_rows"] = get_generations(user.id)
        except Exception:
            _queue_toast(T["error_load"], "error")
            _flush_toast()
            return

    rows = st.session_state["history_rows"]

    if not rows:
        st.info(T["history_empty"])
        return

    search = st.text_input(
        "search",
        placeholder=T["history_search_placeholder"],
        label_visibility="collapsed",
        key="history_cloud_search",
    )

    if search:
        q = search.lower()
        rows_to_show = [r for r in rows if q in (r.get("filename") or "").lower()]
        total = len(rows_to_show)
    else:
        page = st.session_state.get("history_cloud_page", 1)
        rows_to_show = rows[:page * _PAGE_SIZE]
        total = len(rows)

    if not total:
        st.info(T["history_empty"])
        return

    for row in rows_to_show:
        gen_id   = row["id"]
        filename = row.get("filename") or "resume"
        model    = row.get("model") or ""
        created  = row.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = dt.strftime("%d/%m/%Y  %H:%M")
        except Exception:
            date_str = created[:16] if created else ""

        display_name, _ = _parse_stem(filename)
        subtitle = f"{date_str} · {model}" if model else date_str

        with st.container(border=True):
            if confirming_id == gen_id:
                st.warning(T["history_confirm_delete"])
                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    if st.button(T["history_confirm_yes"], key=f"conf_yes_{gen_id}", type="primary", use_container_width=True):
                        try:
                            delete_generation(gen_id)
                            st.session_state["history_rows"] = [
                                r for r in st.session_state["history_rows"] if r["id"] != gen_id
                            ]
                        except Exception:
                            _queue_toast(T["error_delete"], "error")
                        st.rerun(scope="fragment")
                with c2:
                    if st.button(T["history_confirm_no"], key=f"conf_no_{gen_id}", use_container_width=True):
                        st.rerun(scope="fragment")
            else:
                col_info, col_dl, col_del = st.columns([5, 2, 1])

                with col_info:
                    st.markdown(
                        f'<p style="margin:0;line-height:1.35">'
                        f'<span class="file-name">{display_name}</span>'
                        f'<span class="file-size" style="margin-left:6px">· {subtitle}</span>'
                        f'</p>',
                        unsafe_allow_html=True,
                    )

                with col_dl:
                    try:
                        files_data = get_generation_files(gen_id)
                    except Exception:
                        files_data = {}

                    btns = []
                    if files_data.get("file_docx"):
                        btns.append(("DOCX", base64.b64decode(files_data["file_docx"]), "docx"))
                    if files_data.get("file_pdf"):
                        btns.append(("PDF", base64.b64decode(files_data["file_pdf"]), "pdf"))

                    if btns:
                        dl_cols = st.columns(len(btns))
                        for bc, (label, data, ext) in zip(dl_cols, btns):
                            with bc:
                                st.download_button(
                                    label=label,
                                    data=data,
                                    file_name=f"{filename}.{ext}",
                                    mime=_MIME[ext],
                                    use_container_width=True,
                                    key=f"dl_{gen_id}_{ext}",
                                )

                with col_del:
                    if st.button("", key=f"del_{gen_id}", icon=":material/delete:", help=T["history_delete_help"]):
                        st.session_state["_confirm_del_id"] = gen_id
                        st.rerun(scope="fragment")

    shown = len(rows_to_show)
    if not search and total > _PAGE_SIZE:
        st.caption(T["history_showing"].format(shown=shown, total=total))
        if page * _PAGE_SIZE < total:
            remaining = total - shown
            if st.button(T["history_load_more"].format(n=remaining), use_container_width=True):
                st.session_state["history_cloud_page"] = page + 1
                st.rerun(scope="fragment")


@st.fragment
def _render_local_history(T: dict) -> None:
    if not OUTPUT_DIR.exists():
        st.info(T["history_empty"])
        return

    files = [
        f for f in OUTPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in _ALLOWED
    ]

    if not files:
        st.info(T["history_empty"])
        return

    groups: dict[str, list] = {}
    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
        groups.setdefault(f.stem, []).append(f)

    search = st.text_input(
        "search",
        placeholder=T["history_search_placeholder"],
        label_visibility="collapsed",
        key="history_local_search",
    )

    if search:
        q = search.lower()
        groups = {stem: fs for stem, fs in groups.items() if q in stem.lower()}
        items_to_show = list(groups.items())
    else:
        total = len(groups)
        page = st.session_state.get("history_local_page", 1)
        items_to_show = list(groups.items())[:page * _PAGE_SIZE]

    if not groups:
        st.info(T["history_empty"])
        return

    confirming_stem = st.session_state.get("_confirm_del_stem")

    for stem, group_files in items_to_show:
        name, date_str = _parse_stem(stem)
        if confirming_stem == stem:
            with st.container(border=True):
                st.warning(T["history_confirm_delete"])
                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    if st.button(T["history_confirm_yes"], key=f"conf_yes_{stem}", type="primary", use_container_width=True):
                        for f in group_files:
                            try:
                                if f.exists():
                                    f.unlink()
                            except Exception:
                                _queue_toast(T["error_delete"], "error")
                        st.session_state.pop("_confirm_del_stem", None)
                        st.rerun(scope="fragment")
                with c2:
                    if st.button(T["history_confirm_no"], key=f"conf_no_{stem}", use_container_width=True):
                        st.session_state.pop("_confirm_del_stem", None)
                        st.rerun(scope="fragment")
        else:
            if render_file_card(
                display_name=name,
                subtitle=date_str,
                download_files=group_files,
                delete_key=f"del_{stem}",
                delete_help=T["history_delete_help"],
            ):
                st.session_state["_confirm_del_stem"] = stem
                st.rerun(scope="fragment")

    if not search and total > _PAGE_SIZE:
        shown = len(items_to_show)
        st.caption(T["history_showing"].format(shown=shown, total=total))
        if page * _PAGE_SIZE < total:
            remaining = total - shown
            if st.button(T["history_load_more"].format(n=remaining), use_container_width=True):
                st.session_state["history_local_page"] = page + 1
                st.rerun(scope="fragment")


def render_tab_history(T: dict) -> None:
    st.markdown(f"### {T['history_title']}")
    if st.session_state.get("user"):
        _render_cloud_history(T)
    else:
        _render_local_history(T)
