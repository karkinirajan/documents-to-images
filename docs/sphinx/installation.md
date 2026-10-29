# Installation

## Requirements

- Python 3.8+
- System dependencies for document processing

## Install from PyPI

```bash
pip install documents-to-images-converter
```

## Development Installation

For development or contributing:

```bash
git clone https://github.com/yourusername/documents-to-images.git
cd documents-to-images
pip install -e ".[dev,test]"
```

## System Dependencies

### Linux (Ubuntu/Debian)

```bash
# For PDF and image processing
sudo apt update
sudo apt install poppler-utils

# For LibreOffice conversions (optional)
sudo apt install libreoffice
```

### macOS

```bash
# Using Homebrew
brew install poppler

# For LibreOffice conversions (optional)
brew install --cask libreoffice
```

### Windows

1. Download and install Poppler for Windows
2. Add the `bin` directory to your PATH
3. For LibreOffice conversions, install LibreOffice

## Verify Installation

```bash
doc-converter --version
```

Or in Python:

```python
import doc_converter

print(doc_converter.__version__)
```