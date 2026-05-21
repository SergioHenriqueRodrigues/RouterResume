from supabase_client import get_supabase


def get_profile(user_id: str) -> dict:
    try:
        res = (
            get_supabase()
            .table("profiles")
            .select("data_md,openrouter_key,ai_model,ui_lang,ui_theme")
            .eq("id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {}
    except Exception:
        res = (
            get_supabase()
            .table("profiles")
            .select("data_md,openrouter_key,ai_model")
            .eq("id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {}


def get_profile_data(user_id: str) -> str:
    return get_profile(user_id).get("data_md", "")


def save_profile_data(user_id: str, data_md: str) -> None:
    get_supabase().table("profiles").upsert({
        "id": user_id,
        "data_md": data_md,
        "updated_at": "now()",
    }).execute()


def save_api_settings(user_id: str, openrouter_key: str, ai_model: str) -> None:
    get_supabase().table("profiles").upsert({
        "id": user_id,
        "openrouter_key": openrouter_key,
        "ai_model": ai_model,
        "updated_at": "now()",
    }).execute()


def save_ui_preferences(user_id: str, ui_lang: str, ui_theme: str) -> None:
    get_supabase().table("profiles").upsert({
        "id": user_id,
        "ui_lang": ui_lang,
        "ui_theme": ui_theme,
        "updated_at": "now()",
    }).execute()
