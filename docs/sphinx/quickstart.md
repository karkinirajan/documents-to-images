# Quick Start Guide

Get up and running with the Documents to Images Converter in minutes.

## Basic Examples

### Converting PDF to Images

```python
from doc_converter import DocumentConverter

converter = DocumentConverter()

# Single file conversion
images = converter.pdf_to_images("document.pdf")

# With custom settings
images = converter.pdf_to_images(
    "document.pdf",
    format="jpeg",  # 'jpeg' or 'png'
    dpi=300,  # Image resolution
    first_page=1,  # Start page
    last_page=5,  # End page
)

print(f"Generated {len(images)} images")
```

### Converting Documents to PDF

```python
# Word document to PDF
pdf_path = converter.docx_to_pdf("document.docx")

# PowerPoint to PDF
pdf_path = converter.pptx_to_pdf("presentation.pptx")

# Text file to PDF
pdf_path = converter.txt_to_pdf("notes.txt")
```

### HTML to PDF Conversion

```python
# Convert HTML file
converter.html_to_pdf("report.html", "report.pdf")

# Convert web page
converter.html_to_pdf("https://example.com", "webpage.pdf")
```

### Batch Processing

```python
from doc_converter import BatchProcessor

batch = BatchProcessor()

# Convert all PDFs in a directory to images
batch.batch_convert(input_dir="./documents", output_dir="./images", operation="pdf_to_images")

# Convert all DOCX files to PDF
batch.batch_convert(input_dir="./word_docs", output_dir="./pdfs", operation="docx_to_pdf")
```

## Command Line Usage

### Basic Commands

```bash
# Convert PDF to images
doc-converter pdf-to-images input.pdf

# Convert with options
doc-converter pdf-to-images input.pdf --format jpeg --dpi 300 --output-dir ./images

# Convert DOCX to PDF
doc-converter docx-to-pdf document.docx

# Batch convert
doc-converter batch-convert --input-dir ./docs --format pdf
```

### Available Commands

- `pdf-to-images`: Convert PDF pages to image files
- `docx-to-pdf`: Convert Word documents to PDF
- `pptx-to-pdf`: Convert PowerPoint presentations to PDF
- `txt-to-pdf`: Convert text files to PDF
- `html-to-pdf`: Convert HTML files or URLs to PDF
- `docx-to-html`: Convert Word documents to HTML
- `batch-convert`: Process multiple files at once

## Configuration

Create a config file for default settings:

```yaml
# config.yaml
pdf_to_images:
  format: jpeg
  dpi: 300
  
output:
  base_dir: ./output
  create_subdirs: true
  
logging:
  level: INFO
  file: converter.log
```

Use the config:

```python
from doc_converter import DocumentConverter

converter = DocumentConverter(config_file="config.yaml")
```

## Error Handling

```python
from doc_converter import DocumentConverter, ConversionError

converter = DocumentConverter()

try:
    images = converter.pdf_to_images("document.pdf")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except FileNotFoundError:
    print("File not found")
```

## Next Steps

- Check out the [API Reference](api.md) for detailed documentation
- See more [Examples](examples.md) for advanced usage
- Learn about [CLI options](cli.md) for command-line usage
- Read [Troubleshooting](troubleshooting.md) for common issues