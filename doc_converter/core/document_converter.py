"""
Main Document Converter class that orchestrates all conversion operations.
"""

import logging
from pathlib import Path
from typing import Any

from ..utils.config import Config
from ..utils.file_handler import FileHandler
from .docx_converter import DOCXConverter
from .html_converter import HTMLConverter
from .pdf_converter import PDFConverter

logger = logging.getLogger(__name__)


class DocumentConverter:
    """
    Main class for document conversion operations.

    This class provides a unified interface for converting between various
    document formats including PDF, DOCX, HTML, and images.
    """

    def __init__(self, config_path: Config | str | Path | None = None) -> None:
        """
        Initialize the DocumentConverter.

        Args:
            config_path: Path to configuration file (optional)
        """
        # accept a ready-made Config (as BatchProcessor passes) as well as a file path
        self.config = config_path if isinstance(config_path, Config) else Config(config_path)
        self.file_handler = FileHandler()

        # Initialize specific converters
        self.pdf_converter = PDFConverter(self.config)
        self.docx_converter = DOCXConverter(self.config)
        self.html_converter = HTMLConverter(self.config)

        logger.info("DocumentConverter initialized")

    def pdf_to_images(
        self,
        pdf_path: str | Path,
        output_dir: str | Path | None = None,
        format: str = "jpeg",
        dpi: int = 200,
    ) -> list[str]:
        """
        Convert PDF pages to image files.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Output directory for images (optional)
            format: Output format ('jpeg', 'png')
            dpi: Resolution in DPI

        Returns:
            List of created image file paths

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If invalid format specified
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if format not in ["jpeg", "png"]:
            raise ValueError(f"Unsupported format: {format}")

        if output_dir is None:
            output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        return self.pdf_converter.to_images(pdf_path, output_dir, format, dpi)

    def docx_to_pdf(
        self,
        docx_path: str | Path,
        output_path: str | Path | None = None,
    ) -> str:
        """
        Convert DOCX file to PDF.

        Args:
            docx_path: Path to the DOCX file
            output_path: Output PDF path (optional)

        Returns:
            Path to the created PDF file

        Raises:
            FileNotFoundError: If DOCX file doesn't exist
        """
        docx_path = Path(docx_path)

        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        if output_path is None:
            output_path = docx_path.parent / f"{docx_path.stem}.pdf"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        return self.docx_converter.to_pdf(docx_path, output_path)

    def pptx_to_pdf(
        self,
        pptx_path: str | Path,
        output_path: str | Path | None = None,
    ) -> str:
        """
        Convert PPTX file to PDF.

        Args:
            pptx_path: Path to the PPTX file
            output_path: Output PDF path (optional)

        Returns:
            Path to the created PDF file

        Raises:
            FileNotFoundError: If PPTX file doesn't exist
        """
        pptx_path = Path(pptx_path)

        if not pptx_path.exists():
            raise FileNotFoundError(f"PPTX file not found: {pptx_path}")

        if output_path is None:
            output_path = pptx_path.parent / f"{pptx_path.stem}.pdf"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        return self.docx_converter.to_pdf(pptx_path, output_path)  # LibreOffice handles PPTX

    def txt_to_pdf(
        self,
        txt_path: str | Path,
        output_path: str | Path | None = None,
    ) -> str:
        """
        Convert TXT file to PDF.

        Args:
            txt_path: Path to the TXT file
            output_path: Output PDF path (optional)

        Returns:
            Path to the created PDF file

        Raises:
            FileNotFoundError: If TXT file doesn't exist
        """
        txt_path = Path(txt_path)

        if not txt_path.exists():
            raise FileNotFoundError(f"TXT file not found: {txt_path}")

        if output_path is None:
            output_path = txt_path.parent / f"{txt_path.stem}.pdf"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        return self.docx_converter.txt_to_pdf(txt_path, output_path)

    def html_to_pdf(
        self,
        html_source: str,
        output_path: str | Path,
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Convert HTML to PDF.

        Args:
            html_source: HTML file path or URL
            output_path: Output PDF path
            options: Additional conversion options

        Returns:
            Path to the created PDF file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return self.html_converter.to_pdf(html_source, output_path, options)

    def docx_to_html(
        self,
        docx_path: str | Path,
        output_path: str | Path | None = None,
    ) -> str:
        """
        Convert DOCX file to HTML.

        Args:
            docx_path: Path to the DOCX file
            output_path: Output HTML path (optional)

        Returns:
            Path to the created HTML file

        Raises:
            FileNotFoundError: If DOCX file doesn't exist
        """
        docx_path = Path(docx_path)

        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        if output_path is None:
            output_path = docx_path.parent / f"{docx_path.stem}.html"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        return self.docx_converter.to_html(docx_path, output_path)

    def get_supported_formats(self) -> dict[str, list[str]]:
        """
        Get dictionary of supported input and output formats.

        Returns:
            Dictionary with 'input' and 'output' format lists
        """
        return {
            "input": ["pdf", "docx", "pptx", "txt", "html"],
            "output": ["pdf", "html", "jpeg", "png"],
        }
