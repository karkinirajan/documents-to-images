# Versions

Resolved in `uv.lock` on 2026-10-29.

| Component | Version | Previous | Note |
|---|---|---|---|
| Python | 3.10 to 3.13 supported (3.13 for development) | 3.8+ declared; actually unimportable on 3.10/3.11 | `requires-python >=3.10` |
| pdf2image | resolved in lock | >=1.16 | needs poppler |
| Pillow | resolved in lock | >=9.0 | |
| pdfkit | resolved in lock | >=1.0 | needs wkhtmltopdf (archived upstream) |
| mammoth | resolved in lock | >=1.6 | |
| fpdf2 | >=2.8.2 | >=2.7 | `txt=` / `ln=` replaced by `text=` / `new_x` / `new_y` |
| pypdf | >=5.0 | PyPDF2 >=3.0 | PyPDF2 is deprecated |
| PyYAML | resolved in lock | >=6.0 | |
| tqdm | resolved in lock | >=4.64 | |

Dev: pytest >=8, pytest-cov, pytest-mock, ruff, mypy, types-PyYAML (replace black, isort, flake8, pylint, pre-commit).
System tools: poppler (`pdftoppm`), LibreOffice, wkhtmltopdf; versions are whatever the OS provides.
