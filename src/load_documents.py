from pathlib import Path
import re

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_PATH = Path("docs")


def clean_text(text: str) -> str:
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()
    return clean_text(full_text)


def load_all_documents():
    pdf_files = sorted(DOCS_PATH.glob("*.pdf"))

    if not pdf_files:
        return []

    documents = []

    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)

        if text.strip():
            documents.append({
                "source": pdf_file.name,
                "text": text
            })

    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = []

    for doc in documents:
        split_texts = splitter.split_text(doc["text"])

        for i, chunk_text in enumerate(split_texts):
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "source": doc["source"],
                    "chunk_id": i
                }
            })

    return chunks