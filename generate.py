#!/usr/bin/env python3
import os, sys, json, datetime, textwrap, urllib.request, urllib.error
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

BASE_DIR        = Path(__file__).parent
DATA_MD         = BASE_DIR / "data.md"
OLD_RESUMES_DIR = BASE_DIR / "old_resumes"
OUTPUT_DIR      = BASE_DIR / "output"
MODEL           = "inclusionai/ling-2.6-1t:free"
OPENROUTER_URL  = "https://openrouter.ai/api/v1/chat/completions"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── language config ────────────────────────────────────────────────────────────

LANGUAGES = {
    "1": {
        "name": "Portuguese (Brazil)",
        "resume_headers": {
            "name":       "NOME",
            "contact":    "CONTATO",
            "summary":    "RESUMO PROFISSIONAL",
            "experience": "EXPERIÊNCIA PROFISSIONAL",
            "education":  "FORMAÇÃO ACADÊMICA",
            "skills":     "HABILIDADES",
        },
        "ui": {
            "title":               "GERADOR DE CURRÍCULO ATS",
            "reading_profile":     "📄 Lendo seus dados...",
            "data_loaded":         "✓ data.md carregado",
            "data_empty":          "✗ data.md está vazio ou não encontrado — adicione seus dados lá!",
            "resumes_found":       "arquivo(s) encontrado(s) em old_resumes/",
            "job_question":        "📋 Descrição da vaga — onde está?",
            "job_opt1":            "Tenho um arquivo (job_description.txt)",
            "job_opt2":            "Vou colar agora",
            "job_not_found":       "ERRO: job_description.txt não encontrado na pasta do projeto.",
            "job_loaded":          "✓ job_description.txt carregado",
            "job_paste":           "Cole a descrição completa da vaga abaixo:",
            "job_received":        "✓ Descrição da vaga recebida",
            "job_empty":           "ERRO: nenhuma descrição de vaga fornecida.",
            "resume_lang":         "🌐 Idioma do currículo:",
            "resume_lang_opt1":    "Português (Brasil)",
            "resume_lang_opt2":    "Inglês",
            "resume_lang_opt3":    "Espanhol",
            "resume_lang_ok":      "✓ Idioma do currículo",
            "format_question":     "💾 Formato de saída:",
            "format_opt1":         "DOCX (Word)",
            "format_opt2":         "PDF",
            "format_opt3":         "Ambos (DOCX + PDF)",
            "format_ok":           "✓ Formato",
            "model_question":      "🤖 Modelo de IA:",
            "model_opt1":          f"Padrão ({MODEL})",
            "model_opt2":          "Digitar outro modelo",
            "model_custom_prompt": "Digite o ID do modelo (ex: google/gemini-2.5-flash-preview:free): ",
            "model_ok":            "✓ Modelo",
            "generating":          "🚀 Gerando seu currículo ATS...",
            "calling_api":         "Chamando OpenRouter",
            "saving":              "💾 Salvando arquivos...",
            "file_ok":             "✓",
            "done":                "✅ Pronto! Arquivos salvos em: output/",
            "preview":             "📄 Prévia:",
            "paste_end":           "(cole o texto e pressione Enter duas vezes para finalizar)",
            "api_key_error":       "ERRO: variável OPENROUTER_API_KEY não definida.",
            "api_key_hint":        'No Windows rode: setx OPENROUTER_API_KEY "sk-or-..."',
            "api_key_hint2":       "Depois feche e abra o terminal.",
            "api_error":           "ERRO na API",
            "api_empty":           "ERRO: modelo retornou resposta vazia. Tente outro modelo.",
            "api_unexpected":      "ERRO: resposta inesperada da API",
            "docx_missing":        "AVISO: python-docx não instalado. Rode: pip install python-docx",
            "pdf_missing":         "AVISO: reportlab não instalado. Rode: pip install reportlab",
            "choose":              "Escolha",
        }
    },
    "2": {
        "name": "English",
        "resume_headers": {
            "name":       "NAME",
            "contact":    "CONTACT",
            "summary":    "PROFESSIONAL SUMMARY",
            "experience": "WORK EXPERIENCE",
            "education":  "EDUCATION",
            "skills":     "SKILLS",
        },
        "ui": {
            "title":               "ATS RESUME GENERATOR",
            "reading_profile":     "📄 Reading your profile data...",
            "data_loaded":         "✓ data.md loaded",
            "data_empty":          "✗ data.md is empty or missing — add your info there!",
            "resumes_found":       "file(s) found in old_resumes/",
            "job_question":        "📋 Job description — where is it?",
            "job_opt1":            "I have a file (job_description.txt)",
            "job_opt2":            "I'll paste it now",
            "job_not_found":       "ERROR: job_description.txt not found in the project folder.",
            "job_loaded":          "✓ job_description.txt loaded",
            "job_paste":           "Paste the full job description below:",
            "job_received":        "✓ Job description received",
            "job_empty":           "ERROR: no job description provided.",
            "resume_lang":         "🌐 Resume language:",
            "resume_lang_opt1":    "Portuguese (Brazil)",
            "resume_lang_opt2":    "English",
            "resume_lang_opt3":    "Spanish",
            "resume_lang_ok":      "✓ Resume language",
            "format_question":     "💾 Output format:",
            "format_opt1":         "DOCX (Word)",
            "format_opt2":         "PDF",
            "format_opt3":         "Both (DOCX + PDF)",
            "format_ok":           "✓ Format",
            "model_question":      "🤖 AI model:",
            "model_opt1":          f"Default ({MODEL})",
            "model_opt2":          "Type a custom model ID",
            "model_custom_prompt": "Enter model ID (e.g. google/gemini-2.5-flash-preview:free): ",
            "model_ok":            "✓ Model",
            "generating":          "🚀 Generating your ATS resume...",
            "calling_api":         "Calling OpenRouter",
            "saving":              "💾 Saving files...",
            "file_ok":             "✓",
            "done":                "✅ Done! Files saved to: output/",
            "preview":             "📄 Preview:",
            "paste_end":           "(paste the text and press Enter twice when done)",
            "api_key_error":       "ERROR: OPENROUTER_API_KEY not set.",
            "api_key_hint":        'On Windows run: setx OPENROUTER_API_KEY "sk-or-..."',
            "api_key_hint2":       "Then close and reopen the terminal.",
            "api_error":           "API ERROR",
            "api_empty":           "ERROR: model returned empty. Try another model.",
            "api_unexpected":      "ERROR: unexpected API response",
            "docx_missing":        "WARNING: python-docx not installed. Run: pip install python-docx",
            "pdf_missing":         "WARNING: reportlab not installed. Run: pip install reportlab",
            "choose":              "Choose",
        }
    },
    "3": {
        "name": "Spanish",
        "resume_headers": {
            "name":       "NOMBRE",
            "contact":    "CONTACTO",
            "summary":    "RESUMEN PROFESIONAL",
            "experience": "EXPERIENCIA PROFESIONAL",
            "education":  "FORMACIÓN ACADÉMICA",
            "skills":     "HABILIDADES",
        },
        "ui": {
            "title":               "GENERADOR DE CURRÍCULUM ATS",
            "reading_profile":     "📄 Leyendo tus datos...",
            "data_loaded":         "✓ data.md cargado",
            "data_empty":          "✗ data.md está vacío o no encontrado — ¡agrega tu información allí!",
            "resumes_found":       "archivo(s) encontrado(s) en old_resumes/",
            "job_question":        "📋 Descripción del trabajo — ¿dónde está?",
            "job_opt1":            "Tengo un archivo (job_description.txt)",
            "job_opt2":            "Lo voy a pegar ahora",
            "job_not_found":       "ERROR: job_description.txt no encontrado en la carpeta del proyecto.",
            "job_loaded":          "✓ job_description.txt cargado",
            "job_paste":           "Pega la descripción completa del trabajo abajo:",
            "job_received":        "✓ Descripción del trabajo recibida",
            "job_empty":           "ERROR: no se proporcionó descripción del trabajo.",
            "resume_lang":         "🌐 Idioma del currículum:",
            "resume_lang_opt1":    "Portugués (Brasil)",
            "resume_lang_opt2":    "Inglés",
            "resume_lang_opt3":    "Español",
            "resume_lang_ok":      "✓ Idioma del currículum",
            "format_question":     "💾 Formato de salida:",
            "format_opt1":         "DOCX (Word)",
            "format_opt2":         "PDF",
            "format_opt3":         "Ambos (DOCX + PDF)",
            "format_ok":           "✓ Formato",
            "model_question":      "🤖 Modelo de IA:",
            "model_opt1":          f"Predeterminado ({MODEL})",
            "model_opt2":          "Escribir otro modelo",
            "model_custom_prompt": "Ingresa el ID del modelo (ej: google/gemini-2.5-flash-preview:free): ",
            "model_ok":            "✓ Modelo",
            "generating":          "🚀 Generando tu currículum ATS...",
            "calling_api":         "Llamando a OpenRouter",
            "saving":              "💾 Guardando archivos...",
            "file_ok":             "✓",
            "done":                "✅ ¡Listo! Archivos guardados en: output/",
            "preview":             "📄 Vista previa:",
            "paste_end":           "(pega el texto y presiona Enter dos veces para terminar)",
            "api_key_error":       "ERROR: variable OPENROUTER_API_KEY no definida.",
            "api_key_hint":        'En Windows ejecuta: setx OPENROUTER_API_KEY "sk-or-..."',
            "api_key_hint2":       "Luego cierra y abre el terminal.",
            "api_error":           "ERROR de API",
            "api_empty":           "ERROR: el modelo devolvió respuesta vacía. Prueba otro modelo.",
            "api_unexpected":      "ERROR: respuesta inesperada de la API",
            "docx_missing":        "AVISO: python-docx no instalado. Ejecuta: pip install python-docx",
            "pdf_missing":         "AVISO: reportlab no instalado. Ejecuta: pip install reportlab",
            "choose":              "Elige",
        }
    },
}

RESUME_LANG_MAP = {"1": "1", "2": "2", "3": "3"}
FORMAT_MAP = {"1": "docx", "2": "pdf", "3": "all"}

# ── helpers ────────────────────────────────────────────────────────────────────

def separator():
    print("\n" + "─" * 50)

def ask(question, options, ui):
    print(f"\n{question}")
    for key, label in options.items():
        print(f"  [{key}] {label}")
    while True:
        answer = input(f"  {ui['choose']}: ").strip()
        if answer in options:
            return answer
        print(f"  → {', '.join(options.keys())}")

def ask_multiline(question, ui):
    print(f"\n{question}")
    print(f"  {ui['paste_end']}\n")
    lines = []
    blank_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)
    return "\n".join(lines).strip()

# ── readers ────────────────────────────────────────────────────────────────────

def read_data_md():
    if not DATA_MD.exists():
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
    return ""

def _read_docx(path):
    if not DOCX_OK:
        return ""
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

# ── prompt ─────────────────────────────────────────────────────────────────────

def build_prompt(raw_data, resumes, job_description, lang):
    h = lang["resume_headers"]
    lang_name = lang["name"]
    section_resumes = f"\n=== OLD RESUMES ===\n{resumes}\n" if resumes.strip() else ""

    return f"""You are an expert in recruitment and ATS (Applicant Tracking System) resume optimization.

Candidate raw data (may be disorganized, from multiple sources):

=== RAW DATA ===
{raw_data}
{section_resumes}
=== JOB DESCRIPTION ===
{job_description}

=== CRITICAL LANGUAGE RULE ===
Output language: {lang_name}
Write EVERY word in {lang_name} — section headers, job titles, bullet points, summary, skills, everything.
If raw data is in another language, translate ALL content to {lang_name}.
Never mix languages.

=== OUTPUT FORMAT — FOLLOW EXACTLY ===
{h["name"]}: [full name]
{h["contact"]}: [email] | [phone] | [linkedin] | [city/state]

## {h["summary"]}
[3-4 lines in {lang_name}, tailored to the job]

## {h["experience"]}

### [Job title in {lang_name}] - [Company] | [Period]
- [achievement in {lang_name}]
- [achievement in {lang_name}]

## {h["education"]}

### [Degree in {lang_name}] - [Institution] | [Year]

## {h["skills"]}
[comma-separated list in {lang_name}]

=== RULES ===
1. Extract name, contact, experiences, education, skills, achievements
2. Ignore duplicates and irrelevant items for this job
3. Use the SAME keywords from the job description (crucial for ATS)
4. Quantify achievements with numbers whenever possible
5. Max 1-2 pages
6. Reply ONLY with the resume — no explanations, no code fences, no commentary

=== SKILLS SECTION — STRICT RULES ===
List ONLY concrete, specific, verifiable technical skills:
  ✅ INCLUDE: programming languages, frameworks, databases, tools, platforms, certifications
     Examples: Python, Django, PostgreSQL, Docker, AWS, Git, React, Kubernetes

  ❌ NEVER include any of the following — they are obvious, generic or not real skills:
     - Soft skills: "teamwork", "communication", "leadership", "proactivity", "organization"
     - Generic responsibilities: "code review", "software architecture", "third-party integrations",
       "data security", "compliance", "agile methodology", "scrum"
     - Languages spoken: "English", "Portuguese", "Spanish", "native", "intermediate", "fluent"
       (spoken languages do NOT belong in the skills section)
     - Vague tools: "Microsoft Office", "Google Docs", "email", "Slack"

If a skill could appear on ANY professional's resume regardless of their technical area, do NOT include it.
"""

# ── API ────────────────────────────────────────────────────────────────────────

def call_model(prompt, model, ui):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(f"\n  {ui['api_key_error']}")
        print(f"  {ui['api_key_hint']}")
        print(f"  {ui['api_key_hint2']}\n")
        sys.exit(1)

    print(f"\n  {ui['calling_api']} ({model})...")
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
        print(f"\n  {ui['api_error']} ({e.code}): {e.read().decode('utf-8')}")
        sys.exit(1)

    try:
        content = data["choices"][0]["message"]["content"]
        if not content:
            print(f"\n  {ui['api_empty']}")
            sys.exit(1)
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()
        return content
    except (KeyError, IndexError):
        print(f"\n  {ui['api_unexpected']}: {json.dumps(data, indent=2)}")
        sys.exit(1)

# ── savers ─────────────────────────────────────────────────────────────────────

def save_docx(text, base_name, lang, ui):
    if not DOCX_OK:
        print(f"  {ui['docx_missing']}")
        return None
    h = lang["resume_headers"]
    name_lbl    = h["name"]
    contact_lbl = h["contact"]

    path = OUTPUT_DIR / f"{base_name}.docx"
    doc = Document()
    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith(f"{name_lbl}:"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line[len(name_lbl)+1:].strip())
            run.bold = True; run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        elif line.startswith(f"{contact_lbl}:"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line[len(contact_lbl)+1:].strip())
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            doc.add_paragraph()
        elif line.startswith("## "):
            p = doc.add_paragraph()
            run = p.add_run(line[3:].strip().upper())
            run.bold = True; run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after  = Pt(2)
            p2 = doc.add_paragraph()
            run2 = p2.add_run("─" * 60)
            run2.font.size = Pt(7)
            run2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            p2.paragraph_format.space_after = Pt(4)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            run = p.add_run(line[4:].strip())
            run.bold = True; run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
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

def save_pdf(text, base_name, lang, ui):
    if not PDF_OK:
        print(f"  {ui['pdf_missing']}")
        return None
    h = lang["resume_headers"]
    name_lbl    = h["name"]
    contact_lbl = h["contact"]

    path = OUTPUT_DIR / f"{base_name}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    color_p = colors.HexColor("#000000")
    color_t = colors.HexColor("#000000")
    color_s = colors.HexColor("#444444")
    s_name    = ParagraphStyle("Name",    parent=styles["Title"],    fontSize=20, textColor=color_t, spaceAfter=2,   alignment=1, fontName="Helvetica-Bold")
    s_contact = ParagraphStyle("Contact", parent=styles["Normal"],   fontSize=9,  textColor=color_s, spaceAfter=12,  alignment=1, fontName="Helvetica")
    s_section = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=10, textColor=color_p, spaceBefore=12, spaceAfter=2, fontName="Helvetica-Bold")
    s_sub     = ParagraphStyle("Sub",     parent=styles["Normal"],   fontSize=10, textColor=color_t, spaceBefore=6,  spaceAfter=1, fontName="Helvetica-Bold")
    s_bullet  = ParagraphStyle("Bullet",  parent=styles["Normal"],   fontSize=9.5,textColor=color_t, leftIndent=12,  spaceAfter=2, fontName="Helvetica")
    s_normal  = ParagraphStyle("Normal2", parent=styles["Normal"],   fontSize=9.5,textColor=color_t, spaceAfter=2,   fontName="Helvetica")

    story = []
    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith(f"{name_lbl}:"):
            story.append(Paragraph(line[len(name_lbl)+1:].strip(), s_name))
        elif line.startswith(f"{contact_lbl}:"):
            story.append(Paragraph(line[len(contact_lbl)+1:].strip(), s_contact))
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

# ── main ───────────────────────────────────────────────────────────────────────

def main():

    # ── 0. System language (first thing asked) ────────────────────────────────
    print("\n" + "═" * 50)
    print("  Select system language / Selecione o idioma / Selecciona el idioma")
    print("═" * 50)
    print("  [1] Português (Brasil)")
    print("  [2] English")
    print("  [3] Español")
    while True:
        sys_lang_choice = input("  > ").strip()
        if sys_lang_choice in LANGUAGES:
            break
        print("  → 1, 2 or 3")

    lang = LANGUAGES[sys_lang_choice]
    ui   = lang["ui"]

    # ── Header ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 50)
    print(f"         {ui['title']}")
    print("═" * 50)

    # ── 1. Read profile data ──────────────────────────────────────────────────
    separator()
    print(ui["reading_profile"])
    raw_data = read_data_md()
    if raw_data.strip():
        print(f"  {ui['data_loaded']} ({len(raw_data)} chars)")
    else:
        print(f"  {ui['data_empty']}")

    resumes = read_old_resumes()
    n = resumes.count("[Resume:")
    print(f"  ✓ {n} {ui['resumes_found']}")

    # ── 2. Job description ────────────────────────────────────────────────────
    separator()
    job_choice = ask(
        ui["job_question"],
        {"1": ui["job_opt1"], "2": ui["job_opt2"]},
        ui
    )

    if job_choice == "1":
        job_file = BASE_DIR / "job_description.txt"
        if not job_file.exists():
            print(f"\n  {ui['job_not_found']}")
            sys.exit(1)
        job_description = job_file.read_text(encoding="utf-8")
        print(f"  {ui['job_loaded']} ({len(job_description)} chars)")
    else:
        job_description = ask_multiline(ui["job_paste"], ui)
        if not job_description:
            print(f"\n  {ui['job_empty']}")
            sys.exit(1)
        print(f"  {ui['job_received']} ({len(job_description)} chars)")

    # ── 3. Resume language ────────────────────────────────────────────────────
    separator()
    resume_lang_choice = ask(
        ui["resume_lang"],
        {"1": ui["resume_lang_opt1"], "2": ui["resume_lang_opt2"], "3": ui["resume_lang_opt3"]},
        ui
    )
    resume_lang = LANGUAGES[resume_lang_choice]
    print(f"  {ui['resume_lang_ok']}: {resume_lang['name']}")

    # ── 4. Format ─────────────────────────────────────────────────────────────
    separator()
    fmt_choice = ask(
        ui["format_question"],
        {"1": ui["format_opt1"], "2": ui["format_opt2"], "3": ui["format_opt3"]},
        ui
    )
    fmt = FORMAT_MAP[fmt_choice]
    print(f"  {ui['format_ok']}: {fmt.upper()}")

    # ── 5. Model ──────────────────────────────────────────────────────────────
    separator()
    model_choice = ask(
        ui["model_question"],
        {"1": ui["model_opt1"], "2": ui["model_opt2"]},
        ui
    )
    if model_choice == "1":
        model = MODEL
    else:
        model = input(f"  {ui['model_custom_prompt']}").strip() or MODEL
    print(f"  {ui['model_ok']}: {model}")

    # ── 6. Generate ───────────────────────────────────────────────────────────
    separator()
    print(ui["generating"])
    prompt = build_prompt(raw_data, resumes, job_description, resume_lang)
    resume = call_model(prompt, model, ui)

    # ── 7. Save ───────────────────────────────────────────────────────────────
    ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    base_name = f"ats_resume_{ts}"

    separator()
    print(ui["saving"])

    saved = []
    if fmt in ("docx", "all"):
        p = save_docx(resume, base_name, resume_lang, ui)
        if p:
            print(f"  {ui['file_ok']} {p.name}")
            saved.append(p)

    if fmt in ("pdf", "all"):
        p = save_pdf(resume, base_name, resume_lang, ui)
        if p:
            print(f"  {ui['file_ok']} {p.name}")
            saved.append(p)

    # ── 8. Done ───────────────────────────────────────────────────────────────
    separator()
    print(f"\n{ui['done']}")
    for p in saved:
        print(f"   → {p.name}")

    print(f"\n{ui['preview']}\n")
    print(textwrap.indent(resume[:700] + ("..." if len(resume) > 700 else ""), "  "))
    print()

if __name__ == "__main__":
    main()
