<div align="center">

# 🎯 ATS Resume Generator

**PT-BR** | [EN](#-ats-resume-generator-1)

Gera currículos ATS otimizados para vagas específicas a partir dos seus dados brutos, usando modelos de IA gratuitos via OpenRouter.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-purple)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Free](https://img.shields.io/badge/Custo-Gratuito-brightgreen)](https://openrouter.ai)

</div>

---

## Como funciona

```
Seus dados (data.md)          Descrição da vaga
      +                    +                      →  Currículo ATS perfeito 🎯
Currículos antigos (PDFs)     Idioma escolhido
```

Você acumula seus dados uma vez. Para cada vaga, o sistema extrai o que é relevante, usa as palavras-chave exatas da vaga e gera um currículo otimizado para passar pelos filtros ATS.

---

## Estrutura do projeto

```
ats-resume-generator/
│
├── 📄 generate.py          ← script principal (rode esse)
├── 📝 data.md              ← SEUS dados brutos (adicione à vontade)
├── 📋 job_description.txt  ← cole aqui o texto da vaga
├── 📦 requirements.txt
│
├── 📁 old_resumes/         ← jogue seus currículos antigos aqui
│   ├── resume_2022.pdf
│   ├── linkedin_export.txt
│   └── old_resume.docx
│
└── 📁 output/              ← currículos gerados ficam aqui
    └── ats_resume_20240428_1430.docx / .pdf
```

---

## Setup (só uma vez)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/ats-resume-generator.git
cd ats-resume-generator
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Crie sua conta no OpenRouter
- Acesse **[openrouter.ai](https://openrouter.ai)** → Sign in com Google
- Vá em **Keys** → **Create Key**
- Copie a chave `sk-or-...` (é gratuito, sem cartão)

### 4. Configure a chave de API

**Windows:**
```cmd
setx OPENROUTER_API_KEY "sk-or-..."
```
> ⚠️ Feche e abra o terminal depois.

**Mac/Linux:**
```bash
export OPENROUTER_API_KEY="sk-or-..."
# Para persistir, adicione essa linha ao seu ~/.zshrc ou ~/.bashrc
```

---

## Como usar

### Passo 1 — Alimente seus dados

Edite o arquivo `data.md` e jogue qualquer informação sobre você — **sem formato obrigatório**:

```
Trabalhei 4 anos na Empresa X como dev Python.
Fiz integração com APIs de pagamento (Stripe, PagSeguro).
Reduzi tempo de deploy em 60% com CI/CD.
Graduado em Ciência da Computação pela UFPE em 2019.
AWS Certified — 2022. Inglês avançado.
```

> 💡 Cole currículos antigos completos, experiências soltas, certificados, projetos pessoais — tudo junto e misturado. A IA organiza.

Ou coloque arquivos direto na pasta `old_resumes/` — suporta `.pdf`, `.docx`, `.txt`, `.md`.

### Passo 2 — Adicione a vaga

Cole o texto completo da vaga em `job_description.txt`.

### Passo 3 — Gere o currículo

```bash
python generate.py
```

O programa vai te perguntar tudo interativamente:

```
══════════════════════════════════════════════════
  Select system language / Selecione o idioma
══════════════════════════════════════════════════
  [1] Português (Brasil)
  [2] English
  [3] Español

📋 Descrição da vaga — onde está?
  [1] Tenho um arquivo (job_description.txt)
  [2] Vou colar agora

🌐 Idioma do currículo:
  [1] Português (Brasil)
  [2] Inglês
  [3] Espanhol

💾 Formato de saída:
  [1] DOCX (Word)
  [2] PDF
  [3] Ambos

🤖 Modelo de IA:
  [1] Padrão (inclusionai/ling-2.6-1t:free)
  [2] Digitar outro modelo
```

O currículo gerado vai para a pasta `output/` com timestamp.

---

## Fluxo recomendado

```
1. Preencha data.md com tudo que sabe sobre você
2. Jogue currículos antigos em old_resumes/
3. Achou uma vaga? → Cole em job_description.txt
4. Rode: python generate.py
5. Abra output/ats_resume_*.docx, revise e envie ✅
```

> **Dica:** `data.md` é cumulativo. Cada vez que ganhar uma skill, terminar um projeto ou tirar uma certificação, adicione lá. Com o tempo seus currículos ficam cada vez melhores.

---

## Modelos gratuitos disponíveis

Veja todos em **[openrouter.ai/models](https://openrouter.ai/models)** (filtre por "Free").

| Modelo | Qualidade |
|--------|-----------|
| `inclusionai/ling-2.6-1t:free` | ⭐⭐⭐⭐ |
| `google/gemini-2.5-flash-preview:free` | ⭐⭐⭐⭐⭐ |
| `meta-llama/llama-3.3-70b-instruct:free` | ⭐⭐⭐⭐ |
| `deepseek/deepseek-r1:free` | ⭐⭐⭐⭐ |

> ⚠️ Modelos gratuitos podem ter rate limit. Se receber erro 429 ou 404, tente outro modelo.

---

## Dicas

- **Mais dados = melhor resultado** — cole tudo, mesmo que pareça irrelevante. A IA filtra o que importa para cada vaga.
- **Revise sempre** — a IA pode preencher lacunas com informações plausíveis mas imprecisas.
- **Interface e currículo são independentes** — você pode usar o sistema em português e gerar o currículo em inglês.

---
---

<div align="center">

# 🎯 ATS Resume Generator

[PT-BR](#-ats-resume-generator) | **EN**

Generates ATS-optimized resumes for specific job postings from your raw data, using free AI models via OpenRouter.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-purple)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Free](https://img.shields.io/badge/Cost-Free-brightgreen)](https://openrouter.ai)

</div>

---

## How it works

```
Your data (data.md)           Job description
      +                    +                      →  Perfect ATS resume 🎯
Old resumes (PDFs)            Chosen language
```

You accumulate your data once. For each job posting, the system extracts what's relevant, uses the exact keywords from the job description and generates a resume optimized to pass ATS filters.

---

## Project structure

```
ats-resume-generator/
│
├── 📄 generate.py          ← main script (run this)
├── 📝 data.md              ← YOUR raw data (keep adding anytime)
├── 📋 job_description.txt  ← paste the job posting here
├── 📦 requirements.txt
│
├── 📁 old_resumes/         ← drop your old resumes here
│   ├── resume_2022.pdf
│   ├── linkedin_export.txt
│   └── old_resume.docx
│
└── 📁 output/              ← generated resumes saved here
    └── ats_resume_20240428_1430.docx / .pdf
```

---

## Setup (once)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ats-resume-generator.git
cd ats-resume-generator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your OpenRouter account
- Go to **[openrouter.ai](https://openrouter.ai)** → Sign in with Google
- Go to **Keys** → **Create Key**
- Copy the `sk-or-...` key (it's free, no credit card needed)

### 4. Set your API key

**Windows:**
```cmd
setx OPENROUTER_API_KEY "sk-or-..."
```
> ⚠️ Close and reopen the terminal after running this.

**Mac/Linux:**
```bash
export OPENROUTER_API_KEY="sk-or-..."
# To persist, add this line to your ~/.zshrc or ~/.bashrc
```

---

## How to use

### Step 1 — Feed your data

Edit `data.md` and dump any information about yourself — **no format required**:

```
Worked 4 years at Company X as a Python developer.
Built payment API integrations (Stripe, PagSeguro).
Reduced deploy time by 60% implementing CI/CD.
BSc in Computer Science, UFPE, 2019.
AWS Certified — 2022. Fluent English.
```

> 💡 Paste full old resumes, loose experiences, certificates, personal projects — all mixed together. The AI organizes it.

Or drop files directly into the `old_resumes/` folder — supports `.pdf`, `.docx`, `.txt`, `.md`.

### Step 2 — Add the job posting

Paste the full job description text into `job_description.txt`.

### Step 3 — Generate the resume

```bash
python generate.py
```

The program asks everything interactively:

```
══════════════════════════════════════════════════
  Select system language / Selecione o idioma
══════════════════════════════════════════════════
  [1] Português (Brasil)
  [2] English
  [3] Español

📋 Job description — where is it?
  [1] I have a file (job_description.txt)
  [2] I'll paste it now

🌐 Resume language:
  [1] Portuguese (Brazil)
  [2] English
  [3] Spanish

💾 Output format:
  [1] DOCX (Word)
  [2] PDF
  [3] Both

🤖 AI model:
  [1] Default (inclusionai/ling-2.6-1t:free)
  [2] Type a custom model ID
```

The generated resume goes to the `output/` folder with a timestamp.

---

## Recommended workflow

```
1. Fill data.md with everything you know about yourself
2. Drop old resumes into old_resumes/
3. Found a job? → Paste it into job_description.txt
4. Run: python generate.py
5. Open output/ats_resume_*.docx, review and send ✅
```

> **Tip:** `data.md` is cumulative. Every time you gain a new skill, finish a project or get certified, add it there. Over time your resumes get better and better.

---

## Available free models

See all at **[openrouter.ai/models](https://openrouter.ai/models)** (filter by "Free").

| Model | Quality |
|-------|---------|
| `inclusionai/ling-2.6-1t:free` | ⭐⭐⭐⭐ |
| `google/gemini-2.5-flash-preview:free` | ⭐⭐⭐⭐⭐ |
| `meta-llama/llama-3.3-70b-instruct:free` | ⭐⭐⭐⭐ |
| `deepseek/deepseek-r1:free` | ⭐⭐⭐⭐ |

> ⚠️ Free models can have rate limits. If you get a 429 or 404 error, try a different model.

---

## Tips

- **More data = better results** — dump everything, even if it seems irrelevant. The AI filters what matters for each job.
- **Always review** — the AI may fill gaps with plausible but inaccurate details.
- **Interface and resume language are independent** — you can run the system in English and generate the resume in Portuguese.
