import shutil
import zipfile

import pytest

HAS_POPPLER = shutil.which("pdftoppm") is not None
HAS_LIBREOFFICE = shutil.which("libreoffice") is not None or shutil.which("soffice") is not None


def pytest_collection_modifyitems(config, items):
    """Skip tests that need an external program when it is not installed."""
    skips = {
        "needs_poppler": (HAS_POPPLER, "poppler (pdftoppm) is not installed"),
        "needs_libreoffice": (HAS_LIBREOFFICE, "LibreOffice is not installed"),
    }
    for item in items:
        for marker, (available, reason) in skips.items():
            if marker in item.keywords and not available:
                item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture
def workdir(tmp_path):
    return tmp_path


@pytest.fixture
def make_txt(tmp_path):
    def _make(name="note.txt", text="Hello\nWorld\n"):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path

    return _make


@pytest.fixture
def make_pdf(tmp_path):
    """Create a real multi-page PDF with fpdf2 (a project dependency)."""
    from fpdf import FPDF

    def _make(name="doc.pdf", pages=2):
        pdf = FPDF()
        for n in range(pages):
            pdf.add_page()
            pdf.set_font("Helvetica", size=14)
            pdf.cell(0, 10, f"Page {n + 1}")
        path = tmp_path / name
        pdf.output(str(path))
        return path

    return _make


@pytest.fixture
def make_docx(tmp_path):
    """Create a minimal but valid .docx (a zip of three XML parts) with one paragraph."""

    def _make(name="doc.docx", text="Hello docx"):
        path = tmp_path / name
        with zipfile.ZipFile(path, "w") as z:
            z.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                "</Types>",
            )
            z.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                "</Relationships>",
            )
            z.writestr(
                "word/document.xml",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f"<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>",
            )
        return path

    return _make


@pytest.fixture(autouse=True)
def _reset_config_defaults():
    """Config used to leak changes into the class-level defaults; keep tests independent."""
    import copy

    from doc_converter.utils.config import Config

    saved = copy.deepcopy(Config.DEFAULT_CONFIG)
    yield
    Config.DEFAULT_CONFIG.clear()
    Config.DEFAULT_CONFIG.update(saved)
