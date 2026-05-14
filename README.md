<div align="center">

# RouterResume

**PT-BR** | [EN](#routerresume-1)

Gera currículos ATS otimizados para vagas específicas a partir dos seus dados brutos, usando modelos de IA gratuitos via OpenRouter.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red?logo=streamlit&logoColor=white)](https://streamlit.io)
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
RouterResume/
│
├── 📄 app_streamlit.py     ← interface web (rode esse)
├── 📄 generate.py          ← motor de geração
├── 📝 data.md              ← SEUS dados brutos (adicione à vontade)
├── 📦 requirements.txt
│
├── 📁 ui/                  ← componentes da interface
│   ├── sidebar.py
│   ├── i18n.py
│   ├── styles.py
│   └── tabs/
│       ├── tab_how_to.py   ← Como usar
│       ├── tab_generate.py ← Gerar currículo
│       ├── tab_resumes.py  ← Currículos antigos
│       ├── tab_data.py     ← Dados do perfil
│       └── tab_test_key.py ← Testar API Key
│
├── 📁 old_resumes/         ← seus currículos antigos (.pdf, .docx, .txt, .md)
└── 📁 output/              ← currículos gerados ficam aqui
```

---

## Setup (só uma vez)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/RouterResume.git
cd RouterResume
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Rode a interface
```bash
streamlit run app_streamlit.py
```

O browser abre automaticamente em `http://localhost:8501`.

---

## Como usar

A interface é organizada em **5 abas**:

| Aba | Função |
|-----|--------|
| 📖 Como usar | Este guia |
| 🚀 Gerar | Gerar o currículo a partir de uma vaga |
| 📁 Currículos Antigos | Enviar currículos anteriores para contexto |
| 👤 Dados do Perfil | Editar seus dados brutos (`data.md`) |
| 🔑 Testar Key | Testar se a API Key e o modelo estão funcionando |

### Passo 1 — Configure sua API Key

Na **barra lateral**, cole sua chave do OpenRouter (`sk-or-...`) e clique em **Salvar chave**.

> Não tem chave? Crie grátis em [openrouter.ai](https://openrouter.ai) → **Keys** → **Create Key** (sem cartão de crédito).

Use a aba **🔑 Testar Key** para confirmar que está funcionando.

### Passo 2 — Adicione seus dados de perfil

Vá para a aba **👤 Dados do Perfil** e cole tudo sobre você — sem formato obrigatório:

```
Trabalhei 4 anos na Empresa X como dev Python.
Fiz integração com APIs de pagamento (Stripe, PagSeguro).
Reduzi tempo de deploy em 60% com CI/CD.
Graduado em Ciência da Computação pela UFPE em 2019.
AWS Certified — 2022. Inglês avançado.
```

> Quanto mais informação, melhor o resultado. Cole currículos antigos completos, experiências soltas, projetos, tudo.

### Passo 3 — Adicione currículos antigos

Vá para a aba **📁 Currículos Antigos** e envie arquivos `.pdf`, `.docx`, `.txt` ou `.md`.

### Passo 4 — Gere o currículo

Vá para a aba **🚀 Gerar**, cole a descrição completa da vaga e clique em **🚀 Gerar currículo**.

Na barra lateral você ajusta idioma do currículo, formato (DOCX/PDF) e modelo de IA.

---

## Modelos gratuitos disponíveis

Veja todos em **[openrouter.ai/models](https://openrouter.ai/models)** (filtre por "Free").

| Modelo | Qualidade |
|--------|-----------|
| `google/gemini-2.5-flash-preview:free` | ⭐⭐⭐⭐⭐ |
| `meta-llama/llama-3.3-70b-instruct:free` | ⭐⭐⭐⭐ |
| `deepseek/deepseek-r1:free` | ⭐⭐⭐⭐ |
| `inclusionai/ling-2.6-1t:free` | ⭐⭐⭐⭐ |

> ⚠️ Modelos gratuitos podem ter rate limit. Se receber erro 429 ou 404, tente outro modelo.

---

## Dicas

- **Mais dados = melhor resultado** — cole tudo, mesmo que pareça irrelevante. A IA filtra o que importa para cada vaga.
- **Revise sempre** — a IA pode preencher lacunas com informações plausíveis mas imprecisas.
- **Interface e currículo são independentes** — você pode usar o sistema em português e gerar o currículo em inglês.
- **`data.md` é cumulativo** — vá adicionando ao longo do tempo. Com o tempo seus currículos ficam cada vez melhores.

---
---

<div align="center">

# RouterResume

[PT-BR](#routerresume) | **EN**

Generates ATS-optimized resumes for specific job postings from your raw data, using free AI models via OpenRouter.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red?logo=streamlit&logoColor=white)](https://streamlit.io)
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
RouterResume/
│
├── 📄 app_streamlit.py     ← web interface (run this)
├── 📄 generate.py          ← generation engine
├── 📝 data.md              ← YOUR raw data (keep adding anytime)
├── 📦 requirements.txt
│
├── 📁 ui/                  ← interface components
│   ├── sidebar.py
│   ├── i18n.py
│   ├── styles.py
│   └── tabs/
│       ├── tab_how_to.py   ← How to use
│       ├── tab_generate.py ← Generate resume
│       ├── tab_resumes.py  ← Old resumes
│       ├── tab_data.py     ← Profile data
│       └── tab_test_key.py ← Test API Key
│
├── 📁 old_resumes/         ← your old resumes (.pdf, .docx, .txt, .md)
└── 📁 output/              ← generated resumes saved here
```

---

## Setup (once)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/RouterResume.git
cd RouterResume
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the interface
```bash
streamlit run app_streamlit.py
```

The browser opens automatically at `http://localhost:8501`.

---

## How to use

The interface is organized into **5 tabs**:

| Tab | Purpose |
|-----|---------|
| 📖 How to use | This guide |
| 🚀 Generate | Generate a resume from a job posting |
| 📁 Old Resumes | Upload previous resumes for context |
| 👤 Profile Data | Edit your raw data (`data.md`) |
| 🔑 Test Key | Test whether your API Key and model are working |

### Step 1 — Set up your API Key

In the **sidebar**, paste your OpenRouter key (`sk-or-...`) and click **Save key**.

> No key yet? Create one for free at [openrouter.ai](https://openrouter.ai) → **Keys** → **Create Key** (no credit card needed).

Use the **🔑 Test Key** tab to confirm it's working.

### Step 2 — Add your profile data

Go to the **👤 Profile Data** tab and dump everything about yourself — no format required:

```
Worked 4 years at Company X as a Python developer.
Built payment API integrations (Stripe, PagSeguro).
Reduced deploy time by 60% implementing CI/CD.
BSc in Computer Science, UFPE, 2019.
AWS Certified — 2022. Fluent English.
```

> The more data, the better. Paste full old resumes, loose experiences, projects — everything together.

### Step 3 — Add old resumes

Go to the **📁 Old Resumes** tab and upload `.pdf`, `.docx`, `.txt` or `.md` files.

### Step 4 — Generate the resume

Go to the **🚀 Generate** tab, paste the full job description and click **🚀 Generate resume**.

In the sidebar you can adjust the resume language, output format (DOCX/PDF) and AI model.

---

## Available free models

See all at **[openrouter.ai/models](https://openrouter.ai/models)** (filter by "Free").

| Model | Quality |
|-------|---------|
| `google/gemini-2.5-flash-preview:free` | ⭐⭐⭐⭐⭐ |
| `meta-llama/llama-3.3-70b-instruct:free` | ⭐⭐⭐⭐ |
| `deepseek/deepseek-r1:free` | ⭐⭐⭐⭐ |
| `inclusionai/ling-2.6-1t:free` | ⭐⭐⭐⭐ |

> ⚠️ Free models can have rate limits. If you get a 429 or 404 error, try a different model.

---

## Tips

- **More data = better results** — dump everything, even if it seems irrelevant. The AI filters what matters for each job.
- **Always review** — the AI may fill gaps with plausible but inaccurate details.
- **Interface and resume language are independent** — you can run the system in English and generate the resume in Portuguese.
- **`data.md` is cumulative** — keep adding over time. Your resumes get better and better.
