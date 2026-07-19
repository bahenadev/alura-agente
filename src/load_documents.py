from pathlib import Path
from pypdf import PdfReader

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


if __name__ == "__main__":
    # Ejecuta la función principal para cargar todos los documentos.
    documents = load_all_documents()

    # Imprime cuántos documentos se cargaron en total.
    print(f"\nTotal de documentos cargados: {len(documents)}")