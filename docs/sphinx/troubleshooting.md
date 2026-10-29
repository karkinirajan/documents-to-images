# Troubleshooting

Common issues and their solutions.

## Installation Issues

### Missing System Dependencies

**Problem**: Conversion fails with errors about missing libraries.

**Solution**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install poppler-utils libreoffice

# macOS
brew install poppler
brew install --cask libreoffice

# Verify installation
doc-converter --version
```

### Python Version Compatibility

**Problem**: Package fails to install or import.

**Solution**: Ensure you're using Python 3.8 or later:
```bash
python --version
pip --version

# Upgrade if necessary
pip install --upgrade pip
pip install --upgrade documents-to-images-converter
```

## Conversion Issues

### PDF to Images

**Problem**: Low-quality or blurry images.

**Solutions**:
```python
# Increase DPI for better quality
converter.pdf_to_images("file.pdf", dpi=300)  # Higher quality
converter.pdf_to_images("file.pdf", dpi=600)  # Very high quality

# Use PNG for better quality (larger files)
converter.pdf_to_images("file.pdf", format="png", dpi=300)
```

**Problem**: Memory errors with large PDFs.

**Solutions**:
```python
# Process page ranges instead of entire document
converter.pdf_to_images("large.pdf", first_page=1, last_page=10)

# Use lower DPI for large documents
converter.pdf_to_images("large.pdf", dpi=150)
```

### DOCX to PDF Issues

**Problem**: Formatting is lost during conversion.

**Solutions**:
```python
# Ensure LibreOffice is installed for better formatting
# Alternative: Use different conversion method
converter.docx_to_pdf("document.docx", preserve_formatting=True)
```

**Problem**: Embedded images are missing.

**Solutions**:
```python
# Check if images are embedded properly in source document
# Try extracting images separately
converter.docx_to_html("document.docx", extract_images=True)
```

### HTML to PDF Issues

**Problem**: Web page doesn't render correctly.

**Solutions**:
```python
# Add wait time for dynamic content
converter.html_to_pdf(
    "https://example.com",
    "output.pdf",
    wait_time=5000,  # Wait 5 seconds
)

# Adjust page settings
converter.html_to_pdf(
    "file.html",
    "output.pdf",
    page_size="A4",
    orientation="landscape",
    margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
)
```

**Problem**: CSS styling is missing.

**Solutions**:
- Ensure CSS files are accessible
- Use absolute URLs for external resources
- Embed CSS directly in HTML

### PPTX to PDF Issues

**Problem**: Slides are not properly sized.

**Solutions**:
```python
# Adjust output settings
converter.pptx_to_pdf(
    "presentation.pptx",
    output_format="pdf",
    slide_size="standard",  # or 'widescreen'
)
```

## Performance Issues

### Slow Conversion

**Solutions**:
```python
# Use batch processing for multiple files
from doc_converter import BatchProcessor

batch = BatchProcessor()
batch.batch_convert(
    input_dir="./docs",
    output_dir="./output",
    operation="pdf_to_images",
    parallel=True,
    max_workers=4,
)

# Reduce DPI for faster processing
converter.pdf_to_images("file.pdf", dpi=150)  # Faster, lower quality
```

### Memory Usage

**Solutions**:
```python
# Process files individually instead of batch
# Use generators for large file lists
# Clear converter cache periodically
converter.clear_cache()
```

## File Path Issues

### Special Characters

**Problem**: Files with special characters in names fail to process.

**Solutions**:
```python
import os
from pathlib import Path

# Use Path objects for better handling
file_path = Path("document with spaces & symbols.pdf")
converter.pdf_to_images(str(file_path))

# Sanitize filenames
import re


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


clean_name = sanitize_filename("file:with:colons.pdf")
```

### Long File Paths

**Problem**: File paths are too long (Windows limitation).

**Solutions**:
```python
# Use relative paths
os.chdir("./documents")
converter.pdf_to_images("file.pdf")

# Use shorter output directory names
converter.pdf_to_images("file.pdf", output_dir="./out")
```

## Permission Issues

### Access Denied

**Problem**: Cannot read input files or write to output directory.

**Solutions**:
```bash
# Check file permissions
ls -la input_file.pdf

# Fix permissions
chmod 644 input_file.pdf
chmod 755 output_directory/

# Run with appropriate user permissions
sudo chown $USER:$USER input_file.pdf
```

### Network Drive Issues

**Problem**: Files on network drives cannot be accessed.

**Solutions**:
- Copy files to local drive first
- Ensure network drive is properly mounted
- Use UNC paths on Windows

## Configuration Issues

### Config File Not Found

**Problem**: Custom config file is not being loaded.

**Solutions**:
```python
# Use absolute path
converter = DocumentConverter(config_file="/absolute/path/to/config.yaml")

# Check current working directory
import os

print(os.getcwd())

# Verify file exists
from pathlib import Path

config_path = Path("config.yaml")
print(f"Config exists: {config_path.exists()}")
```

### Invalid Configuration

**Problem**: Configuration values cause errors.

**Solutions**:
```yaml
# config.yaml - Use valid values
pdf_to_images:
  format: jpeg  # or 'png', not 'jpg'
  dpi: 300     # integer, not string

html_to_pdf:
  page_size: A4  # Use standard page sizes
  orientation: portrait  # or 'landscape'
```

## CLI Issues

### Command Not Found

**Problem**: `doc-converter` command is not recognized.

**Solutions**:
```bash
# Check if package is installed
pip list | grep documents-to-images

# Reinstall package
pip uninstall documents-to-images-converter
pip install documents-to-images-converter

# Use python module syntax
python -m doc_converter.cli.main --help
```

### Encoding Issues

**Problem**: Non-ASCII characters cause errors.

**Solutions**:
```bash
# Set environment variables
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Use UTF-8 compatible terminal
# Ensure input files are UTF-8 encoded
```

## Logging and Debugging

### Enable Debug Logging

```python
import logging

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Use verbose CLI option
doc-converter --verbose pdf-to-images file.pdf
```

### Common Error Messages

**"Poppler not found"**:
- Install poppler-utils (Linux) or poppler (macOS/Windows)

**"LibreOffice not found"**:
- Install LibreOffice for DOCX/PPTX conversions

**"Permission denied"**:
- Check file and directory permissions
- Ensure output directory is writable

**"File not found"**:
- Verify file path is correct
- Use absolute paths when possible

**"Conversion failed"**:
- Check input file is not corrupted
- Verify file format is supported
- Try with a different file

## Getting Help

If you encounter issues not covered here:

1. Check the [API documentation](api.md)
2. Enable debug logging to get more information
3. Try with a minimal example
4. Check system dependencies are installed
5. Verify file permissions and paths
6. Update to the latest version

### Reporting Bugs

When reporting issues, please include:
- Python version and OS
- Package version (`doc-converter --version`)
- Complete error message and stack trace
- Minimal code example to reproduce
- Input file (if possible)
- System dependencies versions