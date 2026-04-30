# 🎯 Gerador de Currículo ATS

Gera currículos ATS otimizados para vagas específicas a partir dos seus dados brutos.

---

## Estrutura

```
curriculo-ats/
├── gerar.py                  ← script principal
├── dados.md                  ← SEUS dados brutos (edite à vontade)
├── requirements.txt
├── curriculos_antigos/       ← cole aqui seus currículos antigos
│   ├── curriculo_2021.pdf
│   ├── curriculo_linkedin.txt
│   └── curriculo_empresa_x.docx
└── output/                   ← currículos gerados ficam aqui
    └── curriculo_ats_20240428_1430.md / .docx / .pdf
```

---

## Setup (uma vez só)

**1. Clone ou baixe a pasta do projeto**

**2. Crie um ambiente virtual (recomendado)**
```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure sua API key do Claude**
```bash
# Mac/Linux — adicione ao seu ~/.zshrc ou ~/.bashrc para persistir
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-..."
```
Pegue sua key em: https://console.anthropic.com/

---

## Como usar

### Passo 1 — Alimente seus dados
Edite o arquivo `dados.md` e cole tudo que sabe sobre você:
- Texto dos seus currículos antigos
- Experiências, projetos, conquistas soltas
- Formação, certificados
- Habilidades, idiomas

**Ou** jogue os arquivos diretamente na pasta `curriculos_antigos/`.  
Suporta: `.pdf`, `.docx`, `.txt`, `.md`

Não precisa de formato. Pode ser bagunçado. Quanto mais dados, melhor.

---

### Passo 2 — Gere o currículo

**Modo interativo** (cola a vaga no terminal):
```bash
python gerar.py
```

**Passando a vaga em arquivo** (recomendado):
```bash
# Salve o texto da vaga em vaga.txt e rode:
python gerar.py --vaga vaga.txt
```

**Opções extras:**
```bash
# Só gerar .docx (sem pdf)
python gerar.py --vaga vaga.txt --formato docx

# Em inglês
python gerar.py --vaga vaga.txt --idioma "inglês americano"

# Em espanhol
python gerar.py --vaga vaga.txt --idioma "espanhol"
```

---

### Saída

Os arquivos são salvos em `output/` com timestamp:
```
output/curriculo_ats_20240428_1430.md
output/curriculo_ats_20240428_1430.docx
output/curriculo_ats_20240428_1430.pdf
```

---

## Fluxo recomendado

```
1. Você edita dados.md (vai acumulando dados ao longo do tempo)
2. Joga currículos antigos na pasta curriculos_antigos/
3. Acha uma vaga interessante → salva o texto em vaga.txt
4. Roda: python gerar.py --vaga vaga.txt
5. Abre output/curriculo_ats_*.docx e revisa rapidinho
6. Manda pra vaga ✅
```

---

## Dicas

- **Seja generoso com dados** — cole tudo, mesmo que pareça irrelevante. A IA filtra.
- **Atualize dados.md** sempre que tiver uma nova experiência, projeto ou certificado.
- **Salve a vaga em arquivo** para poder regenerar depois se precisar ajustar.
- **Revise sempre** — a IA pode inventar detalhes se os dados estiverem vagos.
- Para vagas em inglês, use `--idioma "inglês americano"` para adaptar o tom.

---

## Custo estimado

Cada geração usa ~3000-6000 tokens de entrada + ~1000 de saída.  
Com Claude Sonnet: ~US$0,01 a US$0,03 por currículo gerado.

Para reduzir custo, edite `gerar.py` e mude:
```python
MODEL = "claude-sonnet-4-5"   # mais rápido e barato
```
