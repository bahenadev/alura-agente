# Asistente RAG

Asistente de问答 basado en Retrieval-Augmented Generation (RAG) para consultar documentos internos de la empresa. Permite subir archivos PDF, generar embeddings vectoriales y hacer preguntas en lenguaje natural que el agente responde utilizando exclusivamente el contenido de los documentos indexados.

## Despliegue en OCI (Evidencia)

**Instancia:** oci-free-1
**Estado:** En ejecución
**IP Pública:** 163.192.159.18
**IP Privada:** 10.0.0.225
**Shape:** VM.Standard.A1.Flex (1 OCPU / 6 GB RAM)
**Availability Domain:** AD-1
**Fault Domain:** FD-1
**Fecha de creación:** 19 jul 2026, 21:07:46 UTC

**URL de la app:** [http://163.192.159.18:8501](http://163.192.159.18:8501)

### Captura del despliegue

<!-- Pegar aquí la captura de pantalla de la consola OCI mostrando la instancia en ejecución -->
![Evidencia de despliegue en OCI](docs/evidencia-oci.png)

### Captura de la app funcionando

<!-- Pegar aquí la captura de pantalla de la app en el navegador -->
![App Asistente RAG funcionando](docs/evidencia-app.png)

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interfaz (Streamlit)                     │
│                                                                 │
│   ┌──────────────┐    ┌──────────────────────────────────────┐  │
│   │  Chat         │    │  Documentos                          │  │
│   │  - Título     │    │  - Uploader de PDFs                  │  │
│   │  - Historial  │    │  - Lista de archivos                 │  │
│   │  - Input      │    │  - Botón de indexación                │  │
│   └──────┬───────┘    └──────────────┬───────────────────────┘  │
│          │                           │                          │
└──────────┼───────────────────────────┼──────────────────────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────────────────────┐
│   Agente (LLM)      │    │   Pipeline de Indexación              │
│                     │    │                                       │
│   Cohere Command-R  │    │   PDF → Loader → Splitter → Embeddings│
│   + Prompt RAG      │    │        PyPDF    RecursiveChar   Cohere│
│   + Contexto        │    │                                       │
└──────────┬──────────┘    └──────────────┬───────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ChromaDB (Vector Store)                        │
│                                                                  │
│   Colección: rag_documents                                       │
│   Embeddings: Cohere embed-v4.0                                  │
│   Búsqueda: similarity_search_with_relevance_scores (TOP_K=3)   │
│   Filtro: MIN_SCORE=0.3                                          │
└──────────────────────────────────────────────────────────────────┘
```

### Flujo de una consulta

1. El usuario escribe una pregunta en el chat.
2. `retriever.py` busca los 3 fragmentos más relevantes en ChromaDB con score >= 0.3.
3. `agent.py` construye un prompt con los fragmentos como contexto.
4. El LLM (Cohere Command-R) genera una respuesta basándose exclusivamente en el contexto.
5. La respuesta se muestra en el chat, incluyendo las fuentes consultadas.

### Flujo de indexación

1. `file_manager.py` guarda los PDFs subidos en `docs/pdfs/`.
2. `build_index.py` compara hashes SHA-256 de los PDFs contra el manifest anterior.
3. Si hay cambios, `load_documents.py` carga los PDFs y los fragmenta (chunk_size=1000, overlap=150).
4. `build_index.py` genera embeddings con Cohere embed-v4.0 y los almacena en ChromaDB.

## Estructura del proyecto

```
alura-agente/
├── .env                          # Variables de entorno (COHERE_API_KEY)
├── requirements.txt              # Dependencias
├── requirements-lock.txt         # Dependencias con versiones fijas
├── docs/
│   └── pdfs/                     # Documentos PDF fuente
│       ├── backend.pdf
│       ├── frontend.pdf
│       ├── incidentes.pdf
│       ├── microservicios.pdf
│       └── onboarding.pdf
└── src/
    ├── app.py                    # Entry point, navegación multipage
    ├── chat_page.py              # Página Chat (st.bottom.chat_input)
    ├── docs_page.py              # Página Documentos (uploader + indexación)
    ├── agent.py                  # LLM + prompt RAG + detección de saludos
    ├── retriever.py              # Búsqueda vectorial en ChromaDB
    ├── build_index.py            # Pipeline de indexación + manifest SHA-256
    ├── load_documents.py         # Carga y fragmentación de PDFs
    ├── file_manager.py           # Gestión de archivos PDF en disco
    └── chroma_db/                # Base vectorial (generada, no commiteada)
```

## Tecnologías

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Interfaz | Streamlit | 1.60.0 |
| LLM | Cohere Command-R | command-r7b-12-2024 |
| Embeddings | Cohere embed-v4.0 | embed-v4.0 |
| Vector Store | ChromaDB | 1.5.9 |
| Framework RAG | LangChain | 1.3.14 |
| Carga de PDFs | PyPDF | 6.14.2 |
| Fragmentación | RecursiveCharacterTextSplitter | 1.1.2 |
| Variables de entorno | python-dotenv | 1.2.2 |

## Ejecución local

### Requisitos

- Python 3.12+
- Una API key de Cohere (gratuita en [cohere.com](https://cohere.com))

### Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd alura-agente

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements-lock.txt

# Configurar la API key
echo 'COHERE_API_KEY="tu-clave-aqui"' > .env
```

### Ejecutar

```bash
cd src
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

### Indexar documentos

1. Ir a la página **Documentos** (sidebar izquierda).
2. Subir PDFs con el uploader, o colocarlos directamente en `docs/pdfs/`.
3. Hacer clic en **Preparar embeddings**.
4. Esperar a que termine la indexación.

## Ejemplos de preguntas

El asistente puede responder preguntas sobre el contenido de los documentos PDF indexados. Aquí hay ejemplos basados en los documentos de ejemplo (backend, frontend, incidentes, microservicios, onboarding):

| Pregunta | Tema |
|----------|------|
| ¿Cuáles son las buenas prácticas para el backend? | Backend |
| ¿Cómo se estructura el frontend de la aplicación? | Frontend |
| ¿Qué hacer ante un incidente en producción? | Incidentes |
| ¿Qué son los microservicios y cómo se comunican? | Microservicios |
| ¿Cuál es el proceso de onboarding de un nuevo empleado? | Onboarding |
| ¿Qué tecnologías se usan en el proyecto? | Stack tecnológico |
| ¿Cuáles son los pasos para desplegar una nueva versión? | Deploy |
| ¿Qué métricas se monitorean en producción? | Observabilidad |

## Ejemplos de respuestas

**Pregunta:** ¿Cuáles son las buenas prácticas para el backend?

> Según el documento, las buenas prácticas para el backend incluyen:
>
> - Separar la lógica de negocio de las rutas HTTP.
> - Usar middleware para autenticación y logging.
> - Implementar validación de entrada en todos los endpoints.
> - Mantener una estructura de capas clara: controlador → servicio → repositorio.
>
> **Fuentes:** backend.pdf

---

**Pregunta:** ¿Qué hacer ante un incidente en producción?

> En caso de un incidente en producción, el proceso documentado establece:
>
> 1. Identificar y clasificar la severidad del incidente.
> 2. Notificar al equipo de on-call según el protocolo.
> 3. Crear un ticket de incidente con toda la información relevante.
> 4. Ejecutar las acciones de mitigación inmediatas.
> 5. Realizar un post-mortem después de la resolución.
>
> **Fuentes:** incidentes.pdf

---

**Pregunta:** ¿Cómo me llamo?

> No lo sé con la información disponible en los documentos.

*(El agente solo responde con base en los documentos indexados y no utiliza conocimiento externo.)*

---

**Pregunta:** Hola

> ¡Hola! Soy tu asistente de documentos internos. Hazme una pregunta sobre los documentos y con gusto te ayudaré.

*(El agente detecta saludos y responde de forma amigable sin consultar la base de datos.)*

## Despliegue en Oracle Cloud (OCI)

```bash
# En el VM de OCI
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

git clone <url-del-repositorio> /opt/asistente-rag
cd /opt/asistente-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt

# Configurar variable de entorno
export COHERE_API_KEY="tu-clave-aqui"

# Ejecutar
cd src
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

Abrir el puerto 8501 en la security list de la VCN de OCI.

## Licencia

Proyecto privado. Uso interno de la empresa.
