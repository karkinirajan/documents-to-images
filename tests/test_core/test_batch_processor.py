import pytest

from doc_converter.core.batch_processor import BatchProcessor


class FakeConverter:
    """Records calls; raises for any file whose name contains 'bad'."""

    def __init__(self):
        self.calls = []

    def _convert(self, kind, source, out):
        if "bad" in str(source):
            raise RuntimeError(f"cannot convert {source}")
        self.calls.append((kind, str(source)))
        return str(out)

    def docx_to_pdf(self, src, out):
        return self._convert("docx_to_pdf", src, out)

    def pptx_to_pdf(self, src, out):
        return self._convert("pptx_to_pdf", src, out)

    def txt_to_pdf(self, src, out):
        return self._convert("txt_to_pdf", src, out)

    def html_to_pdf(self, src, out):
        return self._convert("html_to_pdf", src, out)

    def docx_to_html(self, src, out):
        return self._convert("docx_to_html", src, out)

    def pdf_to_images(self, src, out_dir, fmt):
        return [str(out_dir / f"page_001.{fmt}")]


@pytest.fixture
def processor():
    p = BatchProcessor(max_workers=2)
    p.converter = FakeConverter()
    return p


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "in"
    (root / "sub").mkdir(parents=True)
    for rel in ("a.docx", "b.txt", "c.pptx", "d.html", "e.pdf", "sub/f.docx", "ignore.xyz"):
        (root / rel).write_text("x")
    return root


def test_missing_input_directory(processor, tmp_path):
    with pytest.raises(FileNotFoundError):
        processor.convert_directory(tmp_path / "nope", tmp_path / "out", "pdf")


def test_empty_directory_returns_an_empty_summary(processor, tmp_path):
    (tmp_path / "in").mkdir()
    result = processor.convert_directory(tmp_path / "in", tmp_path / "out", "pdf")
    assert result == {"total_files": 0, "successful": 0, "failed": 0, "results": [], "errors": []}
    assert (tmp_path / "out").is_dir()


def test_each_supported_type_is_routed_to_its_converter(processor, tree, tmp_path):
    result = processor.convert_directory(
        tree, tmp_path / "out", "pdf", ["*.docx", "*.txt", "*.pptx", "*.html"]
    )
    kinds = sorted(k for k, _ in processor.converter.calls)
    assert kinds == ["docx_to_pdf", "docx_to_pdf", "html_to_pdf", "pptx_to_pdf", "txt_to_pdf"]
    assert result["successful"] == 5 and result["failed"] == 0 and result["total_files"] == 5
    assert all(r["type"] == "single_file" and r["format"] == "pdf" for r in result["results"])


def test_default_patterns_skip_unknown_extensions(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "pdf")
    seen = {p.rsplit("/", 1)[-1] for _, p in processor.converter.calls}
    assert "ignore.xyz" not in seen
    # e.pdf matches the default patterns but cannot be converted *to* pdf
    assert result["failed"] == 1 and "Cannot convert pdf to PDF" in result["errors"][0]["error"]


def test_non_recursive_search_ignores_subdirectories(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "pdf", ["*.docx"], recursive=False)
    assert result["total_files"] == 1


def test_one_failing_file_does_not_stop_the_batch(processor, tmp_path):
    root = tmp_path / "in"
    root.mkdir()
    for name in ("ok1.docx", "bad.docx", "ok2.docx"):
        (root / name).write_text("x")
    result = processor.convert_directory(root, tmp_path / "out", "pdf", ["*.docx"])
    assert (result["successful"], result["failed"]) == (2, 1)
    assert result["errors"][0]["file"].endswith("bad.docx")
    assert "cannot convert" in result["errors"][0]["error"]


def test_progress_callback_reports_every_file(processor, tree, tmp_path):
    seen = []
    processor.convert_directory(
        tree,
        tmp_path / "out",
        "pdf",
        ["*.docx"],
        progress_callback=lambda c, t, n: seen.append((c, t, n)),
    )
    assert sorted(c for c, _, _ in seen) == [1, 2] and {t for _, t, _ in seen} == {2}
    assert {n for _, _, n in seen} == {"a.docx", "f.docx"}


def test_image_targets_create_one_folder_per_pdf(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "png", ["*.pdf"])
    assert result["successful"] == 1
    entry = result["results"][0]
    assert entry["type"] == "multiple_images" and entry["format"] == "png"
    assert (tmp_path / "out" / "e_images").is_dir()


def test_image_targets_reject_non_pdf_inputs(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "jpeg", ["*.docx"])
    assert result["failed"] == 2 and "Cannot convert docx to jpeg" in result["errors"][0]["error"]


def test_html_target_only_supports_docx(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "html", ["*.docx", "*.txt"])
    assert (result["successful"], result["failed"]) == (2, 1)


def test_unsupported_target_format(processor, tree, tmp_path):
    result = processor.convert_directory(tree, tmp_path / "out", "xlsx", ["*.docx"])
    assert result["failed"] == 2 and "Unsupported target format" in result["errors"][0]["error"]


def test_file_list_skips_missing_files(processor, tree, tmp_path):
    result = processor.convert_file_list(
        [tree / "a.docx", tree / "gone.docx", str(tree / "b.txt")], tmp_path / "out", "pdf"
    )
    assert result["total_files"] == 2 and result["successful"] == 2


def test_real_end_to_end_txt_to_pdf(tmp_path):
    root = tmp_path / "in"
    root.mkdir()
    (root / "note.txt").write_text("hello\nworld\n")
    result = BatchProcessor(max_workers=1).convert_directory(
        root, tmp_path / "out", "pdf", ["*.txt"]
    )
    assert result["successful"] == 1
    assert (tmp_path / "out" / "note.pdf").read_bytes().startswith(b"%PDF")


def test_batch_processor_accepts_a_config_object():
    from doc_converter.utils.config import Config

    cfg = Config()
    assert (
        BatchProcessor(cfg).converter.config is cfg
    )  # used to fail: a Config was treated as a path
