# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### LibreOffice Not Found

**Problem:** Getting "LibreOffice not found" error during DOCX/PPTX conversion.

**Solutions:**

1. **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install libreoffice
   ```

2. **macOS:**
   ```bash
   brew install libreoffice
   ```

3. **Windows:**
   - Download LibreOffice from [official website](https://www.libreoffice.org/download/download/)
   - Install and ensure it's in PATH, or specify full path in configuration

4. **Manual PATH Configuration:**
   ```bash
   export PATH=$PATH:/usr/lib/libreoffice/program
   ```

#### wkhtmltopdf Issues

**Problem:** HTML to PDF conversion fails with wkhtmltopdf errors.

**Solutions:**

1. **Ubuntu/Debian:**
   ```bash
   sudo apt-get install wkhtmltopdf
   ```

2. **macOS:**
   ```bash
   brew install wkhtmltopdf
   ```

3. **Windows:**
   - Download from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)
   - Install and add to PATH

4. **Permission Issues:**
   ```bash
   sudo chmod +x /usr/local/bin/wkhtmltopdf
   ```

### Conversion Issues

#### PDF to Images Conversion Fails

**Problem:** `pdf2image` conversion fails or produces poor quality images.

**Solutions:**

1. **Install poppler-utils:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install poppler-utils
   
   # macOS
   brew install poppler
   
   # Windows (via conda)
   conda install poppler
   ```

2. **Increase DPI for better quality:**
   ```python
   converter.pdf_to_images("input.pdf", dpi=300)  # Higher quality
   ```

3. **Handle large PDFs:**
   ```python
   # Process specific page range
   converter.pdf_to_images("large.pdf", first_page=1, last_page=10)
   ```

#### DOCX Conversion Issues

**Problem:** DOCX files fail to convert or produce corrupted output.

**Solutions:**

1. **Check file integrity:**
   ```python
   from pathlib import Path

   docx_path = Path("document.docx")
   if not docx_path.exists():
       print("File not found")
   elif docx_path.stat().st_size == 0:
       print("File is empty")
   ```

2. **Handle password-protected files:**
   - Remove password protection before conversion
   - Or use alternative libraries for protected documents

3. **Complex formatting issues:**
   - Try converting to HTML first, then to PDF
   - Use LibreOffice directly for complex documents

#### HTML to PDF Issues

**Problem:** HTML to PDF conversion produces incorrect layout or fails.

**Solutions:**

1. **Adjust page settings:**
   ```python
   options = {
       "page-size": "A4",
       "margin-top": "0.75in",
       "margin-right": "0.75in",
       "margin-bottom": "0.75in",
       "margin-left": "0.75in",
       "disable-smart-shrinking": "",
   }
   converter.html_to_pdf("input.html", "output.pdf", options=options)
   ```

2. **Handle external resources:**
   ```python
   options = {
       "enable-local-file-access": None,
       "load-error-handling": "ignore",
       "load-media-error-handling": "ignore",
   }
   ```

3. **JavaScript issues:**
   ```python
   options = {
       "javascript-delay": 1000,  # Wait 1 second for JS
       "no-stop-slow-scripts": None,
   }
   ```

### Performance Issues

#### Slow Batch Processing

**Problem:** Batch conversion is very slow.

**Solutions:**

1. **Increase worker threads:**
   ```python
   processor = BatchProcessor(max_workers=8)
   ```

2. **Process smaller batches:**
   ```python
   # Split large directories into smaller chunks
   processor.convert_directory(
       input_dir="./large_dir",
       output_dir="./output",
       target_format="pdf",
       file_patterns=["*.docx"],  # Limit file types
       recursive=False,  # Don't process subdirectories
   )
   ```

3. **Use SSD storage:**
   - Process files on SSD for better I/O performance

#### Memory Issues

**Problem:** Out of memory errors during conversion.

**Solutions:**

1. **Reduce DPI for images:**
   ```python
   converter.pdf_to_images("large.pdf", dpi=150)  # Lower memory usage
   ```

2. **Process pages individually:**
   ```python
   # For large PDFs, process page by page
   for page in range(1, total_pages + 1):
       converter.pdf_to_images(
           "large.pdf", first_page=page, last_page=page, output_dir=f"./output/page_{page}"
       )
   ```

3. **Clean up temporary files:**
   ```python
   import tempfile
   import shutil

   # Clean temp directory periodically
   temp_dir = Path(tempfile.gettempdir())
   for temp_file in temp_dir.glob("doc_converter_*"):
       temp_file.unlink()
   ```

### File Format Issues

#### Unsupported File Types

**Problem:** Getting "unsupported format" errors.

**Solutions:**

1. **Check supported formats:**
   ```python
   converter = DocumentConverter()
   formats = converter.get_supported_formats()
   print(f"Supported input formats: {formats['input']}")
   print(f"Supported output formats: {formats['output']}")
   ```

2. **Convert to intermediate format:**
   ```python
   # Convert DOC to DOCX first, then to PDF
   # Use LibreOffice to convert DOC to DOCX manually
   ```

#### Encoding Issues

**Problem:** Text encoding problems in converted files.

**Solutions:**

1. **For TXT to PDF:**
   ```python
   # Specify encoding when reading text files
   with open("file.txt", "r", encoding="utf-8") as f:
       content = f.read()
   ```

2. **For HTML conversion:**
   ```python
   options = {
       "encoding": "UTF-8",
   }
   converter.html_to_pdf("input.html", "output.pdf", options=options)
   ```

### Configuration Issues

#### Custom Configuration

**Problem:** Need to customize default settings.

**Solutions:**

1. **Create config file:**
   ```yaml
   # config.yaml
   output:
     image_format: "png"
     image_dpi: 300
   
   conversion:
     timeout: 600
     max_workers: 2
   
   paths:
     temp_dir: "/tmp/doc_converter"
   ```

2. **Use configuration:**
   ```python
   converter = DocumentConverter("config.yaml")
   ```

### Debugging Tips

#### Enable Verbose Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Or use CLI verbose mode
# python -m doc_converter --verbose pdf-to-images input.pdf
```

#### Check System Dependencies

```bash
# Check if required tools are installed
which libreoffice
which wkhtmltopdf
python -c "import pdf2image, PIL, pdfkit, mammoth, fpdf; print('All dependencies OK')"
```

#### Validate Input Files

```python
def validate_file(file_path):
    path = Path(file_path)
    
    if not path.exists():
        print(f"File not found: {path}")
        return False
    
    if path.stat().st_size == 0:
        print(f"File is empty: {path}")
        return False
    
    print(f"File OK: {path} ({path.stat().st_size} bytes)")
    return True
```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the GitHub Issues:** [Project Issues](https://github.com/kneeraazon404/documents-to-images/issues)
2. **Create a new issue** with:
   - Your operating system
   - Python version
   - Error message (full traceback)
   - Input file details
   - Steps to reproduce

## Environment Information

To help with debugging, gather this information:

```python
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")

# Check package versions
try:
    import pdf2image

    print(f"pdf2image version: {pdf2image.__version__}")
except:
    print("pdf2image not available")

try:
    import PIL

    print(f"Pillow version: {PIL.__version__}")
except:
    print("Pillow not available")
```