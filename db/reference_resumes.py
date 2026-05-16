import base64
import io
from pathlib import Path

from supabase_client import get_supabase


def _extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext in {".md", ".txt"}:
        return content.decode("utf-8", errors="ignore")
    if ext == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except Exception:
            return ""
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    return ""


def upload_reference_resume(user_id: str, filename: str, content: bytes) -> None:
    get_supabase().table("reference_resumes").insert({
        "user_id": user_id,
        "filename": filename,
        "file_size": len(content),
        "file_content": base64.b64encode(content).decode(),
        "file_text": _extract_text(filename, content),
    }).execute()


def get_reference_resumes(user_id: str) -> list[dict]:
    res = (
        get_supabase()
        .table("reference_resumes")
        .select("id,filename,file_size,file_text,created_at")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return res.data or []


def get_reference_resume_bytes(resume_id: str) -> bytes:
    res = (
        get_supabase()
        .table("reference_resumes")
        .select("file_content")
        .eq("id", resume_id)
        .execute()
    )
    return base64.b64decode(res.data[0]["file_content"]) if res.data else b""


def delete_reference_resume(resume_id: str) -> None:
    get_supabase().table("reference_resumes").delete().eq("id", resume_id).execute()
