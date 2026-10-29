import pdfkit
import pytest

from doc_converter.core.html_converter import HTMLConverter


@pytest.fixture
def fake_pdfkit(monkeypatch):
    """Replace pdfkit (which needs wkhtmltopdf) with functions that record their arguments."""
    calls = []

    def make(kind):
        def fn(source, output, options=None, configuration=None):
            calls.append((kind, source, output, options))
            with open(output, "wb") as f:
                f.write(b"%PDF-fake")

        return fn

    for kind in ("from_url", "from_file", "from_string"):
        monkeypatch.setattr(pdfkit, kind, make(kind))
    monkeypatch.setattr(pdfkit, "configuration", lambda **kw: kw)
    return calls


def test_html_file_becomes_a_pdf_with_default_options(fake_pdfkit, tmp_path):
    html = tmp_path / "p.html"
    html.write_text("<h1>Hi</h1>")
    out = tmp_path / "o" / "p.pdf"
    assert HTMLConverter().to_pdf(str(html), out) == str(out)
    kind, source, _, options = fake_pdfkit[0]
    assert kind == "from_file" and source == str(html)
    assert options["page-size"] == "A4" and options["encoding"] == "UTF-8"


def test_urls_use_from_url(fake_pdfkit, tmp_path):
    HTMLConverter().to_pdf("https://example.com/x", tmp_path / "u.pdf")
    assert fake_pdfkit[0][0] == "from_url"


def test_user_options_override_defaults(fake_pdfkit, tmp_path):
    html = tmp_path / "p.html"
    html.write_text("x")
    HTMLConverter().to_pdf(str(html), tmp_path / "o.pdf", {"page-size": "Letter"})
    assert fake_pdfkit[0][3]["page-size"] == "Letter"


def test_missing_html_file_is_reported(fake_pdfkit, tmp_path):
    with pytest.raises(FileNotFoundError):
        HTMLConverter().to_pdf(str(tmp_path / "missing.html"), tmp_path / "o.pdf")
    assert fake_pdfkit == []


def test_a_conversion_that_produces_no_file_is_an_error(monkeypatch, tmp_path):
    monkeypatch.setattr(pdfkit, "from_url", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="PDF was not created"):
        HTMLConverter().to_pdf("https://example.com", tmp_path / "none.pdf")


def test_missing_wkhtmltopdf_gives_install_instructions(monkeypatch, tmp_path):
    def boom(*args, **kwargs):
        raise OSError("No wkhtmltopdf executable found: ''")

    monkeypatch.setattr(pdfkit, "from_url", boom)
    with pytest.raises(RuntimeError, match="Please install wkhtmltopdf"):
        HTMLConverter().to_pdf("https://example.com", tmp_path / "o.pdf")


def test_from_string(fake_pdfkit, tmp_path):
    out = tmp_path / "s" / "s.pdf"
    assert HTMLConverter().from_string("<p>hi</p>", out, {"margin-top": "1in"}) == str(out)
    kind, source, _, options = fake_pdfkit[0]
    assert kind == "from_string" and source == "<p>hi</p>" and options["margin-top"] == "1in"


def test_executable_discovery_uses_the_path(monkeypatch):
    conv = HTMLConverter()
    monkeypatch.setattr(conv, "_which", lambda program: program == "wkhtmltopdf")
    monkeypatch.setattr("os.path.isfile", lambda path: False)
    assert conv._find_wkhtmltopdf() == "wkhtmltopdf"
    monkeypatch.setattr(conv, "_which", lambda program: False)
    assert conv._find_wkhtmltopdf() is None
