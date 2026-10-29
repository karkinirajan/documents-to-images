# Contributing

We welcome contributions to the Documents to Images Converter project!

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- System dependencies (poppler, LibreOffice)

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/yourusername/documents-to-images.git
cd documents-to-images
```

3. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies:

```bash
pip install -e ".[dev,test]"
```

## Development Workflow

### Code Style

We use the following tools for code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run all checks:

```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type checking
mypy doc_converter/
```

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=doc_converter --cov-report=html

# Run specific test file
pytest tests/test_pdf_converter.py

# Run with verbose output
pytest -v
```

### Adding Tests

When adding new features:

1. Write tests for new functionality
2. Ensure all tests pass
3. Maintain or improve code coverage
4. Test with different Python versions locally if possible

Example test structure:

```python
import pytest
from doc_converter import DocumentConverter
from doc_converter.exceptions import ConversionError


class TestPDFConverter:
    def test_pdf_to_images_success(self, sample_pdf):
        converter = DocumentConverter()
        images = converter.pdf_to_images(sample_pdf)
        assert len(images) > 0
        assert all(img.endswith((".jpg", ".jpeg", ".png")) for img in images)

    def test_pdf_to_images_invalid_file(self):
        converter = DocumentConverter()
        with pytest.raises(ConversionError):
            converter.pdf_to_images("nonexistent.pdf")
```

## Contributing Guidelines

### Issue Reporting

When reporting bugs:

1. Use the issue template
2. Provide a minimal reproducible example
3. Include system information (OS, Python version)
4. Attach sample files if relevant (ensure no sensitive data)

### Feature Requests

For new features:

1. Check existing issues first
2. Provide clear use case and rationale
3. Consider backwards compatibility
4. Be willing to implement or help implement

### Pull Requests

Before submitting a PR:

1. Create an issue to discuss the change (for large changes)
2. Fork the repo and create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Update documentation if needed
6. Follow the existing code style

PR checklist:

- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code follows project style guidelines
- [ ] All CI checks passing

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(pdf): add support for password-protected PDFs
fix(cli): handle special characters in filenames
docs(api): update docstrings for DocumentConverter
test(batch): add tests for parallel processing
```

## Project Structure

```
documents-to-images/
├── doc_converter/           # Main package
│   ├── core/               # Core conversion modules
│   ├── utils/              # Utility functions
│   ├── cli/                # Command line interface
│   └── exceptions.py       # Custom exceptions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Usage examples
├── scripts/                # Utility scripts
└── requirements/           # Dependency files
```

### Adding New Converters

To add a new conversion type:

1. Create converter module in `doc_converter/core/`
2. Implement converter class with standard interface
3. Add integration to main `DocumentConverter` class
4. Add CLI command in `doc_converter/cli/commands.py`
5. Write comprehensive tests
6. Update documentation

Example converter structure:

```python
# doc_converter/core/xyz_converter.py
from pathlib import Path
from typing import Union, Optional
from ..exceptions import ConversionError


class XYZConverter:
    """Convert XYZ format to other formats."""

    def xyz_to_pdf(
        self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None, **kwargs
    ) -> str:
        """Convert XYZ file to PDF."""
        # Implementation here
        pass
```

## Documentation

### Building Documentation

Build Sphinx documentation:

```bash
cd docs/sphinx
make html
# Or on Windows: make.bat html
```

View locally:

```bash
python -m http.server 8000 -d docs/sphinx/_build/html
```

### Documentation Style

- Use clear, concise language
- Include code examples
- Document all public APIs
- Update both inline docstrings and Sphinx docs

## Release Process

For maintainers:

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Create release PR
4. After merge, tag release
5. GitHub Actions will publish to PyPI

Version numbering follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Code of Conduct

Please follow our Code of Conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Report unacceptable behavior to maintainers

## Getting Help

- Check existing issues and documentation first
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Reach out to maintainers for guidance

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Invited to become maintainers for sustained contributions

Thank you for contributing to Documents to Images Converter!