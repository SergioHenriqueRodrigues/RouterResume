import json
import urllib.error
import urllib.request

import streamlit as st

from generate import validate_api_key, mask_api_key


def render_tab_test_key(api_key: str, model: str, T: dict) -> None:
    st.markdown(f"### {T['test_key_title']}")

    key_to_use = api_key or st.session_state.get("api_key", "")

    if not key_to_use:
        st.warning(T["test_key_no_key"])
        return

    st.info(f"`{mask_api_key(key_to_use)}`")

    if not validate_api_key(key_to_use):
        st.error(T["api_key_invalid"])
        return

    if st.button(T["test_key_btn"], type="primary", icon=":material/wifi_tethering:"):
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Say 'OK'"}],
            "max_tokens": 10,
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key_to_use}",
                "Content-Type": "application/json",
            },
        )

        with st.spinner(T["test_key_testing"]):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                    reply = data["choices"][0]["message"]["content"]
                    st.success(T["test_key_ok"].format(reply=reply))
            except urllib.error.HTTPError as e:
                body = e.read().decode()
                try:
                    detail = json.loads(body).get("error", {}).get("message", body)
                except Exception:
                    detail = body
                if e.code in (401, 403):
                    st.error(T["test_key_err_key"].format(code=e.code, detail=detail))
                elif e.code == 402:
                    st.error(T["test_key_err_credits"].format(detail=detail))
                elif e.code == 404:
                    st.error(T["test_key_err_model"].format(model=model, detail=detail))
                elif e.code == 429:
                    st.warning(T["test_key_err_ratelimit"].format(detail=detail))
                else:
                    st.error(T["test_key_fail"].format(code=e.code, detail=detail))
            except Exception as e:
                st.error(T["test_key_fail"].format(code="?", detail=str(e)))
