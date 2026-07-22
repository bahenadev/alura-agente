from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR.parent / "docs"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_and_chunk_documents():
    archivos_pdf = sorted(DOCS_DIR.glob("*.pdf"))

    if not archivos_pdf:
        raise ValueError("No hay archivos PDF en la carpeta docs.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
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
