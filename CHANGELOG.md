# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- The package raised a `SyntaxError` on import under Python 3.10 and 3.11 (a multi-line expression inside an f-string in `pdf_converter.py`), so it never worked on the Python versions it claimed to support.
- `Config` shallow-copied its class-level defaults, so `set()` or loading a file changed the defaults for every later `Config` in the process; it now deep-copies.
- `BatchProcessor(config=Config(...))` crashed because the `Config` object was handed to `DocumentConverter` as if it were a file path; `DocumentConverter` now accepts a `Config` as well as a path.
- CLI errors are written to stderr (they went to stdout) and `main()` accepts an `argv` list; the "output directory" message shows the real default directory.
- Re-raised exceptions are now chained (`raise ... from e`).

### Changed
- Python 3.10 or newer is required (3.8 and 3.9 are end-of-life); tested on 3.10 to 3.13.
- TXT to PDF uses the current `fpdf2` API (`text=`, `new_x`/`new_y`) instead of the deprecated `txt=`/`ln=`; `fpdf2>=2.8.2`.
- `PyPDF2` (deprecated) replaced by `pypdf`.
- Tooling: ruff (lint and format) replaces black, isort and flake8; `mypy` strict now passes; one `tests/` directory; deprecation warnings from the package are errors in tests instead of being ignored.

### Added
- A real test suite (112 tests, about 94% coverage; previously about 19% from placeholder tests), including real PDF to image and DOCX to PDF conversions when poppler and LibreOffice are installed.

### Removed
- Placeholder tests, a duplicate `documents-to-images-converter/` tree, and committed Sphinx build output.

## [1.0.0] - 2025-01-XX

### Initial Release

#### Added
- Core document conversion functionality
- PDF to images conversion (JPEG, PNG)
- Document to PDF conversions (DOCX, PPTX, TXT, HTML)
- DOCX to HTML conversion
- Command line interface
- Python API
- Batch processing
- Configuration management
- Comprehensive documentation
- Test suite with high coverage

#### System Requirements
- Python 3.8+
- Poppler (for PDF processing)
- LibreOffice (optional, for enhanced DOCX/PPTX conversion)

#### Supported Formats

##### Input Formats
- PDF
- DOCX (Microsoft Word)
- PPTX (Microsoft PowerPoint)
- TXT (Plain text)
- HTML (Local files and URLs)

##### Output Formats
- JPEG images
- PNG images
- PDF
- HTML

#### Breaking Changes
- None (initial release)

#### Known Issues
- Large PDF files may require substantial memory
- HTML to PDF conversion depends on web rendering engine
- Some complex DOCX formatting may not be preserved perfectly
- wkhtmltopdf dependency deprecated on macOS (functionality limited)