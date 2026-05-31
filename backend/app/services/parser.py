import io
from fastapi import UploadFile, HTTPException


def _sanitize(text: str) -> str:
    # Postgres TEXT rejects null bytes; strip them out after PDF extraction
    return text.replace("\x00", "")


async def extract_text(file: UploadFile) -> str:
    content = await file.read()
    filename = file.filename or ""

    if filename.endswith(".pdf"):
        return _sanitize(_extract_pdf(content))
    elif filename.endswith(".docx"):
        return _sanitize(_extract_docx(content))
    else:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")


def _extract_pdf(content: bytes) -> str:
    import pdfplumber

    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise HTTPException(status_code=422, detail="Could not extract text from PDF. The file may be image-based.")
    return full_text


def _extract_docx(content: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs).strip()
    if not full_text:
        raise HTTPException(status_code=422, detail="Could not extract text from DOCX.")
    return full_text
