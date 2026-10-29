"""
Batch processing utilities for handling multiple file conversions.
"""

import logging
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ..utils.config import Config
from .document_converter import DocumentConverter

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Handles batch conversion operations with progress tracking and parallel processing.
    """

    def __init__(self, config: Config | None = None, max_workers: int = 4) -> None:
        """
        Initialize batch processor.

        Args:
            config: Configuration object (optional)
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.config = config
        self.max_workers = max_workers
        self.converter = DocumentConverter(config)
        self._progress_lock = threading.Lock()
        logger.info(f"BatchProcessor initialized with {max_workers} workers")

    def convert_directory(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        target_format: str,
        file_patterns: list[str] | None = None,
        recursive: bool = True,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        """
        Convert all supported files in a directory to target format.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files
            target_format: Target format ('pdf', 'html', 'jpeg', 'png')
            file_patterns: File patterns to include (e.g., ['*.docx', '*.pdf'])
            recursive: Whether to process subdirectories
            progress_callback: Callback function for progress updates (current, total, filename)

        Returns:
            Dictionary with conversion results and statistics
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting batch conversion: {input_dir} -> {output_dir}")
        logger.info(f"Target format: {target_format}")

        # Find all files to process
        files_to_process = self._find_files(input_dir, file_patterns, recursive)

        if not files_to_process:
            logger.warning("No files found to process")
            return {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "results": [],
                "errors": [],
            }

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process files
        return self._process_files_parallel(
            files_to_process, output_dir, target_format, progress_callback
        )

    def convert_file_list(
        self,
        file_list: list[str | Path],
        output_dir: str | Path,
        target_format: str,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        """
        Convert a specific list of files to target format.

        Args:
            file_list: List of file paths to convert
            output_dir: Directory for output files
            target_format: Target format ('pdf', 'html', 'jpeg', 'png')
            progress_callback: Callback function for progress updates

        Returns:
            Dictionary with conversion results and statistics
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Filter existing files
        existing_files = [Path(f) for f in file_list if Path(f).exists()]

        if len(existing_files) != len(file_list):
            missing_files = set(file_list) - set(str(f) for f in existing_files)
            logger.warning(f"Some files not found: {missing_files}")

        logger.info(f"Processing {len(existing_files)} files")

        return self._process_files_parallel(
            existing_files, output_dir, target_format, progress_callback
        )

    def _find_files(
        self, directory: Path, patterns: list[str] | None, recursive: bool
    ) -> list[Path]:
        """
        Find files matching the specified patterns.

        Args:
            directory: Directory to search
            patterns: File patterns (e.g., ['*.docx', '*.pdf'])
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        if patterns is None:
            # Default supported extensions
            patterns = ["*.pdf", "*.docx", "*.pptx", "*.txt", "*.html"]

        files: list[Path] = []

        for pattern in patterns:
            if recursive:
                files.extend(directory.rglob(pattern))
            else:
                files.extend(directory.glob(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        logger.info(f"Found {len(files)} files matching patterns: {patterns}")
        return files

    def _process_files_parallel(
        self,
        files: list[Path],
        output_dir: Path,
        target_format: str,
        progress_callback: Callable[[int, int, str], None] | None,
    ) -> dict[str, Any]:
        """
        Process files in parallel using ThreadPoolExecutor.

        Args:
            files: List of files to process
            output_dir: Output directory
            target_format: Target format
            progress_callback: Progress callback function

        Returns:
            Processing results
        """
        results: dict[str, Any] = {
            "total_files": len(files),
            "successful": 0,
            "failed": 0,
            "results": [],
            "errors": [],
        }

        completed_count = 0

        def update_progress(filename: str = "") -> None:
            nonlocal completed_count
            with self._progress_lock:
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, len(files), filename)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self._convert_single_file,
                    file_path,
                    output_dir,
                    target_format,
                ): file_path
                for file_path in files
            }

            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    result = future.result()
                    results["successful"] += 1
                    results["results"].append(result)
                    logger.info(f"Successfully processed: {file_path.name}")

                except Exception as e:
                    error_info = {"file": str(file_path), "error": str(e)}
                    results["failed"] += 1
                    results["errors"].append(error_info)
                    logger.error(f"Failed to process {file_path.name}: {e}")

                finally:
                    update_progress(file_path.name)

        logger.info(
            f"Batch processing completed: "
            f"{results['successful']} successful, {results['failed']} failed"
        )

        return results

    def _convert_single_file(
        self, input_file: Path, output_dir: Path, target_format: str
    ) -> dict[str, Any]:
        """
        Convert a single file to the target format.

        Args:
            input_file: Input file path
            output_dir: Output directory
            target_format: Target format

        Returns:
            Conversion result information

        Raises:
            Exception: If conversion fails
        """
        input_ext = input_file.suffix.lower().lstrip(".")

        # Determine output filename
        if target_format in ["jpeg", "png"]:
            # For image formats, create subdirectory for each file
            file_output_dir = output_dir / f"{input_file.stem}_images"
            file_output_dir.mkdir(parents=True, exist_ok=True)

            if input_ext == "pdf":
                output_files = self.converter.pdf_to_images(
                    input_file, file_output_dir, target_format
                )
                return {
                    "input_file": str(input_file),
                    "output_files": output_files,
                    "format": target_format,
                    "type": "multiple_images",
                }
            else:
                raise ValueError(f"Cannot convert {input_ext} to {target_format}")

        else:
            # Single file output
            output_file = output_dir / f"{input_file.stem}.{target_format}"

            if target_format == "pdf":
                if input_ext == "docx":
                    result_path = self.converter.docx_to_pdf(input_file, output_file)
                elif input_ext == "pptx":
                    result_path = self.converter.pptx_to_pdf(input_file, output_file)
                elif input_ext == "txt":
                    result_path = self.converter.txt_to_pdf(input_file, output_file)
                elif input_ext == "html":
                    result_path = self.converter.html_to_pdf(str(input_file), output_file)
                else:
                    raise ValueError(f"Cannot convert {input_ext} to PDF")

            elif target_format == "html":
                if input_ext == "docx":
                    result_path = self.converter.docx_to_html(input_file, output_file)
                else:
                    raise ValueError(f"Cannot convert {input_ext} to HTML")

            else:
                raise ValueError(f"Unsupported target format: {target_format}")

            return {
                "input_file": str(input_file),
                "output_file": result_path,
                "format": target_format,
                "type": "single_file",
            }
