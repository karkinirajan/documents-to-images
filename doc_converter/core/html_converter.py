"""
HTML conversion utilities for converting HTML to PDF.
"""

import logging
import os
from pathlib import Path
from typing import Any

import pdfkit

from ..utils.config import Config

logger = logging.getLogger(__name__)


class HTMLConverter:
    """
    Handles HTML to PDF conversions using pdfkit (wkhtmltopdf).
    """

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize HTML converter.

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self.wkhtmltopdf_path = self._find_wkhtmltopdf()
        logger.info("HTMLConverter initialized")

    def _find_wkhtmltopdf(self) -> str | None:
        """
        Find wkhtmltopdf executable path.

        Returns:
            Path to wkhtmltopdf executable or None if not found
        """
        possible_paths = [
            "wkhtmltopdf",
            "/usr/bin/wkhtmltopdf",
            "/usr/local/bin/wkhtmltopdf",
            "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",
            "C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",
        ]

        for path in possible_paths:
            if os.path.isfile(path) or self._which(path):
                logger.info(f"Found wkhtmltopdf at: {path}")
                return path

        logger.warning("wkhtmltopdf not found in standard locations")
        return None

    def _which(self, program: str) -> bool:
        """
        Check if a program exists in PATH.

        Args:
            program: Program name to check

        Returns:
            True if program exists in PATH
        """
        import shutil

        return shutil.which(program) is not None

    def to_pdf(
        self,
        html_source: str,
        output_path: str | Path,
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Convert HTML to PDF.

        Args:
            html_source: HTML file path or URL
            output_path: Path for output PDF file
            options: Additional pdfkit options

        Returns:
            Path to the created PDF file

        Raises:
            RuntimeError: If wkhtmltopdf not found or conversion fails
        """
        try:
            output_path = Path(output_path)

            logger.info(f"Converting HTML to PDF: {html_source}")
            logger.info(f"Output: {output_path}")

            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Default options
            default_options = {
                "page-size": "A4",
                "margin-top": "0.75in",
                "margin-right": "0.75in",
                "margin-bottom": "0.75in",
                "margin-left": "0.75in",
                "encoding": "UTF-8",
                "no-outline": None,
                "enable-local-file-access": None,
            }

            # Merge with user options
            if options:
                default_options.update(options)

            # Configuration for pdfkit
            config = None
            if self.wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)

            # Determine if input is URL or file path
            if html_source.startswith(("http://", "https://")):
                # URL
                logger.info(f"Converting URL: {html_source}")
                pdfkit.from_url(
                    html_source,
                    str(output_path),
                    options=default_options,
                    configuration=config,
                )
            else:
                # File path
                html_path = Path(html_source)
                if not html_path.exists():
                    raise FileNotFoundError(f"HTML file not found: {html_path}")

                logger.info(f"Converting HTML file: {html_path}")
                pdfkit.from_file(
                    str(html_path),
                    str(output_path),
                    options=default_options,
                    configuration=config,
                )

            if not output_path.exists():
                raise RuntimeError(f"PDF was not created: {output_path}")

            logger.info(f"Successfully created PDF: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert HTML to PDF: {e}")
            if "No wkhtmltopdf executable found" in str(e):
                raise RuntimeError(
                    "wkhtmltopdf not found. Please install wkhtmltopdf:\n"
                    "Ubuntu/Debian: sudo apt-get install wkhtmltopdf\n"
                    "macOS: brew install wkhtmltopdf\n"
                    "Windows: Download from https://wkhtmltopdf.org/downloads.html"
                ) from e
            raise

    def from_string(
        self,
        html_string: str,
        output_path: str | Path,
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Convert HTML string directly to PDF.

        Args:
            html_string: HTML content as string
            output_path: Path for output PDF file
            options: Additional pdfkit options

        Returns:
            Path to the created PDF file
        """
        try:
            output_path = Path(output_path)

            logger.info("Converting HTML string to PDF")
            logger.info(f"Output: {output_path}")

            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Default options
            default_options = {
                "page-size": "A4",
                "margin-top": "0.75in",
                "margin-right": "0.75in",
                "margin-bottom": "0.75in",
                "margin-left": "0.75in",
                "encoding": "UTF-8",
                "no-outline": None,
            }

            # Merge with user options
            if options:
                default_options.update(options)

            # Configuration for pdfkit
            config = None
            if self.wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)

            # Convert HTML string to PDF
            pdfkit.from_string(
                html_string,
                str(output_path),
                options=default_options,
                configuration=config,
            )

            if not output_path.exists():
                raise RuntimeError(f"PDF was not created: {output_path}")

            logger.info(f"Successfully created PDF: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert HTML string to PDF: {e}")
            raise
