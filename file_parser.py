from __future__ import annotations

from io import BytesIO

from flask import Request
from PyPDF2 import PdfReader

ALLOWED_EXTENSIONS = {"pdf", "txt"}


def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_resume_text(request: Request) -> str:
    pasted = (request.form.get("resume_text") or "").strip()
    if pasted:
        return pasted

    file = request.files.get("resume_file")
    if not file or not file.filename:
        raise ValueError("Please upload a resume file or paste resume text.")

    if not _is_allowed(file.filename):
        raise ValueError("Only PDF and TXT files are supported.")

    ext = file.filename.rsplit(".", 1)[1].lower()
    data = file.read()

    if ext == "txt":
        text = data.decode("utf-8", errors="ignore").strip()
        if not text:
            raise ValueError("TXT file is empty.")
        return text

    if ext == "pdf":
        try:
            reader = PdfReader(BytesIO(data))
            chunks = [(page.extract_text() or "").strip() for page in reader.pages]
            text = "\n".join([c for c in chunks if c]).strip()
            if not text:
                raise ValueError("Could not extract text from PDF. Try a text-based PDF or paste text.")
            return text
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Failed to read PDF. Try another file or paste text.") from exc

    raise ValueError("Unsupported file type.")
