"""The DocumentConverter facade: input validation, default output paths, delegation."""

import pytest

from doc_converter.core.document_converter import DocumentConverter


class Recorder:
    """Stands in for a sub-converter and remembers how it was called."""

    def __init__(self, result):
        self.result = result
        self.calls = []

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self.result

        return method


@pytest.fixture
def conv():
    c = DocumentConverter()
    c.pdf_converter = Recorder(["page_001.jpeg"])
    c.docx_converter = Recorder("out-path")
    c.html_converter = Recorder("html-out")
    return c


@pytest.mark.parametrize(
    "method",
    ["pdf_to_images", "docx_to_pdf", "pptx_to_pdf", "txt_to_pdf", "docx_to_html"],
)
def test_missing_input_files_are_reported_before_any_conversion(conv, tmp_path, method):
    with pytest.raises(FileNotFoundError):
        getattr(conv, method)(tmp_path / "nope.file")
    assert not conv.pdf_converter.calls and not conv.docx_converter.calls


def test_pdf_to_images_rejects_unknown_formats(conv, make_pdf):
    with pytest.raises(ValueError, match="Unsupported format"):
        conv.pdf_to_images(make_pdf(), format="gif")
    assert not conv.pdf_converter.calls


def test_pdf_to_images_defaults_the_output_directory_next_to_the_pdf(conv, make_pdf):
    pdf = make_pdf("report.pdf")
    assert conv.pdf_to_images(pdf) == ["page_001.jpeg"]
    name, args, _ = conv.pdf_converter.calls[0]
    assert name == "to_images" and args[1] == pdf.parent / "report_images"
    assert args[1].is_dir()  # created for the converter
    assert args[2:] == ("jpeg", 200)


def test_pdf_to_images_uses_an_explicit_directory_format_and_dpi(conv, make_pdf, tmp_path):
    out = tmp_path / "custom" / "dir"
    conv.pdf_to_images(make_pdf(), out, format="png", dpi=72)
    _, args, _ = conv.pdf_converter.calls[0]
    assert args[1] == out and out.is_dir() and args[2:] == ("png", 72)


@pytest.mark.parametrize(
    ("method", "source", "target"),
    [("docx_to_pdf", "a.docx", "to_pdf"), ("pptx_to_pdf", "a.pptx", "to_pdf"),
     ("txt_to_pdf", "a.txt", "txt_to_pdf")],
)  # fmt: skip
def test_office_and_text_conversions_default_to_a_pdf_beside_the_input(
    conv, tmp_path, method, source, target
):
    src = tmp_path / source
    src.write_bytes(b"x")
    assert getattr(conv, method)(src) == "out-path"
    name, args, _ = conv.docx_converter.calls[0]
    assert name == target and args == (src, tmp_path / "a.pdf")


def test_explicit_output_paths_get_their_parent_directory_created(conv, tmp_path):
    src = tmp_path / "a.docx"
    src.write_bytes(b"x")
    target = tmp_path / "new" / "folder" / "o.pdf"
    conv.docx_to_pdf(src, target)
    assert target.parent.is_dir() and conv.docx_converter.calls[0][1][1] == target


def test_html_to_pdf_passes_source_options_and_creates_the_parent(conv, tmp_path):
    out = tmp_path / "x" / "page.pdf"
    assert conv.html_to_pdf("https://example.com", out, {"page-size": "A3"}) == "html-out"
    name, args, _ = conv.html_converter.calls[0]
    assert name == "to_pdf" and args == ("https://example.com", out, {"page-size": "A3"})
    assert out.parent.is_dir()


def test_accepts_a_config_object_a_path_or_nothing(tmp_path):
    from doc_converter.utils.config import Config

    cfg = Config()
    cfg.set("output.image_dpi", 111)
    assert DocumentConverter(cfg).config is cfg  # BatchProcessor passes its Config like this
    path = tmp_path / "c.yaml"
    cfg.save_to_file(path)
    assert DocumentConverter(str(path)).config.get("output.image_dpi") == 111
    assert DocumentConverter().config.get("output.image_dpi") == 200
