"""
File handling utilities.
"""

import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Utility class for file and directory operations.
    """

    @staticmethod
    def ensure_directory(path: str | Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Directory path

        Returns:
            Path object for the directory
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean a filename by removing/replacing invalid characters.

        Args:
            filename: Original filename

        Returns:
            Cleaned filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Remove leading/trailing dots and spaces
        filename = filename.strip(". ")

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            max_name_length = 255 - len(ext)
            filename = name[:max_name_length] + ext

        return filename

    @staticmethod
    def get_file_size(path: str | Path) -> int:
        """
        Get file size in bytes.

        Args:
            path: File path

        Returns:
            File size in bytes
        """
        return Path(path).stat().st_size

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)

        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1

        return f"{size:.1f} {size_names[i]}"

    @staticmethod
    def copy_file(src: str | Path, dst: str | Path) -> Path:
        """
        Copy a file to destination.

        Args:
            src: Source file path
            dst: Destination file path

        Returns:
            Destination path
        """
        src = Path(src)
        dst = Path(dst)

        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        logger.info(f"Copied file: {src} -> {dst}")

        return dst

    @staticmethod
    def move_file(src: str | Path, dst: str | Path) -> Path:
        """
        Move a file to destination.

        Args:
            src: Source file path
            dst: Destination file path

        Returns:
            Destination path
        """
        src = Path(src)
        dst = Path(dst)

        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(src, dst)
        logger.info(f"Moved file: {src} -> {dst}")

        return dst

    @staticmethod
    def delete_file(path: str | Path) -> None:
        """
        Delete a file.

        Args:
            path: File path to delete
        """
        path = Path(path)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted file: {path}")

    @staticmethod
    def find_files(
        directory: str | Path,
        patterns: list[str],
        recursive: bool = True,
    ) -> list[Path]:
        """
        Find files matching patterns in directory.

        Args:
            directory: Directory to search
            patterns: File patterns (e.g., ['*.pdf', '*.docx'])
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        directory = Path(directory)
        files: list[Path] = []

        for pattern in patterns:
            if recursive:
                files.extend(directory.rglob(pattern))
            else:
                files.extend(directory.glob(pattern))

        return sorted(list(set(files)))

    @staticmethod
    def get_temp_file(suffix: str = "", prefix: str = "doc_converter_") -> Path:
        """
        Get a temporary file path.

        Args:
            suffix: File suffix (e.g., '.pdf')
            prefix: File prefix

        Returns:
            Path to temporary file
        """
        import tempfile

        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # Close file descriptor, but keep the path
        return Path(path)

    @staticmethod
    def create_backup(path: str | Path) -> Path:
        """
        Create a backup copy of a file.

        Args:
            path: File path to backup

        Returns:
            Path to backup file
        """
        path = Path(path)
        backup_path = path.with_suffix(f"{path.suffix}.backup")

        counter = 1
        while backup_path.exists():
            backup_path = path.with_suffix(f"{path.suffix}.backup.{counter}")
            counter += 1

        shutil.copy2(path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        return backup_path
