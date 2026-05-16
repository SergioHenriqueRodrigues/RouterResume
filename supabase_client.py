import os
from supabase import create_client, Client

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL e SUPABASE_KEY não configurados")
        _client = create_client(url, key)
    return _client


def restore_session(access_token: str, refresh_token: str) -> bool:
    try:
        get_supabase().auth.set_session(access_token, refresh_token)
        return True
    except Exception:
        return False
