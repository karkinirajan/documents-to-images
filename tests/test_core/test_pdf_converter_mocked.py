"""
Tests for PDF converter functionality.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from doc_converter.core.pdf_converter import PDFConverter


class TestPDFConverter:
    @pytest.fixture
    def converter(self):
        """Create a PDFConverter instance for testing."""
        return PDFConverter()

    @pytest.fixture
    def sample_pdf_path(self):
        """Path to a sample PDF file."""
        return Path("tests/fixtures/sample.pdf")

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Temporary output directory."""
        return tmp_path / "images"

    def test_converter_initialization(self, converter):
        """Test PDFConverter initialization."""
        assert converter is not None
        assert converter.config is None

    def test_converter_with_config(self):
        """Test PDFConverter initialization with config."""
        mock_config = Mock()
        converter = PDFConverter(mock_config)
        assert converter.config == mock_config

    @patch("doc_converter.core.pdf_converter.convert_from_path")
    def test_to_images_success(self, mock_convert, converter, sample_pdf_path, output_dir):
        """Test successful PDF to images conversion."""
        # Mock the pdf2image conversion
        mock_image = Mock()
        mock_convert.return_value = [mock_image, mock_image]

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        result = converter.to_images(
            pdf_path=sample_pdf_path,
            output_dir=output_dir,
            format="jpeg",
            dpi=200,
        )

        # Verify conversion was called with correct parameters
        mock_convert.assert_called_once_with(
            sample_pdf_path, dpi=200, first_page=None, last_page=None
        )

        # Verify images were saved
        mock_image.save.assert_called()
        assert len(result) == 2

    def test_to_images_invalid_format(self, converter, sample_pdf_path, output_dir):
        """Test PDF to images conversion with invalid format."""
        with pytest.raises(Exception):  # noqa: B017  - the exact type depends on pdf2image/Pillow
            converter.to_images(
                pdf_path=sample_pdf_path,
                output_dir=output_dir,
                format="invalid_format",
            )

    @patch("doc_converter.core.pdf_converter.convert_from_path")
    def test_to_images_with_page_range(self, mock_convert, converter, sample_pdf_path, output_dir):
        """Test PDF to images conversion with specific page range."""
        mock_image = Mock()
        mock_convert.return_value = [mock_image]

        output_dir.mkdir(parents=True, exist_ok=True)

        converter.to_images(
            pdf_path=sample_pdf_path,
            output_dir=output_dir,
            first_page=1,
            last_page=1,
        )

        mock_convert.assert_called_once_with(sample_pdf_path, dpi=200, first_page=1, last_page=1)

    @patch("pypdf.PdfReader")
    def test_get_page_count_success(self, mock_pdf_reader, converter, sample_pdf_path):
        """Test getting page count from PDF."""
        mock_reader = Mock()
        mock_reader.pages = [Mock(), Mock(), Mock()]  # 3 pages
        mock_pdf_reader.return_value = mock_reader

        count = converter.get_page_count(sample_pdf_path)

        assert count == 3
        mock_pdf_reader.assert_called_once_with(str(sample_pdf_path))

    @patch("pypdf.PdfReader")
    @patch("doc_converter.core.pdf_converter.convert_from_path")
    def test_get_page_count_fallback(
        self, mock_convert, mock_pdf_reader, converter, sample_pdf_path
    ):
        """Test getting page count with fallback method."""
        # Make PdfReader fail
        mock_pdf_reader.side_effect = Exception("PDF reader failed")

        # Mock fallback method
        mock_convert.return_value = [Mock(), Mock()]  # 2 pages

        count = converter.get_page_count(sample_pdf_path)

        assert count == 2
        mock_convert.assert_called_once()

    def test_extract_page_range(self, converter, sample_pdf_path, output_dir):
        """Test extracting specific page range."""
        with patch.object(converter, "to_images") as mock_to_images:
            mock_to_images.return_value = ["page1.jpg", "page2.jpg"]

            result = converter.extract_page_range(
                pdf_path=sample_pdf_path,
                output_dir=output_dir,
                start_page=2,
                end_page=3,
                format="jpeg",
                dpi=300,
            )

            mock_to_images.assert_called_once_with(
                pdf_path=sample_pdf_path,
                output_dir=output_dir,
                format="jpeg",
                dpi=300,
                first_page=2,
                last_page=3,
            )

            assert result == ["page1.jpg", "page2.jpg"]
