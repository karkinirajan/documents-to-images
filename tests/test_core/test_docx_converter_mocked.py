"""
Tests for DOCX converter functionality.
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from doc_converter.core.docx_converter import DOCXConverter


class TestDOCXConverter:
    @pytest.fixture
    def converter(self):
        """Create a DOCXConverter instance for testing."""
        with patch.object(DOCXConverter, "_find_libreoffice", return_value="libreoffice"):
            return DOCXConverter()

    @pytest.fixture
    def sample_docx_path(self):
        """Path to a sample DOCX file."""
        return Path("tests/fixtures/sample.docx")

    @pytest.fixture
    def sample_txt_path(self):
        """Path to a sample TXT file."""
        return Path("tests/fixtures/sample.txt")

    @pytest.fixture
    def output_path(self, tmp_path):
        """Temporary output file path."""
        return tmp_path / "output.pdf"

    def test_converter_initialization(self, converter):
        """Test DOCXConverter initialization."""
        assert converter is not None
        assert converter.libreoffice_cmd == "libreoffice"

    def test_find_libreoffice_success(self):
        """Test finding LibreOffice executable."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            converter = DOCXConverter()
            assert converter.libreoffice_cmd in ["libreoffice", "lowriter"]

    def test_find_libreoffice_not_found(self):
        """Test LibreOffice not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="LibreOffice not found"):
                DOCXConverter()

    @patch("subprocess.run")
    def test_to_pdf_success(self, mock_run, converter, sample_docx_path, output_path):
        """Test successful DOCX to PDF conversion."""
        # Mock successful subprocess run
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Create the expected PDF file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()

        result = converter.to_pdf(sample_docx_path, output_path)

        assert result == str(output_path)
        mock_run.assert_called_once()

        # Verify the command includes correct parameters
        call_args = mock_run.call_args[0][0]
        assert "libreoffice" in call_args
        assert "--headless" in call_args
        assert "--convert-to" in call_args
        assert "pdf" in call_args

    @patch("subprocess.run")
    def test_to_pdf_conversion_fails(self, mock_run, converter, sample_docx_path, output_path):
        """Test failed DOCX to PDF conversion."""
        # Mock failed subprocess run
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Conversion failed")

        with pytest.raises(subprocess.CalledProcessError):
            converter.to_pdf(sample_docx_path, output_path)

    @patch("subprocess.run")
    def test_to_pdf_timeout(self, mock_run, converter, sample_docx_path, output_path):
        """Test DOCX to PDF conversion timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["libreoffice"], timeout=300)

        with pytest.raises(RuntimeError, match="Conversion timed out"):
            converter.to_pdf(sample_docx_path, output_path)

    @patch("mammoth.convert_to_html")
    @patch("builtins.open", new_callable=mock_open)
    def test_to_html_success(self, mock_file, mock_mammoth, converter, sample_docx_path, tmp_path):
        """Test successful DOCX to HTML conversion."""
        # Mock mammoth conversion
        mock_result = Mock()
        mock_result.value = "<html><body>Test content</body></html>"
        mock_result.messages = []
        mock_mammoth.return_value = mock_result

        html_path = tmp_path / "output.html"

        result = converter.to_html(sample_docx_path, html_path)

        assert result == str(html_path)
        mock_mammoth.assert_called_once()
        mock_file.assert_called()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="Test content\nSecond line\n",
    )
    def test_txt_to_pdf_success(self, mock_file, converter, sample_txt_path, output_path):
        """Test successful TXT to PDF conversion."""
        with patch("doc_converter.core.docx_converter.FPDF") as mock_fpdf:
            mock_pdf_instance = Mock()
            mock_fpdf.return_value = mock_pdf_instance

            # Make the output file exist after conversion
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch()

            result = converter.txt_to_pdf(sample_txt_path, output_path)

            assert result == str(output_path)
            mock_pdf_instance.add_page.assert_called_once()
            mock_pdf_instance.set_font.assert_called_once()
            mock_pdf_instance.output.assert_called_once_with(str(output_path))

    def test_txt_to_pdf_file_not_found(self, converter, tmp_path):
        """Test TXT to PDF conversion with non-existent file."""
        non_existent = tmp_path / "non_existent.txt"
        output_path = tmp_path / "output.pdf"

        with pytest.raises(OSError):  # a missing input file is an OSError (FileNotFoundError)
            converter.txt_to_pdf(non_existent, output_path)
