# API Reference

## DocumentConverter Class

The main class for document conversion operations.

### Constructor

```python
DocumentConverter(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (str, optional): Path to configuration file

### Methods

#### `pdf_to_images(pdf_path, output_dir=None, format='jpeg', dpi=200)`

Convert PDF pages to image files.

**Parameters:**
- `pdf_path` (str|Path): Path to the PDF file
- `output_dir` (str|Path, optional): Output directory for images
- `format` (str): Output format ('jpeg', 'png')
- `dpi` (int): Resolution in DPI

**Returns:**
- `List[str]`: List of created image file paths

**Raises:**
- `FileNotFoundError`: If PDF file doesn't exist
- `ValueError`: If invalid format specified

**Example:**
```python
from doc_converter import DocumentConverter

converter = DocumentConverter()
images = converter.pdf_to_images("document.pdf", output_dir="./images", format="jpeg", dpi=300)
print(f"Created {len(images)} images")
```

#### `docx_to_pdf(docx_path, output_path=None)`

Convert DOCX file to PDF.

**Parameters:**
- `docx_path` (str|Path): Path to the DOCX file
- `output_path` (str|Path, optional): Output PDF path

**Returns:**
- `str`: Path to the created PDF file

**Raises:**
- `FileNotFoundError`: If DOCX file doesn't exist

**Example:**
```python
converter = DocumentConverter()
pdf_path = converter.docx_to_pdf("document.docx", "output.pdf")
```

#### `pptx_to_pdf(pptx_path, output_path=None)`

Convert PPTX file to PDF.

**Parameters:**
- `pptx_path` (str|Path): Path to the PPTX file
- `output_path` (str|Path, optional): Output PDF path

**Returns:**
- `str`: Path to the created PDF file

#### `txt_to_pdf(txt_path, output_path=None)`

Convert TXT file to PDF.

**Parameters:**
- `txt_path` (str|Path): Path to the TXT file
- `output_path` (str|Path, optional): Output PDF path

**Returns:**
- `str`: Path to the created PDF file

#### `html_to_pdf(html_source, output_path, options=None)`

Convert HTML to PDF.

**Parameters:**
- `html_source` (str): HTML file path or URL
- `output_path` (str|Path): Output PDF path
- `options` (dict, optional): Additional conversion options

**Returns:**
- `str`: Path to the created PDF file

**Example:**
```python
# Convert local HTML file
converter.html_to_pdf("page.html", "output.pdf")

# Convert URL
converter.html_to_pdf("https://example.com", "webpage.pdf")

# With custom options
options = {"page-size": "A4", "margin-top": "1in"}
converter.html_to_pdf("page.html", "output.pdf", options=options)
```

#### `docx_to_html(docx_path, output_path=None)`

Convert DOCX file to HTML.

**Parameters:**
- `docx_path` (str|Path): Path to the DOCX file
- `output_path` (str|Path, optional): Output HTML path

**Returns:**
- `str`: Path to the created HTML file

#### `get_supported_formats()`

Get dictionary of supported input and output formats.

**Returns:**
- `Dict[str, List[str]]`: Dictionary with 'input' and 'output' format lists

---

## BatchProcessor Class

Handles batch conversion operations with progress tracking.

### Constructor

```python
BatchProcessor(config=None, max_workers=4)
```

**Parameters:**
- `config`: Configuration object (optional)
- `max_workers` (int): Maximum number of worker threads

### Methods

#### `convert_directory(input_dir, output_dir, target_format, file_patterns=None, recursive=True, progress_callback=None)`

Convert all supported files in a directory to target format.

**Parameters:**
- `input_dir` (str|Path): Directory containing input files
- `output_dir` (str|Path): Directory for output files
- `target_format` (str): Target format ('pdf', 'html', 'jpeg', 'png')
- `file_patterns` (List[str], optional): File patterns to include
- `recursive` (bool): Whether to process subdirectories
- `progress_callback` (Callable, optional): Progress callback function

**Returns:**
- `Dict[str, Any]`: Dictionary with conversion results and statistics

**Example:**
```python
from doc_converter.core.batch_processor import BatchProcessor

processor = BatchProcessor(max_workers=2)


def progress_callback(current, total, filename):
    print(f"Progress: {current}/{total} - {filename}")


results = processor.convert_directory(
    input_dir="./documents",
    output_dir="./converted",
    target_format="pdf",
    progress_callback=progress_callback,
)

print(f"Converted {results['successful']} files successfully")
```

---

## Configuration

### Config Class

Configuration manager for the document converter.

#### Default Configuration

```yaml
output:
  image_format: "jpeg"
  image_quality: 95
  image_dpi: 200
  pdf_quality: "high"

conversion:
  batch_size: 10
  timeout: 300
  max_workers: 4

paths:
  temp_dir: "./temp"
  output_dir: "./output"
```

#### Usage

```python
from doc_converter.utils.config import Config

# Load default configuration
config = Config()

# Load from file
config = Config("config.yaml")

# Get configuration values
image_format = config.get("output.image_format")
max_workers = config.get("conversion.max_workers", 4)

# Set configuration values
config.set("output.image_dpi", 300)
```

---

## Command Line Interface

The package includes a comprehensive CLI for all operations.

### Basic Usage

```bash
# Convert PDF to images
python -m doc_converter pdf-to-images input.pdf --output-dir ./images --format jpeg --dpi 300

# Convert DOCX to PDF
python -m doc_converter docx-to-pdf input.docx --output output.pdf

# Convert HTML to PDF
python -m doc_converter html-to-pdf https://example.com --output webpage.pdf

# Batch convert
python -m doc_converter batch-convert --input-dir ./docs --output-dir ./converted --format pdf
```

### Available Commands

- `pdf-to-images`: Convert PDF to images
- `docx-to-pdf`: Convert DOCX to PDF
- `pptx-to-pdf`: Convert PPTX to PDF
- `txt-to-pdf`: Convert TXT to PDF
- `html-to-pdf`: Convert HTML to PDF
- `docx-to-html`: Convert DOCX to HTML
- `batch-convert`: Batch convert files

Use `python -m doc_converter <command> --help` for detailed help on each command.