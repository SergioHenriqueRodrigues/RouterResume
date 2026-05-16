import base64
from pathlib import Path

from supabase_client import get_supabase


def save_generation(
    user_id: str,
    job_description: str,
    resume_text: str,
    model: str,
    filename: str,
    saved_paths: list[Path],
) -> None:
    file_docx = file_pdf = None
    for p in saved_paths:
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            if p.suffix == ".docx":
                file_docx = b64
            elif p.suffix == ".pdf":
                file_pdf = b64

    get_supabase().table("generations").insert({
        "user_id": user_id,
        "job_description": job_description,
        "resume_text": resume_text,
        "model": model,
        "filename": filename,
        "file_docx": file_docx,
        "file_pdf": file_pdf,
    }).execute()


def get_generations(user_id: str) -> list[dict]:
    res = (
        get_supabase()
        .table("generations")
        .select("id,filename,model,created_at,job_description")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_generation_files(gen_id: str) -> dict:
    res = (
        get_supabase()
        .table("generations")
        .select("filename,file_docx,file_pdf,resume_text")
        .eq("id", gen_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def delete_generation(gen_id: str) -> None:
    get_supabase().table("generations").delete().eq("id", gen_id).execute()
