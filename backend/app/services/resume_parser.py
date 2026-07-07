"""
Resume Parser Service.

Responsibilities:
- Accept raw PDF bytes
- Extract clean, normalised text using PyMuPDF
- Validate file integrity and content presence
- Raise PDFParseError on failure
"""
import re
from typing import Final

import fitz  # PyMuPDF

from app.core.exceptions import PDFParseError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Minimum number of characters to consider a PDF "valid"
_MIN_CONTENT_LENGTH: Final[int] = 50


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract and clean plain text from PDF bytes.

    Args:
        pdf_bytes: Raw bytes of an uploaded PDF file.

    Returns:
        Cleaned extracted text string.

    Raises:
        PDFParseError: If the file is corrupt, encrypted, or yields no usable text.
    """
    if not pdf_bytes:
        raise PDFParseError("Received empty file. Please upload a valid PDF.")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        logger.error("PyMuPDF failed to open PDF", extra={"error": str(exc)})
        raise PDFParseError(f"Could not open PDF: {exc}") from exc

    if doc.is_encrypted:
        raise PDFParseError("The uploaded PDF is encrypted. Please provide an unlocked file.")

    pages_text: list[str] = []
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            pages_text.append(page.get_text("text"))
        except Exception as exc:
            logger.warning(
                "Skipping unreadable page",
                extra={"page": page_num, "error": str(exc)},
            )

    doc.close()

    raw_text = "\n".join(pages_text)
    cleaned = _clean_text(raw_text)

    if len(cleaned) < _MIN_CONTENT_LENGTH:
        raise PDFParseError(
            "PDF appears to contain no readable text. "
            "It may be a scanned image-only document."
        )

    logger.info(
        "PDF parsed successfully",
        extra={"char_count": len(cleaned), "pages": len(pages_text)},
    )
    return cleaned


def _clean_text(text: str) -> str:
    """
    Remove excessive whitespace, non-printable characters, normalise unicode control characters,
    soft hyphens, and stitch together words broken by line-breaks (e.g., Pan- das, Scikit- learn).
    """
    if not text:
        return ""

    # Replace soft hyphens (\xad, \u00ad) with empty string
    text = text.replace("\u00ad", "").replace("\xad", "")

    # Remove unicode control characters (except newline, tab, carriage return)
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\r\t")

    # Replace various unicode whitespace with a standard space
    text = re.sub(r"[\r\t\xa0\u2000-\u200a\u202f\u205f\u3000]", " ", text)

    # Stitch together words broken by line hyphenation
    # e.g., "Pan-\n das" or "Pan-\ndas" -> "Pandas"
    # e.g., "Scikit-\n learn" or "Scikit-\nlearn" -> "Scikit-learn"
    def merge_hyphenated(match):
        w1 = match.group(1)
        w2 = match.group(2)
        combined_lower = (w1 + w2).lower()
        # "scikitlearn" should retain its hyphen
        if combined_lower == "scikitlearn":
            return "Scikit-learn"
        # Other common hyphenated tech terms
        if combined_lower in ["nodejs", "nextjs"]:
            return f"{w1}-{w2}"
        # Default: merge without hyphen (e.g., Pandas, PyTorch)
        return w1 + w2

    # Match letters, a hyphen, optional space, newline, optional space, then letters
    text = re.sub(r"([a-zA-Z]+)-\s*\n\s*([a-zA-Z]+)", merge_hyphenated, text)

    # Replace strange PDF separators (like bullet points or non-breaking symbols) with spaces
    text = re.sub(r"[\u2022\u25cf\u25aa\u25b6\u2219]", " ", text)

    # Collapse multiple blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces on the same line
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
