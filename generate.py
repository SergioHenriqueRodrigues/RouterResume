#!/usr/bin/env python3
import os, sys, json, argparse, datetime, textwrap, urllib.request, urllib.error
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_OK = True
except ImportError:
    PDF_OK = False

BASE_DIR       = Path(__file__).parent
DATA_MD        = BASE_DIR / "data.md"
OLD_RESUMES_DIR = BASE_DIR / "old_resumes"
OUTPUT_DIR     = BASE_DIR / "output"
MODEL          = "inclusionai/ling-2.6-1t:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OUTPUT_DIR.mkdir(exist_ok=True)

def read_data_md():
    if not DATA_MD.exists():
        print("WARNING: data.md not found.")
        return ""
    return DATA_MD.read_text(encoding="utf-8")

def read_old_resumes():
    if not OLD_RESUMES_DIR.exists():
        return ""
    parts = []
    for file in sorted(OLD_RESUMES_DIR.iterdir()):
        if file.suffix.lower() not in {".md", ".txt", ".pdf", ".docx"}:
            continue
        content = ""
        if file.suffix.lower() in {".md", ".txt"}:
            content = file.read_text(encoding="utf-8", errors="ignore")
        elif file.suffix.lower() == ".pdf":
            content = _read_pdf(file)
        elif file.suffix.lower() == ".docx":
            content = _read_docx(file)
        if content.strip():
            parts.append(f"[Resume: {file.name}]\n{content}")
    return "\n\n---\n\n".join(parts)

def _read_pdf(path):
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except ImportError:
        pass
    print(f"  WARNING: install pdfplumber to read {path.name}")
    return ""

def _read_docx(path):
    if not DOCX_OK:
        return ""
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

def build_prompt(raw_data, resumes, job_description, language):
    section_resumes = f"\n=== OLD RESUMES ===\n{resumes}\n" if resumes.strip() else ""
    return f"""You are an expert in recruitment and ATS resume optimization.

Candidate raw data (may be disorganized):

=== RAW DATA ===
{raw_data}
{section_resumes}
=== JOB DESCRIPTION ===
{job_description}

Language: {language}

Instructions:
1. Extract name, contact info, experiences, education, skills, achievements
2. Ignore duplicates and items irrelevant to this job
3. Professional summary focused on what the job requires (3-4 lines)
4. Use EXACTLY the keywords from the job description (crucial for ATS)
5. Quantify achievements whenever possible
6. Maximum 1-2 pages

Respond ONLY with the formatted resume, no explanations, no code blocks, no extra markdown.
Use this exact format:

NAME: [full name]
CONTACT: [email] | [phone] | [linkedin] | [city]

## PROFESSIONAL SUMMARY
[paragraph]

## WORK EXPERIENCE

### [Title] - [Company] | [Period]
- [achievement]
- [achievement]

## EDUCATION

### [Degree] - [Institution] | [Year]

## SKILLS
[list]
"""

def call_model(prompt, model):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set.")
        print('  setx OPENROUTER_API_KEY "sk-or-..."')
        sys.exit(1)
    print(f"Calling OpenRouter ({model})...")
    payload = json.dumps({
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL, data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://resume-ats-local",
            "X-Title": "ATS Resume Generator",
        }, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"API ERROR ({e.code}): {e.read().decode('utf-8')}")
        sys.exit(1)
    try:
        content = data["choices"][0]["message"]["content"]
        if not content:
            print("ERROR: model returned empty. Try another --model")
            sys.exit(1)
        # Remove code blocks if the model puts them
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()
        return content
    except (KeyError, IndexError):
        print(f"ERROR unexpected response: {json.dumps(data, indent=2)}")
        sys.exit(1)

def save_md(text, base_name):
    path = OUTPUT_DIR / f"{base_name}.md"
    path.write_text(text, encoding="utf-8")
    return path

def save_docx(text, base_name):
    if not DOCX_OK:
        print("  WARNING: run: pip install python-docx")
        return None
    path = OUTPUT_DIR / f"{base_name}.docx"
    doc = Document()
    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)
    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith("NAME:"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line.replace("NAME:", "").strip())
            run.bold = True; run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
        elif line.startswith("CONTACT:"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line.replace("CONTACT:", "").strip())
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            doc.add_paragraph()
        elif line.startswith("## "):
            p = doc.add_paragraph()
            run = p.add_run(line[3:].strip().upper())
            run.bold = True; run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x2E, 0x86, 0xAB)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after  = Pt(2)
            p2 = doc.add_paragraph()
            run2 = p2.add_run("-" * 60)
            run2.font.size = Pt(7)
            run2.font.color.rgb = RGBColor(0x2E, 0x86, 0xAB)
            p2.paragraph_format.space_after = Pt(4)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            run = p.add_run(line[4:].strip())
            run.bold = True; run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after  = Pt(1)
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(line[2:].strip())
            run.font.size = Pt(9.5)
        elif not line:
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        else:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.size = Pt(9.5)
            p.paragraph_format.space_after = Pt(2)
    doc.save(str(path))
    return path

def save_pdf(text, base_name):
    if not PDF_OK:
        print("  WARNING: run: pip install reportlab")
        return None
    path = OUTPUT_DIR / f"{base_name}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    color_p = colors.HexColor("#2E86AB")
    color_t = colors.HexColor("#1A1A2E")
    color_s = colors.HexColor("#555555")
    s_name    = ParagraphStyle("Name",    parent=styles["Title"],   fontSize=20, textColor=color_t, spaceAfter=2,   alignment=1, fontName="Helvetica-Bold")
    s_contact = ParagraphStyle("Contact", parent=styles["Normal"],  fontSize=9,  textColor=color_s, spaceAfter=12,  alignment=1, fontName="Helvetica")
    s_section = ParagraphStyle("Section",   parent=styles["Heading2"],fontSize=10, textColor=color_p, spaceBefore=12, spaceAfter=2, fontName="Helvetica-Bold")
    s_sub     = ParagraphStyle("Sub",     parent=styles["Normal"],  fontSize=10, textColor=color_t, spaceBefore=6,  spaceAfter=1, fontName="Helvetica-Bold")
    s_bullet  = ParagraphStyle("Bullet",  parent=styles["Normal"],  fontSize=9.5,textColor=color_t, leftIndent=12,  spaceAfter=2, fontName="Helvetica")
    s_normal  = ParagraphStyle("Normal2", parent=styles["Normal"],  fontSize=9.5,textColor=color_t, spaceAfter=2,   fontName="Helvetica")
    story = []
    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith("NAME:"):
            story.append(Paragraph(line.replace("NAME:", "").strip(), s_name))
        elif line.startswith("CONTACT:"):
            story.append(Paragraph(line.replace("CONTACT:", "").strip(), s_contact))
        elif line.startswith("## "):
            story.append(HRFlowable(width="100%", thickness=1, color=color_p, spaceAfter=2))
            story.append(Paragraph(line[3:].strip(), s_section))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), s_sub))
        elif line.startswith("- ") or line.startswith("* "):
            story.append(Paragraph("- " + line[2:].strip(), s_bullet))
        elif not line:
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(line, s_normal))
    doc.build(story)
    return path

def main():
    parser = argparse.ArgumentParser(description="ATS Resume Generator")
    parser.add_argument("--job",       help=".txt file with job description")
    parser.add_argument("--language",  default="English")
    parser.add_argument("--format", choices=["md", "docx", "pdf", "all"], default="docx")
    parser.add_argument("--model",     default=MODEL)
    args = parser.parse_args()

    print("\nATS Resume Generator")
    print("-" * 40)

    raw_data = read_data_md()
    print(f"Reading {DATA_MD.name}... OK")

    resumes = read_old_resumes()
    n = resumes.count("[Resume:")
    print(f"Old resumes: {n} file(s)")

    if args.job:
        job_path = Path(args.job)
        if not job_path.exists():
            print(f"ERROR: {args.job} not found")
            sys.exit(1)
        job_description = job_path.read_text(encoding="utf-8")
        print(f"Job description: {args.job}")
    else:
        print("\nPaste the job description. Finish with Enter + Ctrl+Z (Windows) or Ctrl+D (Unix):\n")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        job_description = "\n".join(lines).strip()
        if not job_description:
            print("ERROR: no job description provided.")
            sys.exit(1)

    prompt    = build_prompt(raw_data, resumes, job_description, args.language)
    resume    = call_model(prompt, args.model)

    ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    base_name = f"ats_resume_{ts}"

    print(f"\nSaving to output/...")

    if args.format in ("md", "all"):
        p = save_md(resume, base_name)
        print(f"  OK: {p.name}")

    if args.format in ("docx", "all"):
        p = save_docx(resume, base_name)
        if p: print(f"  OK: {p.name}")

    if args.format in ("pdf", "all"):
        p = save_pdf(resume, base_name)
        if p: print(f"  OK: {p.name}")

    print(f"\nFiles in: {OUTPUT_DIR}")
    print("-" * 40)
    print("\nPreview:\n")
    print(textwrap.indent(resume[:600] + ("..." if len(resume) > 600 else ""), "  "))
    print()

if __name__ == "__main__":
    main()