import streamlit as st

_CONTENT = {
    "pt": """
### Passo 1 — Crie sua conta ou entre

Crie uma conta gratuita ou faça login pelo painel na barra lateral.
Com conta, seus dados de perfil, currículos de referência e histórico de gerações ficam salvos na nuvem.

---

### Passo 2 — Configure sua API Key

Na **barra lateral**, cole sua chave do OpenRouter (`sk-or-...`) e pressione **Enter**.

> Não tem chave? Crie grátis em [openrouter.ai](https://openrouter.ai) → **Keys** → **Create Key** (sem cartão de crédito).

---

### Passo 3 — Adicione seus dados de perfil

Vá para a aba **Dados do Perfil** e cole tudo sobre você:

- Experiências profissionais (empresa, cargo, período, responsabilidades)
- Habilidades técnicas e comportamentais
- Educação, certificações, cursos
- Projetos pessoais e conquistas

Sem formato obrigatório — jogue tudo junto. Quanto mais informação, melhor o resultado.
Clique em **Salvar dados** ao terminar.

---

### Passo 4 — Adicione currículos de referência *(opcional)*

Vá para a aba **Currículos de Referência** e envie arquivos `.pdf`, `.docx`, `.txt` ou `.md`.

Eles ajudam a IA a usar seu estilo de escrita e destacar experiências reais com mais precisão.

---

### Passo 5 — Gere o currículo

Vá para a aba **Gerar**, cole a descrição completa da vaga e clique em **Gerar currículo**.

Na barra lateral você pode ajustar:
- **Idioma do currículo** — Português, Inglês ou Espanhol
- **Formato de saída** — DOCX, PDF ou ambos
- **Modelo de IA** — veja modelos disponíveis em [openrouter.ai/models](https://openrouter.ai/models)

Após gerar, baixe o arquivo e revise antes de enviar.

---

### Passo 6 — Acesse seu histórico

Na aba **Histórico** você encontra todos os currículos gerados anteriormente para baixar novamente.

---

### Dicas

- Dados do perfil são cumulativos — vá adicionando informações ao longo do tempo para melhores resultados
- Sempre revise o currículo gerado antes de enviar
- Erro **401/403** → chave inválida ou sem permissão
- Erro **404** → modelo não encontrado, troque pelo nome correto em openrouter.ai/models
- Erro **429** → rate limit atingido, aguarde alguns segundos ou troque de modelo
""",
    "en": """
### Step 1 — Create an account or sign in

Create a free account or sign in from the panel in the sidebar.
With an account, your profile data, reference resumes and generation history are saved in the cloud.

---

### Step 2 — Set up your API Key

In the **sidebar**, paste your OpenRouter key (`sk-or-...`) and press **Enter**.

> No key yet? Create one for free at [openrouter.ai](https://openrouter.ai) → **Keys** → **Create Key** (no credit card needed).

---

### Step 3 — Add your profile data

Go to the **Profile Data** tab and dump everything about yourself:

- Work experience (company, role, period, responsibilities)
- Technical and soft skills
- Education, certifications, courses
- Personal projects and achievements

No format required — mix everything together. The more data, the better the result.
Click **Save data** when done.

---

### Step 4 — Add reference resumes *(optional)*

Go to the **Reference Resumes** tab and upload `.pdf`, `.docx`, `.txt` or `.md` files.

They help the AI match your writing style and highlight real experience more accurately.

---

### Step 5 — Generate the resume

Go to the **Generate** tab, paste the full job description and click **Generate resume**.

In the sidebar you can adjust:
- **Resume language** — Portuguese, English or Spanish
- **Output format** — DOCX, PDF or both
- **AI model** — browse available models at [openrouter.ai/models](https://openrouter.ai/models)

After generating, download the file and review it before sending.

---

### Step 6 — Access your history

In the **History** tab you can find all previously generated resumes to download again.

---

### Tips

- Profile data is cumulative — keep adding information over time for better results
- Always review the generated resume before sending it
- Error **401/403** → invalid key or missing permission
- Error **404** → model not found, replace with the correct name from openrouter.ai/models
- Error **429** → rate limit reached, wait a moment or switch models
""",
    "es": """
### Paso 1 — Crea una cuenta o inicia sesión

Crea una cuenta gratuita o inicia sesión desde el panel en la barra lateral.
Con cuenta, tus datos de perfil, CVs de referencia e historial de generaciones se guardan en la nube.

---

### Paso 2 — Configura tu API Key

En la **barra lateral**, pega tu clave de OpenRouter (`sk-or-...`) y presiona **Enter**.

> ¿No tienes clave? Créala gratis en [openrouter.ai](https://openrouter.ai) → **Keys** → **Create Key** (sin tarjeta de crédito).

---

### Paso 3 — Agrega tus datos de perfil

Ve a la pestaña **Datos del Perfil** y vuelca todo sobre ti:

- Experiencia laboral (empresa, cargo, período, responsabilidades)
- Habilidades técnicas y blandas
- Educación, certificaciones, cursos
- Proyectos personales y logros

Sin formato obligatorio — mezcla todo junto. Cuanta más información, mejor el resultado.
Haz clic en **Guardar datos** al terminar.

---

### Paso 4 — Agrega CVs de referencia *(opcional)*

Ve a la pestaña **CVs de Referencia** y sube archivos `.pdf`, `.docx`, `.txt` o `.md`.

Ayudan a la IA a usar tu estilo de escritura y destacar experiencias reales con más precisión.

---

### Paso 5 — Genera el currículum

Ve a la pestaña **Generar**, pega la descripción completa de la oferta y haz clic en **Generar currículum**.

En la barra lateral puedes ajustar:
- **Idioma del CV** — Portugués, Inglés o Español
- **Formato de salida** — DOCX, PDF o ambos
- **Modelo de IA** — consulta los modelos disponibles en [openrouter.ai/models](https://openrouter.ai/models)

Después de generar, descarga el archivo y revísalo antes de enviarlo.

---

### Paso 6 — Accede a tu historial

En la pestaña **Historial** encontrarás todos los currículums generados anteriormente para descargarlos de nuevo.

---

### Consejos

- Los datos del perfil son acumulativos — sigue añadiendo información con el tiempo para mejores resultados
- Siempre revisa el currículum generado antes de enviarlo
- Error **401/403** → clave inválida o sin permiso
- Error **404** → modelo no encontrado, reemplázalo con el nombre correcto en openrouter.ai/models
- Error **429** → límite de solicitudes alcanzado, espera un momento o cambia de modelo
""",
}


def render_tab_how_to(T: dict) -> None:
    st.markdown(f"### {T['tab_how_to_title']}")
    lang = st.session_state.get("ui_lang", "pt")
    st.markdown(_CONTENT.get(lang, _CONTENT["en"]))
