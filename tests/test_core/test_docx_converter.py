import subprocess

import pytest

from doc_converter.core.docx_converter import DOCXConverter


def test_docx_to_html_keeps_the_text(make_docx, tmp_path):
    out = tmp_path / "out" / "doc.html"
    assert DOCXConverter().to_html(make_docx(text="Hello docx"), out) == str(out)
    assert "Hello docx" in out.read_text(encoding="utf-8")


def test_docx_to_html_fails_on_a_non_docx(tmp_path):
    bad = tmp_path / "bad.docx"
    bad.write_text("not a zip")
    with pytest.raises(Exception):  # noqa: B017
        DOCXConverter().to_html(bad, tmp_path / "o.html")


@pytest.mark.needs_poppler
def test_txt_to_pdf_makes_a_readable_pdf(make_txt, tmp_path):
    out = tmp_path / "t" / "note.pdf"
    path = DOCXConverter().txt_to_pdf(make_txt(text="line one\nline two\n"), out)
    assert path == str(out) and out.read_bytes().startswith(b"%PDF")
    from pypdf import PdfReader

    pages = PdfReader(str(out)).pages
    assert len(pages) == 1
    assert "line one" in pages[0].extract_text() and "line two" in pages[0].extract_text()


def test_txt_to_pdf_wraps_long_lines_and_survives_non_latin_text(make_txt, tmp_path):
    text = ("word " * 100) + "\n" + "日本語のテキスト and emoji \U0001f600\n"
    out = tmp_path / "wrap.pdf"
    DOCXConverter().txt_to_pdf(make_txt(text=text), out)
    from pypdf import PdfReader

    extracted = "".join(p.extract_text() for p in PdfReader(str(out)).pages).replace("\n", "")
    assert extracted.count("word") == 100  # the 500-character line is wrapped, nothing lost
    assert "and emoji" in extracted


def test_txt_to_pdf_handles_an_empty_file(make_txt, tmp_path):
    out = tmp_path / "empty.pdf"
    DOCXConverter().txt_to_pdf(make_txt(text=""), out)
    assert out.read_bytes().startswith(b"%PDF")


@pytest.mark.needs_libreoffice
def test_docx_to_pdf_with_libreoffice(make_docx, tmp_path):
    out = tmp_path / "o" / "doc.pdf"
    path = DOCXConverter().to_pdf(make_docx(), out)
    assert path == str(out) and out.read_bytes().startswith(b"%PDF")


def test_to_pdf_surfaces_libreoffice_failures(make_docx, tmp_path, monkeypatch):
    conv = DOCXConverter()

    def fail(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(Exception, match="(?i)boom|failed|exit|returned"):
        conv.to_pdf(make_docx(), tmp_path / "x.pdf")
