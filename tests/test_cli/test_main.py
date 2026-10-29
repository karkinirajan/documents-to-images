import importlib
import sys

import pytest

# `doc_converter.cli` re-exports the main() function under the same name, so import the module.
cli = importlib.import_module("doc_converter.cli.main")


class StubConverter:
    instances = []

    def __init__(self, *a, **k):
        self.calls = []
        StubConverter.instances.append(self)

    def pdf_to_images(self, **kw):
        self.calls.append(("pdf_to_images", kw))
        return ["a.jpeg", "b.jpeg"]

    def docx_to_pdf(self, **kw):
        self.calls.append(("docx_to_pdf", kw))
        return "out.pdf"

    def pptx_to_pdf(self, **kw):
        self.calls.append(("pptx_to_pdf", kw))
        return "out.pdf"

    def txt_to_pdf(self, **kw):
        self.calls.append(("txt_to_pdf", kw))
        return "out.pdf"

    def html_to_pdf(self, **kw):
        self.calls.append(("html_to_pdf", kw))
        return "out.pdf"

    def docx_to_html(self, **kw):
        self.calls.append(("docx_to_html", kw))
        return "out.html"


@pytest.fixture
def run(monkeypatch, capsys):
    StubConverter.instances = []
    monkeypatch.setattr(cli, "DocumentConverter", StubConverter)

    def _run(*argv):
        monkeypatch.setattr(sys, "argv", ["doc-converter", *argv])
        cli.main()
        return capsys.readouterr()

    return _run


def test_no_command_prints_help_and_exits_1(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["doc-converter"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1 and "usage:" in capsys.readouterr().out


def test_unknown_command_is_rejected_by_argparse(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["doc-converter", "frobnicate"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2


def test_pdf_to_images_arguments(run):
    out = run("pdf-to-images", "d.pdf", "--output-dir", "imgs", "--format", "png", "--dpi", "72")
    call = StubConverter.instances[0].calls[0]
    assert call == (
        "pdf_to_images",
        {"pdf_path": "d.pdf", "output_dir": "imgs", "format": "png", "dpi": 72},
    )
    assert "2 images" in out.out


@pytest.mark.parametrize(
    ("command", "method", "key", "result"),
    [
        ("docx-to-pdf", "docx_to_pdf", "docx_path", "out.pdf"),
        ("pptx-to-pdf", "pptx_to_pdf", "pptx_path", "out.pdf"),
        ("txt-to-pdf", "txt_to_pdf", "txt_path", "out.pdf"),
        ("docx-to-html", "docx_to_html", "docx_path", "out.html"),
    ],
)
def test_simple_conversion_commands(run, command, method, key, result):
    out = run(command, "in.file", "--output", "o.file")
    name, kwargs = StubConverter.instances[0].calls[0]
    assert name == method and kwargs == {key: "in.file", "output_path": "o.file"}
    assert result in out.out


def test_html_to_pdf_command(run):
    out = run("html-to-pdf", "https://example.com", "--output", "w.pdf")
    name, kwargs = StubConverter.instances[0].calls[0]
    assert name == "html_to_pdf" and kwargs["html_source"] == "https://example.com"
    assert "out.pdf" in out.out


def test_errors_exit_with_status_1_and_go_to_stderr(monkeypatch, capsys):
    class Failing(StubConverter):
        def docx_to_pdf(self, **kw):
            raise RuntimeError("it broke")

    monkeypatch.setattr(cli, "DocumentConverter", Failing)
    monkeypatch.setattr(sys, "argv", ["doc-converter", "docx-to-pdf", "x.docx"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    captured = capsys.readouterr()
    assert exc.value.code == 1 and "it broke" in captured.err and "it broke" not in captured.out


def test_batch_convert_runs_the_processor_and_reports(monkeypatch, capsys, tmp_path):
    seen = {}

    class FakeProcessor:
        def __init__(self, max_workers):
            seen["workers"] = max_workers

        def convert_directory(self, **kw):
            seen["kw"] = kw
            return {"total_files": 2, "successful": 1, "failed": 1, "results": [],
                    "errors": [{"file": "bad.docx", "error": "nope"}]}  # fmt: skip

    monkeypatch.setattr(cli, "BatchProcessor", FakeProcessor)
    argv = ["doc-converter", "batch-convert", "-i", "in", "-o", "out", "-f", "pdf"]
    argv += ["--patterns", "*.docx", "-r", "-w", "3"]
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()
    text = capsys.readouterr().out
    assert seen["workers"] == 3
    assert seen["kw"]["target_format"] == "pdf" and seen["kw"]["recursive"] is True
    assert seen["kw"]["file_patterns"] == ["*.docx"]
    assert "Successful: 1" in text and "bad.docx: nope" in text


def test_batch_convert_rejects_unknown_formats(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["doc-converter", "batch-convert", "-i", "a", "-o", "b", "-f", "bmp"]
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2


def test_package_entry_point_module_exists():
    import importlib

    assert importlib.import_module("doc_converter.__main__")


def test_main_accepts_an_explicit_argv_list(monkeypatch, capsys):
    StubConverter.instances = []
    monkeypatch.setattr(cli, "DocumentConverter", StubConverter)
    cli.main(["docx-to-pdf", "in.docx", "-o", "o.pdf"])
    assert StubConverter.instances[0].calls[0][1] == {
        "docx_path": "in.docx",
        "output_path": "o.pdf",
    }


def test_pdf_to_images_reports_the_default_output_directory(run):
    out = run("pdf-to-images", "reports/q3.pdf")
    assert "reports/q3_images" in out.out
