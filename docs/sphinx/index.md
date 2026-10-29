# Documents to Images Converter

A comprehensive Python toolkit for converting various document formats into images and other formats.

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api
cli
examples
troubleshooting
contributing
changelog
```

## Features

- **PDF to Images**: Convert PDF pages to high-quality JPEG/PNG images
- **DOCX to PDF**: Convert Word documents to PDF format  
- **PPTX to PDF**: Convert PowerPoint presentations to PDF
- **TXT to PDF**: Convert plain text files to formatted PDF
- **HTML to PDF**: Convert HTML files or web pages to PDF
- **DOCX to HTML**: Convert Word documents to HTML format
- **Batch Processing**: Convert multiple files at once with progress tracking
- **Command Line Interface**: Easy-to-use CLI tools
- **Programmatic API**: Full Python API for custom workflows

## Quick Start

### Installation

```bash
pip install documents-to-images-converter
```

### Basic Usage

```python
from doc_converter import DocumentConverter

converter = DocumentConverter()

# Convert PDF to images
images = converter.pdf_to_images("document.pdf", format="jpeg", dpi=300)

# Convert DOCX to PDF
pdf = converter.docx_to_pdf("document.docx")

# Convert HTML to PDF
converter.html_to_pdf("https://example.com", "webpage.pdf")
```

### Command Line

```bash
# Convert PDF to images
doc-converter pdf-to-images input.pdf --format jpeg --dpi 300

# Batch convert documents to PDF
doc-converter batch-convert --input-dir ./docs --format pdf
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`