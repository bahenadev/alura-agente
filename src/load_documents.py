from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Ruta a la carpeta donde guardaste los PDFs del proyecto.
# Path("docs") significa: busca una carpeta llamada "docs"
# dentro del lugar donde estés ejecutando este script.
DOCS_PATH = Path("docs")


def extract_text_from_pdf(pdf_path: Path) -> str:
    # Crea un lector de PDF usando la ruta que recibe la función.
    # PdfReader abre el archivo y permite acceder a sus páginas.
    reader = PdfReader(pdf_path)

    # Lista vacía donde vamos a guardar el texto de cada página.
    text_parts = []

    # Recorre una por una todas las páginas del PDF.
    for page in reader.pages:
        # Extrae el texto de la página actual.
        # Si la página tiene texto seleccionable, lo devuelve como string.
        # Si no tiene texto, puede devolver None o una cadena vacía.
        page_text = page.extract_text()

        # Solo guardamos el texto si realmente existe.
        # Esto evita meter valores vacíos o None en la lista.
        if page_text:
            text_parts.append(page_text)

    # Une todos los textos de las páginas en un solo string.
    # "\n" pone un salto de línea entre cada página.
    # .strip() quita espacios o saltos de línea sobrantes al inicio y al final.
    return "\n".join(text_parts).strip()


def load_all_documents():
    # Busca todos los archivos .pdf dentro de la carpeta docs/
    # glob("*.pdf") significa: "todos los archivos que terminen en .pdf"
    # sorted(...) los ordena para procesarlos siempre en el mismo orden.
    pdf_files = sorted(DOCS_PATH.glob("*.pdf"))

    # Si no encontró ningún PDF, muestra un mensaje y devuelve una lista vacía.
    if not pdf_files:
        print("No se encontraron PDFs en la carpeta docs/")
        return []

    # Lista donde vamos a guardar cada documento como un diccionario.
    documents = []

    # Recorre cada archivo PDF encontrado.
    for pdf_file in pdf_files:
        # Extrae el texto completo del PDF actual.
        text = extract_text_from_pdf(pdf_file)

        # Muestra el nombre del archivo y cuántos caracteres se extrajeron.
        # Esto sirve para comprobar que sí leyó texto.
        print(f"{pdf_file.name}: {len(text)} caracteres extraídos")

        # Guarda la información del documento en un diccionario:
        # source = nombre del archivo
        # text = texto completo extraído
        documents.append({
            "source": pdf_file.name,
            "text": text
        })

    # Devuelve la lista completa de documentos cargados.
    return documents

def chunk_documents(documents):
    # Creamos el divisor de texto.
    # chunk_size=1000 significa que cada chunk tendrá aprox. 1000 caracteres.
    # chunk_overlap=200 significa que cada chunk comparte 200 caracteres
    # con el chunk anterior para no perder contexto.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Aquí guardaremos todos los chunks generados.
    chunks = []

    # Recorremos cada documento cargado.
    for doc in documents:
        # Dividimos el texto completo del documento en varios chunks.
        split_texts = splitter.split_text(doc["text"])

        # Recorremos cada chunk generado.
        for i, chunk_text in enumerate(split_texts):
            # Guardamos el chunk junto con su metadata.
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "source": doc["source"],  # nombre del PDF
                    "chunk_id": i             # número del chunk en ese PDF
                }
            })

    # Regresamos la lista completa de chunks.
    return chunks


if __name__ == "__main__":
    # Ejecuta la función principal para cargar todos los documentos.
    documents = load_all_documents()

    # Imprime cuántos documentos se cargaron en total.
    print(f"\nTotal de documentos cargados: {len(documents)}")
    
    chunks = chunk_documents(documents)
    print(f"Total de chunks creados: {len(chunks)}")
    print("=== 3 chunks de ejemplo ===")
    for chunk in chunks[:3]:
        print(f"Fuente: {chunk['metadata']['source']}")
        print(f"Chunk ID: {chunk['metadata']['chunk_id']}")
        print(chunk["content"][:500])  # solo mostramos los primeros 500 caracteres
        print("-" * 80)