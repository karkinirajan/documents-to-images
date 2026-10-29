import pytest
from PIL import Image

from doc_converter.core.pdf_converter import PDFConverter


@pytest.mark.needs_poppler
def test_pdf_pages_become_numbered_jpeg_files(make_pdf, tmp_path):
    out = tmp_path / "imgs"
    out.mkdir()
    files = PDFConverter().to_images(make_pdf(pages=3), out, "jpeg", dpi=50)
    assert [f.rsplit("/", 1)[-1] for f in files] == [
        "page_001.jpeg",
        "page_002.jpeg",
        "page_003.jpeg",
    ]
    with Image.open(files[0]) as im:
        assert im.format == "JPEG" and im.width > 0


@pytest.mark.needs_poppler
def test_png_output_and_page_range(make_pdf, tmp_path):
    out = tmp_path / "imgs"
    out.mkdir()
    files = PDFConverter().to_images(
        make_pdf(pages=4), out, "png", dpi=40, first_page=2, last_page=3
    )
    assert [f.rsplit("/", 1)[-1] for f in files] == ["page_002.png", "page_003.png"]
    with Image.open(files[1]) as im:
        assert im.format == "PNG"


@pytest.mark.needs_poppler
def test_dpi_changes_the_image_size(make_pdf, tmp_path):
    pdf = make_pdf(pages=1)
    sizes = {}
    for dpi in (40, 80):
        out = tmp_path / f"d{dpi}"
        out.mkdir()
        with Image.open(PDFConverter().to_images(pdf, out, "png", dpi=dpi)[0]) as im:
            sizes[dpi] = im.size
    assert sizes[80][0] == pytest.approx(sizes[40][0] * 2, abs=2)


@pytest.mark.needs_poppler
def test_get_page_count(make_pdf):
    assert PDFConverter().get_page_count(make_pdf(pages=5)) == 5


def test_conversion_failures_propagate(tmp_path):
    with pytest.raises(Exception):  # noqa: B017 - pdf2image raises its own error types
        PDFConverter().to_images(tmp_path / "missing.pdf", tmp_path, "png")


def test_unreadable_pdf_page_count_raises(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_text("this is not a pdf")
    with pytest.raises(Exception):  # noqa: B017
        PDFConverter().get_page_count(bad)


def test_module_imports_on_older_pythons():
    """Regression: a multi-line f-string expression made this module a SyntaxError before 3.12."""
    import ast
    import inspect

    from doc_converter.core import pdf_converter

    ast.parse(inspect.getsource(pdf_converter), feature_version=(3, 10))
