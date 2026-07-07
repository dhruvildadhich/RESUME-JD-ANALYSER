"""
Domain-specific HTTP exceptions for the Resume-JD Matcher.
Each exception maps to a meaningful HTTP status code and carries
a structured detail payload for consistent API error responses.
"""
from fastapi import HTTPException, status


class PDFParseError(HTTPException):
    """Raised when PyMuPDF cannot extract text from the uploaded file."""

    def __init__(self, detail: str = "Failed to parse PDF file.") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"error": "pdf_parse_error", "message": detail},
        )


class GeminiAPIError(HTTPException):
    """Raised when the Gemini API call fails or returns unexpected output."""

    def __init__(self, detail: str = "Gemini API request failed.") -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "gemini_api_error", "message": detail},
        )


class EmbeddingError(HTTPException):
    """Raised when embedding generation fails."""

    def __init__(self, detail: str = "Failed to generate embeddings.") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "embedding_error", "message": detail},
        )


class FileSizeLimitError(HTTPException):
    """Raised when the uploaded file exceeds the configured size limit."""

    def __init__(self, max_mb: int = 10) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large",
                "message": f"PDF must be smaller than {max_mb} MB.",
            },
        )
