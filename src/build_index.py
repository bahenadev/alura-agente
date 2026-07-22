import json
import hashlib
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"
STATE_DIR = BASE_DIR / ".index_state"
MANIFEST_PATH = STATE_DIR / "manifest.json"
COLLECTION_NAME = "rag_documents"

EMBEDDING_MODEL = "embed-v4.0"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def _asegurar_directorios():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _hash_archivo(path: Path) -> str:
    sha256 = hashlib.sha256()

    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            sha256.update(bloque)

    return sha256.hexdigest()


def _construir_manifest_actual() -> dict:
    archivos = sorted(DOCS_DIR.glob("*.pdf"))
    manifest = {}

    for archivo in archivos:
        stat = archivo.stat()
        manifest[archivo.name] = {
            "sha256": _hash_archivo(archivo),
            "size_bytes": stat.st_size,
            "mtime": stat.st_mtime,
        }

    return manifest


def _leer_manifest_guardado() -> dict:
    if not MANIFEST_PATH.exists():
        return {}

    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_manifest(manifest: dict) -> None:
    _asegurar_directorios()

    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _obtener_info_base_vectorial() -> dict:
    _asegurar_directorios()

    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        colecciones = client.list_collections()
        nombres = [c.name for c in colecciones]

        if COLLECTION_NAME not in nombres:
            return {
                "existe": False,
                "cantidad_registros": 0,
                "colecciones_disponibles": nombres,
            }

        collection = client.get_collection(name=COLLECTION_NAME)
        cantidad = collection.count()

        return {
            "existe": cantidad > 0,
            "cantidad_registros": cantidad,
            "colecciones_disponibles": nombres,
        }
    except Exception:
        return {
            "existe": False,
            "cantidad_registros": 0,
            "colecciones_disponibles": [],
        }


def _base_vectorial_existe_y_tiene_datos() -> bool:
    info = _obtener_info_base_vectorial()
    return info["existe"]


def obtener_estado_embeddings() -> dict:
    _asegurar_directorios()

    manifest_actual = _construir_manifest_actual()
    manifest_guardado = _leer_manifest_guardado()
    info_base = _obtener_info_base_vectorial()

    hay_pdfs = len(manifest_actual) > 0
    base_ok = info_base["existe"]
    hay_manifest_guardado = bool(manifest_guardado)
    manifest_iguales = manifest_actual == manifest_guardado

    if not hay_pdfs:
        razon = "no_hay_pdfs"
        permitir = False
    elif not base_ok:
        razon = "primer_embedding"
        permitir = True
    elif not hay_manifest_guardado:
        razon = "falta_manifest"
        permitir = True
    elif not manifest_iguales:
        razon = "documentos_cambiaron"
        permitir = True
    else:
        razon = "sin_cambios"
        permitir = False

    return {
        "permitir_embedding": permitir,
        "razon": razon,
        "hay_pdfs": hay_pdfs,
        "base_vectorial_existe": base_ok,
        "cantidad_registros": info_base["cantidad_registros"],
        "colecciones_disponibles": info_base["colecciones_disponibles"],
        "manifest_actual_total": len(manifest_actual),
        "manifest_guardado_total": len(manifest_guardado),
        "manifest_iguales": manifest_iguales,
    }


def obtener_resumen_indexacion() -> dict:
    estado = obtener_estado_embeddings()

    return {
        "inicializado": estado["base_vectorial_existe"],
        "total_archivos_indexados": estado["manifest_guardado_total"],
        "base_vectorial_lista": estado["base_vectorial_existe"],
        "cantidad_registros": estado["cantidad_registros"],
        "razon": estado["razon"],
    }


def hay_cambios_pendientes() -> bool:
    estado = obtener_estado_embeddings()
    return estado["permitir_embedding"]


def _cargar_y_fragmentar_documentos():
    archivos_pdf = sorted(DOCS_DIR.glob("*.pdf"))

    if not archivos_pdf:
        raise ValueError("No hay archivos PDF en la carpeta docs.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    documentos_fragmentados = []

    for archivo in archivos_pdf:
        loader = PyPDFLoader(str(archivo))
        documentos = loader.load()

        for doc in documentos:
            doc.metadata["source_file"] = archivo.name

        chunks = splitter.split_documents(documentos)
        documentos_fragmentados.extend(chunks)

    return archivos_pdf, documentos_fragmentados


def build_index() -> dict:
    _asegurar_directorios()

    estado = obtener_estado_embeddings()

    if not estado["hay_pdfs"]:
        raise ValueError("No hay archivos PDF en la carpeta docs.")

    if not estado["permitir_embedding"]:
        return {
            "status": "sin_cambios",
            "archivos_procesados": 0,
            "chunks_generados": 0,
        }

    archivos_pdf, documentos_fragmentados = _cargar_y_fragmentar_documentos()

    embeddings = CohereEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    if estado["base_vectorial_existe"]:
        existentes = vectorstore.get()

        if existentes and existentes.get("ids"):
            vectorstore.delete(ids=existentes["ids"])

    ids = [
        f"{doc.metadata.get('source_file', 'doc')}::{i}"
        for i, doc in enumerate(documentos_fragmentados)
    ]

    if documentos_fragmentados:
        vectorstore.add_documents(documents=documentos_fragmentados, ids=ids)

    _guardar_manifest(_construir_manifest_actual())

    return {
        "status": "ok",
        "archivos_procesados": len(archivos_pdf),
        "chunks_generados": len(documentos_fragmentados),
    }