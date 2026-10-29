"""
PDF conversion utilities for converting PDFs to images.
"""

import logging
from pathlib import Path

from pdf2image import convert_from_path

from ..utils.config import Config

logger = logging.getLogger(__name__)


class PDFConverter:
    """
    Handles PDF to image conversions using pdf2image library.
    """

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize PDF converter.

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        logger.info("PDFConverter initialized")

    def to_images(
        self,
        pdf_path: str | Path,
        output_dir: str | Path,
        format: str = "jpeg",
        dpi: int = 200,
        first_page: int | None = None,
        last_page: int | None = None,
    ) -> list[str]:
        """
        Convert PDF pages to image files.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save image files
            format: Output format ('jpeg', 'png')
            dpi: Resolution in DPI
            first_page: First page to convert (1-indexed, optional)
            last_page: Last page to convert (1-indexed, optional)

        Returns:
            List of created image file paths

        Raises:
            Exception: If conversion fails
        """
        try:
            pdf_path = Path(pdf_path)
            output_dir = Path(output_dir)

            logger.info(f"Converting PDF to images: {pdf_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Format: {format}, DPI: {dpi}")

            # Convert PDF to images
            # pdf2image annotates the page arguments as `int` although None (its default) means
            # "no limit", which is what we pass through.
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=first_page,  # type: ignore[arg-type]
                last_page=last_page,  # type: ignore[arg-type]
            )

            output_files = []

            # Save each page as an image
            for i, image in enumerate(images):
                page_num = (first_page or 1) + i
                filename = f"page_{page_num:03d}.{format.lower()}"
                output_path = output_dir / filename

                # Save with appropriate format and quality
                if format.lower() == "jpeg":
                    image.save(output_path, "JPEG", quality=95, optimize=True)
                elif format.lower() == "png":
                    image.save(output_path, "PNG", optimize=True)
                else:
                    image.save(output_path, format.upper())

                output_files.append(str(output_path))
                logger.info(f"Saved: {output_path}")

            logger.info(f"Successfully converted {len(images)} pages to {format}")
            return output_files

        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise

    def get_page_count(self, pdf_path: str | Path) -> int:
        """
        Get the number of pages in a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Number of pages in the PDF

        Raises:
            Exception: If unable to read PDF
        """
        try:
            from pypdf import PdfReader

            pdf_path = Path(pdf_path)
            reader = PdfReader(str(pdf_path))
            page_count = len(reader.pages)

            logger.info(f"PDF {pdf_path.name} has {page_count} pages")
            return page_count

        except Exception as e:
            logger.error(f"Failed to get page count: {e}")
            # Fallback: try with pdf2image
            try:
                images = convert_from_path(pdf_path, dpi=50)  # Low DPI for speed
                return len(images)
            except Exception as e2:
                logger.error(f"Fallback method also failed: {e2}")
                raise e2 from e

    def extract_page_range(
        self,
        pdf_path: str | Path,
        output_dir: str | Path,
        start_page: int,
        end_page: int,
        format: str = "jpeg",
        dpi: int = 200,
    ) -> list[str]:
        """
        Extract a specific range of pages from PDF as images.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save image files
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed)
            format: Output format ('jpeg', 'png')
            dpi: Resolution in DPI

        Returns:
            List of created image file paths
        """
        return self.to_images(
            pdf_path=pdf_path,
            output_dir=output_dir,
            format=format,
            dpi=dpi,
            first_page=start_page,
            last_page=end_page,
        )
