#!/usr/bin/env python3
"""
ATS Resume Generator — Web UI
Run: python app.py
Then open: http://localhost:5000
"""
import os, sys, json, threading, webbrowser, datetime, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Import core logic from generate.py
sys.path.insert(0, str(Path(__file__).parent))
from generate import (
    LANGUAGES, read_data_md, read_old_resumes,
    build_prompt, call_model, save_docx, save_pdf,
    OUTPUT_DIR, DATA_MD, OLD_RESUMES_DIR, MODEL
)

PORT = 5000

# ── HTML ───────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ATS Resume Generator</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:      #F5F2ED;
    --surface: #FDFCFA;
    --border:  #D8D3CB;
    --ink:     #1A1814;
    --muted:   #7A766E;
    --accent:  #1A1814;
    --success: #2D6A4F;
    --error:   #9B2226;
    --radius:  4px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--ink);
    min-height: 100vh;
    padding: 0 0 60px;
  }

  /* Header */
  header {
    border-bottom: 1px solid var(--border);
    padding: 28px 48px;
    display: flex;
    align-items: baseline;
    gap: 16px;
    background: var(--surface);
  }
  header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 24px;
    font-weight: 400;
    letter-spacing: -0.3px;
  }
  header span {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 3px 8px;
    border-radius: 2px;
  }

  /* Layout */
  .layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 48px;
  }
  @media (max-width: 860px) {
    .layout { grid-template-columns: 1fr; padding: 24px 20px; }
    header { padding: 20px; }
  }

  .col-left  { padding-right: 40px; border-right: 1px solid var(--border); }
  .col-right { padding-left: 40px; }

  /* Section titles */
  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  .block { margin-bottom: 32px; }

  /* Form elements */
  label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 6px;
    letter-spacing: 0.02em;
  }

  textarea, select, input[type=text] {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px 12px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13.5px;
    color: var(--ink);
    outline: none;
    transition: border-color .15s;
  }
  textarea:focus, select:focus, input:focus {
    border-color: var(--ink);
  }
  textarea {
    resize: vertical;
    min-height: 120px;
    line-height: 1.6;
  }
  select { cursor: pointer; }

  /* Data status bar */
  .data-status {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 14px;
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .data-status .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--success);
    flex-shrink: 0;
  }
  .data-status .dot.warn { background: #E76F51; }

  /* Row */
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  /* Button */
  .btn-generate {
    width: 100%;
    padding: 14px;
    background: var(--ink);
    color: #F5F2ED;
    border: none;
    border-radius: var(--radius);
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    letter-spacing: 0.02em;
    transition: opacity .15s;
    margin-top: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  .btn-generate:hover { opacity: .85; }
  .btn-generate:disabled { opacity: .4; cursor: not-allowed; }

  /* Log / output */
  .log-area {
    background: var(--ink);
    color: #C8C4BB;
    border-radius: var(--radius);
    padding: 16px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    line-height: 1.7;
    min-height: 100px;
    white-space: pre-wrap;
    margin-top: 16px;
    display: none;
  }
  .log-area.visible { display: block; }
  .log-area .ok  { color: #95D5B2; }
  .log-area .err { color: #F4978E; }
  .log-area .dim { color: #6B6760; }

  /* Download cards */
  .downloads { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
  .dl-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-decoration: none;
    color: var(--ink);
    font-size: 13px;
    transition: border-color .15s;
  }
  .dl-card:hover { border-color: var(--ink); }
  .dl-card .dl-name { font-family: 'DM Mono', monospace; font-size: 11.5px; }
  .dl-card .dl-arrow { font-size: 16px; color: var(--muted); }

  /* Preview */
  .preview-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    font-size: 12.5px;
    line-height: 1.75;
    white-space: pre-wrap;
    color: var(--ink);
    max-height: 400px;
    overflow-y: auto;
    margin-top: 16px;
    display: none;
  }
  .preview-box.visible { display: block; }

  /* Spinner */
  .spin {
    width: 16px; height: 16px;
    border: 2px solid rgba(245,242,237,.3);
    border-top-color: #F5F2ED;
    border-radius: 50%;
    animation: spin .7s linear infinite;
    display: none;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Divider */
  hr { border: none; border-top: 1px solid var(--border); margin: 28px 0; }

  .hint {
    font-size: 11.5px;
    color: var(--muted);
    margin-top: 6px;
    line-height: 1.5;
  }
</style>
</head>
<body>

<header>
  <h1>ATS Resume Generator</h1>
  <span>local · free</span>
</header>

<div class="layout">

  <!-- LEFT COLUMN -->
  <div class="col-left">

    <div class="block">
      <div class="section-label">Profile data</div>
      <div class="data-status" id="status-data">
        <div class="dot" id="dot-data"></div>
        <span id="text-data">Checking data.md...</span>
      </div>
      <div class="data-status" id="status-resumes">
        <div class="dot" id="dot-resumes"></div>
        <span id="text-resumes">Checking old_resumes/...</span>
      </div>
      <p class="hint">Edit <code>data.md</code> to add your info. Drop old resumes in <code>old_resumes/</code>.</p>
    </div>

    <div class="block">
      <div class="section-label">Job description</div>
      <label for="job">Paste the full job posting</label>
      <textarea id="job" placeholder="Paste the complete job description here — title, requirements, responsibilities, everything..."></textarea>
    </div>

    <div class="block">
      <div class="section-label">Options</div>
      <div class="row">
        <div>
          <label for="lang">Resume language</label>
          <select id="lang">
            <option value="1">Português (Brasil)</option>
            <option value="2">English</option>
            <option value="3">Español</option>
          </select>
        </div>
        <div>
          <label for="fmt">Output format</label>
          <select id="fmt">
            <option value="docx">DOCX (Word)</option>
            <option value="pdf">PDF</option>
            <option value="all">Both</option>
          </select>
        </div>
      </div>
      <div style="margin-top:12px">
        <label for="model">AI model</label>
        <input type="text" id="model" value="__MODEL__" placeholder="openrouter model id">
        <p class="hint">Free models at <a href="https://openrouter.ai/models" target="_blank" style="color:var(--ink)">openrouter.ai/models</a> — filter by "Free"</p>
      </div>
    </div>

    <button class="btn-generate" id="btn" onclick="generate()">
      <div class="spin" id="spin"></div>
      <span id="btn-text">Generate resume</span>
    </button>

  </div>

  <!-- RIGHT COLUMN -->
  <div class="col-right">

    <div class="section-label">Output</div>

    <div id="log" class="log-area"></div>

    <div id="downloads" class="downloads"></div>

    <div id="preview" class="preview-box"></div>

  </div>

</div>

<script>
async function checkStatus() {
  const r = await fetch('/status');
  const d = await r.json();

  const dotD = document.getElementById('dot-data');
  const txtD = document.getElementById('text-data');
  if (d.data_chars > 0) {
    txtD.textContent = `data.md — ${d.data_chars} characters loaded`;
  } else {
    dotD.classList.add('warn');
    txtD.textContent = 'data.md is empty — add your profile info';
  }

  const dotR = document.getElementById('dot-resumes');
  const txtR = document.getElementById('text-resumes');
  if (d.resumes > 0) {
    txtR.textContent = `old_resumes/ — ${d.resumes} file(s) found`;
  } else {
    dotR.classList.add('warn');
    txtR.textContent = 'old_resumes/ — no files found (optional)';
  }
}

function log(msg, cls='') {
  const el = document.getElementById('log');
  el.classList.add('visible');
  el.innerHTML += cls ? `<span class="${cls}">${msg}</span>\n` : msg + '\n';
  el.scrollTop = el.scrollHeight;
}

async function generate() {
  const job = document.getElementById('job').value.trim();
  if (!job) { alert('Please paste a job description first.'); return; }

  const btn  = document.getElementById('btn');
  const spin = document.getElementById('spin');
  const btxt = document.getElementById('btn-text');

  btn.disabled = true;
  spin.style.display = 'block';
  btxt.textContent = 'Generating...';

  const logEl = document.getElementById('log');
  logEl.innerHTML = '';
  logEl.classList.add('visible');
  document.getElementById('downloads').innerHTML = '';
  document.getElementById('preview').classList.remove('visible');

  log('Starting generation...', 'dim');

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job:      job,
        lang:     document.getElementById('lang').value,
        format:   document.getElementById('fmt').value,
        model:    document.getElementById('model').value.trim(),
      })
    });

    const data = await resp.json();

    if (data.error) {
      log(data.error, 'err');
    } else {
      log('✓ Resume generated', 'ok');

      // Downloads
      const dl = document.getElementById('downloads');
      data.files.forEach(f => {
        const a = document.createElement('a');
        a.href = `/download?file=${encodeURIComponent(f.name)}`;
        a.download = f.name;
        a.className = 'dl-card';
        a.innerHTML = `<span class="dl-name">${f.name}</span><span class="dl-arrow">↓</span>`;
        dl.appendChild(a);
        log(`✓ ${f.name}`, 'ok');
      });

      // Preview
      const pv = document.getElementById('preview');
      pv.textContent = data.preview;
      pv.classList.add('visible');
    }
  } catch(e) {
    log('Network error: ' + e.message, 'err');
  }

  btn.disabled = false;
  spin.style.display = 'none';
  btxt.textContent = 'Generate resume';
}

checkStatus();
</script>
</body>
</html>
""".replace("__MODEL__", MODEL)

# ── HTTP handler ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress default server logs

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.send_html(HTML)

        elif parsed.path == "/status":
            raw = read_data_md()
            resumes = read_old_resumes()
            self.send_json({
                "data_chars": len(raw.strip()),
                "resumes": resumes.count("[Resume:"),
            })

        elif parsed.path == "/download":
            qs = parse_qs(parsed.query)
            fname = qs.get("file", [""])[0]
            fpath = OUTPUT_DIR / fname
            if not fpath.exists() or not fname:
                self.send_response(404); self.end_headers(); return
            data = fpath.read_bytes()
            ext  = fpath.suffix.lower()
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if ext == ".docx" else "application/pdf"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)

        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path != "/generate":
            self.send_response(404); self.end_headers(); return

        length  = int(self.headers.get("Content-Length", 0))
        body    = json.loads(self.rfile.read(length))

        job     = body.get("job", "").strip()
        lang    = LANGUAGES.get(body.get("lang", "1"), LANGUAGES["1"])
        fmt     = body.get("format", "docx")
        model   = body.get("model", MODEL).strip() or MODEL

        if not job:
            self.send_json({"error": "No job description provided."}, 400); return

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            self.send_json({"error": "OPENROUTER_API_KEY not set. Set it and restart the server."}); return

        try:
            raw_data    = read_data_md()
            old_resumes = read_old_resumes()
            prompt      = build_prompt(raw_data, old_resumes, job, lang)

            # call_model expects a ui dict for error messages — provide a minimal one
            ui_stub = {
                "calling_api": "Calling OpenRouter",
                "api_key_error": "API key error",
                "api_key_hint": "", "api_key_hint2": "",
                "api_error": "API error",
                "api_empty": "Empty response",
                "api_unexpected": "Unexpected response",
            }
            resume = call_model(prompt, model, ui_stub)

            ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            base_name = f"ats_resume_{ts}"
            saved     = []

            if fmt in ("docx", "all"):
                ui_docx = {"docx_missing": "python-docx not installed"}
                p = save_docx(resume, base_name, lang, ui_docx)
                if p: saved.append(p)

            if fmt in ("pdf", "all"):
                ui_pdf = {"pdf_missing": "reportlab not installed"}
                p = save_pdf(resume, base_name, lang, ui_pdf)
                if p: saved.append(p)

            self.send_json({
                "files":   [{"name": p.name} for p in saved],
                "preview": resume[:1200],
            })

        except SystemExit:
            self.send_json({"error": "API call failed. Check model name or API key."})
        except Exception as e:
            self.send_json({"error": str(e)})

# ── entry point ────────────────────────────────────────────────────────────────

def main():
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\n  WARNING: OPENROUTER_API_KEY not set.")
        print("  Set it before generating resumes.\n")

    server = HTTPServer(("localhost", PORT), Handler)
    url    = f"http://localhost:{PORT}"

    print(f"\n  ATS Resume Generator — Web UI")
    print(f"  ──────────────────────────────")
    print(f"  Running at: {url}")
    print(f"  Press Ctrl+C to stop\n")

    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")

if __name__ == "__main__":
    main()
