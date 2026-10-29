"""
DOCX conversion utilities for converting DOCX files to various formats.
"""

import logging
import subprocess
from pathlib import Path

import mammoth
from fpdf import FPDF

from ..utils.config import Config

logger = logging.getLogger(__name__)


class DOCXConverter:
    """
    Handles DOCX conversions using LibreOffice and other libraries.
    """

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize DOCX converter.

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self.libreoffice_cmd = self._find_libreoffice()
        logger.info("DOCXConverter initialized")

    def _find_libreoffice(self) -> str:
        """
        Find LibreOffice executable path.

        Returns:
            Path to LibreOffice executable

        Raises:
            RuntimeError: If LibreOffice not found
        """
        possible_paths = [
            "libreoffice",
            "lowriter",
            "/usr/bin/libreoffice",
            "/usr/bin/lowriter",
            "/opt/libreoffice/program/soffice",
            "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
            "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"Found LibreOffice at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        raise RuntimeError(
            "LibreOffice not found. Please install LibreOffice and ensure it's in PATH."
        )

    def to_pdf(self, input_path: str | Path, output_path: str | Path) -> str:
        """
        Convert DOCX/PPTX file to PDF using LibreOffice.

        Args:
            input_path: Path to input file (DOCX, PPTX, etc.)
            output_path: Path for output PDF file

        Returns:
            Path to the created PDF file

        Raises:
            subprocess.CalledProcessError: If conversion fails
            RuntimeError: If LibreOffice not available
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            logger.info(f"Converting {input_path} to PDF using LibreOffice")

            # Create output directory if it doesn't exist
            output_dir = output_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Run LibreOffice conversion
            cmd = [
                self.libreoffice_cmd,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(input_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode != 0:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                raise subprocess.CalledProcessError(
                    result.returncode, cmd, result.stdout, result.stderr
                )

            # LibreOffice creates file with same name as input but .pdf
            # extension
            generated_pdf = output_dir / f"{input_path.stem}.pdf"

            # Rename to desired output name if different
            if generated_pdf != output_path:
                if generated_pdf.exists():
                    generated_pdf.rename(output_path)

            if not output_path.exists():
                raise RuntimeError(f"PDF was not created: {output_path}")

            logger.info(f"Successfully created PDF: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired as e:
            logger.error("LibreOffice conversion timed out")
            raise RuntimeError("Conversion timed out after 5 minutes") from e
        except Exception as e:
            logger.error(f"Failed to convert to PDF: {e}")
            raise

    def to_html(self, docx_path: str | Path, html_path: str | Path) -> str:
        """
        Convert DOCX file to HTML using mammoth.

        Args:
            docx_path: Path to DOCX file
            html_path: Path for output HTML file

        Returns:
            Path to the created HTML file

        Raises:
            Exception: If conversion fails
        """
        try:
            docx_path = Path(docx_path)
            html_path = Path(html_path)

            logger.info(f"Converting DOCX to HTML: {docx_path}")

            # Create output directory if it doesn't exist
            html_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert using mammoth
            with open(docx_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)

                # Write HTML content
                with open(html_path, "w", encoding="utf-8") as html_file:
                    html_file.write(result.value)

                # Log any messages from mammoth
                if result.messages:
                    for message in result.messages:
                        logger.warning(f"Mammoth message: {message}")

            logger.info(f"Successfully created HTML: {html_path}")
            return str(html_path)

        except Exception as e:
            logger.error(f"Failed to convert DOCX to HTML: {e}")
            raise

    def txt_to_pdf(self, txt_path: str | Path, pdf_path: str | Path) -> str:
        """
        Convert TXT file to PDF using FPDF.

        Args:
            txt_path: Path to TXT file
            pdf_path: Path for output PDF file

        Returns:
            Path to the created PDF file

        Raises:
            Exception: If conversion fails
        """
        try:
            txt_path = Path(txt_path)
            pdf_path = Path(pdf_path)

            logger.info(f"Converting TXT to PDF: {txt_path}")

            # Create output directory if it doesn't exist
            pdf_path.parent.mkdir(parents=True, exist_ok=True)

            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)

            # Read text file and add to PDF
            with open(txt_path, encoding="utf-8", errors="ignore") as txt_file:
                for line in txt_file:
                    # Handle encoding issues and long lines
                    try:
                        # Remove or replace problematic characters
                        line = line.encode("latin1", errors="replace").decode("latin1")
                        line = line.rstrip("\n\r")

                        # Split long lines
                        while len(line) > 80:
                            pdf.cell(
                                0, 10, text=line[:80], new_x="LMARGIN", new_y="NEXT", align="L"
                            )
                            line = line[80:]

                        if line:
                            pdf.cell(0, 10, text=line, new_x="LMARGIN", new_y="NEXT", align="L")
                    except Exception as line_error:
                        logger.warning(f"Skipped problematic line: {line_error}")
                        continue

            # Save PDF
            pdf.output(str(pdf_path))

            logger.info(f"Successfully created PDF: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"Failed to convert TXT to PDF: {e}")
            raise
