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


def restore_session(access_token: str, refresh_token: str):
    """Returns (user, access_token, refresh_token) on success, None on failure."""
    try:
        res = get_supabase().auth.set_session(access_token, refresh_token)
        if res and res.user and res.session:
            return res.user, res.session.access_token, res.session.refresh_token
    except Exception:
        pass
    # Access token may be expired — try refreshing with refresh token
    try:
        res = get_supabase().auth.refresh_session(refresh_token)
        if res and res.user and res.session:
            return res.user, res.session.access_token, res.session.refresh_token
    except Exception:
        pass
    return None
