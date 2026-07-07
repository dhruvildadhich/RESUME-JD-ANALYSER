"""
Tests for ResumeParserService.
"""
import io
import pytest

from app.core.exceptions import PDFParseError
from app.services.resume_parser import extract_text_from_pdf, _clean_text


class TestCleanText:
    def test_collapses_extra_spaces(self):
        result = _clean_text("hello   world")
        assert result == "hello world"

    def test_collapses_multiple_blank_lines(self):
        result = _clean_text("line1\n\n\n\nline2")
        assert result == "line1\n\nline2"

    def test_strips_whitespace(self):
        result = _clean_text("  hello  ")
        assert result == "hello"

    def test_replaces_tab_with_space(self):
        result = _clean_text("col1\tcol2")
        assert "col1 col2" == result

    def test_merges_hyphenated_line_breaks(self):
        # Pan-\ndas -> Pandas
        result = _clean_text("Pan-\ndas")
        assert result == "Pandas"

        # Scikit-\nlearn -> Scikit-learn
        result2 = _clean_text("Scikit-\nlearn")
        assert result2 == "Scikit-learn"


class TestExtractTextFromPDF:
    def test_raises_on_empty_bytes(self):
        with pytest.raises(PDFParseError) as exc_info:
            extract_text_from_pdf(b"")
        assert "empty file" in str(exc_info.value.detail).lower()

    def test_raises_on_invalid_pdf(self):
        with pytest.raises(PDFParseError):
            extract_text_from_pdf(b"not a pdf at all")

    def test_raises_on_non_pdf_bytes(self):
        # A JPEG magic number — not a PDF
        jpeg_bytes = bytes([0xFF, 0xD8, 0xFF, 0xE0] + [0x00] * 100)
        with pytest.raises(PDFParseError):
            extract_text_from_pdf(jpeg_bytes)
