"""Extract plain text from small, text-based PDF and DOCX resumes.

Uploads are processed in memory and are not persisted to disk or database.
"""

from io import BytesIO
from pathlib import PurePath
from zipfile import BadZipFile, ZipFile

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader

MAX_RESUME_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 30
MAX_EXTRACTED_CHARS = 100_000
MAX_DOCX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024
MAX_DOCX_ZIP_MEMBERS = 1500


class ResumeExtractionError(ValueError):
    """User-correctable upload or text-extraction error."""


def _clean_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def _extract_pdf(data: bytes) -> tuple[str, list[str]]:
    if not data.startswith(b"%PDF-"):
        raise ResumeExtractionError("The uploaded file is not a valid PDF.")

    try:
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise ResumeExtractionError("Password-protected PDF files are not supported.")
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ResumeExtractionError(f"PDF exceeds the {MAX_PDF_PAGES}-page limit.")

        pages: list[str] = []
        chars = 0
        for page in reader.pages:
            text = _clean_text(page.extract_text() or "")
            chars += len(text)
            if chars > MAX_EXTRACTED_CHARS:
                raise ResumeExtractionError("Resume contains too much text to process.")
            if text:
                pages.append(text)
    except ResumeExtractionError:
        raise
    except Exception as exc:
        raise ResumeExtractionError("Could not read this PDF. Try exporting it again.") from exc

    result = "\n\n".join(pages)
    if not result:
        raise ResumeExtractionError(
            "No selectable text was found in this PDF. Scanned/image-only PDFs need OCR, which is not supported yet."
        )
    return result, []


def _extract_docx(data: bytes) -> tuple[str, list[str]]:
    if not data.startswith(b"PK\x03\x04"):
        raise ResumeExtractionError("The uploaded file is not a valid DOCX document.")

    try:
        with ZipFile(BytesIO(data)) as archive:
            members = archive.infolist()
            names = {member.filename for member in members}
            if not {"[Content_Types].xml", "word/document.xml"}.issubset(names):
                raise ResumeExtractionError("This ZIP file is not a DOCX document.")
            if len(members) > MAX_DOCX_ZIP_MEMBERS or sum(
                member.file_size for member in members
            ) > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise ResumeExtractionError("The DOCX contains too much embedded data.")
            if any(member.flag_bits & 0x1 for member in members):
                raise ResumeExtractionError("Encrypted DOCX files are not supported.")

        document = Document(BytesIO(data))
        parts: list[str] = []
        for item in document.iter_inner_content():
            if isinstance(item, Paragraph):
                text = item.text.strip()
                if text:
                    parts.append(text)
            elif isinstance(item, Table):
                for row in item.rows:
                    cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if cells:
                        parts.append(" | ".join(cells))

        result = _clean_text("\n".join(parts))
    except ResumeExtractionError:
        raise
    except (BadZipFile, KeyError, ValueError, OSError) as exc:
        raise ResumeExtractionError("Could not read this DOCX. Try exporting it again.") from exc

    if len(result) > MAX_EXTRACTED_CHARS:
        raise ResumeExtractionError("Resume contains too much text to process.")
    if not result:
        raise ResumeExtractionError("No readable text was found in this DOCX document.")
    return result, []


def extract_resume(filename: str, data: bytes) -> dict:
    """Validate a resume and return extracted text for user review."""
    safe_name = (filename or "").replace("\\", "/").split("/")[-1]
    extension = PurePath(safe_name).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise ResumeExtractionError("Only .pdf and .docx resumes are supported.")
    if not data:
        raise ResumeExtractionError("The uploaded file is empty.")
    if len(data) > MAX_RESUME_BYTES:
        raise ResumeExtractionError("Resume exceeds the 5 MB upload limit.")

    text, warnings = _extract_pdf(data) if extension == ".pdf" else _extract_docx(data)
    return {
        "filename": safe_name,
        "file_type": extension.removeprefix("."),
        "file_size_bytes": len(data),
        "character_count": len(text),
        "extracted_text": text,
        "warnings": warnings,
    }
