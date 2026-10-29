import pytest

from doc_converter.utils.file_handler import FileHandler as FH


def test_ensure_directory_is_idempotent(tmp_path):
    target = tmp_path / "a" / "b"
    assert FH.ensure_directory(target) == target and target.is_dir()
    assert FH.ensure_directory(target) == target


@pytest.mark.parametrize(
    ("raw", "clean"),
    [
        ("report.pdf", "report.pdf"),
        ('a<b>c:d"e/f\\g|h?i*j.txt', "a_b_c_d_e_f_g_h_i_j.txt"),
        ("  .hidden. ", "hidden"),
    ],
)
def test_clean_filename(raw, clean):
    assert FH.clean_filename(raw) == clean


def test_clean_filename_limits_length_but_keeps_the_extension():
    cleaned = FH.clean_filename("x" * 400 + ".pdf")
    assert len(cleaned) == 255 and cleaned.endswith(".pdf")


@pytest.mark.parametrize(
    ("size", "text"),
    [(0, "0 B"), (1, "1.0 B"), (1023, "1023.0 B"), (1024, "1.0 KB"), (1536, "1.5 KB"),
     (1024**2, "1.0 MB"), (1024**3, "1.0 GB"), (1024**4, "1.0 TB"), (1024**5, "1024.0 TB")],
)  # fmt: skip
def test_format_file_size(size, text):
    assert FH.format_file_size(size) == text


def test_get_file_size(tmp_path):
    f = tmp_path / "f.bin"
    f.write_bytes(b"12345")
    assert FH.get_file_size(f) == 5


def test_copy_creates_parent_directories_and_keeps_the_source(tmp_path):
    src = tmp_path / "s.txt"
    src.write_text("data")
    dst = FH.copy_file(src, tmp_path / "deep" / "er" / "d.txt")
    assert dst.read_text() == "data" and src.exists()


def test_move_removes_the_source(tmp_path):
    src = tmp_path / "s.txt"
    src.write_text("data")
    dst = FH.move_file(src, tmp_path / "x" / "d.txt")
    assert dst.read_text() == "data" and not src.exists()


@pytest.mark.parametrize("op", [FH.copy_file, FH.move_file])
def test_copy_and_move_require_an_existing_source(tmp_path, op):
    with pytest.raises(FileNotFoundError):
        op(tmp_path / "missing", tmp_path / "dst")


def test_delete_file_ignores_missing_files(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("x")
    FH.delete_file(f)
    FH.delete_file(f)  # second call is a no-op
    assert not f.exists()


def test_find_files_recursive_non_recursive_and_deduplicated(tmp_path):
    (tmp_path / "a.pdf").write_text("")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.pdf").write_text("")
    (tmp_path / "sub" / "c.docx").write_text("")
    assert [p.name for p in FH.find_files(tmp_path, ["*.pdf"])] == ["a.pdf", "b.pdf"]
    assert [p.name for p in FH.find_files(tmp_path, ["*.pdf"], recursive=False)] == ["a.pdf"]
    assert len(FH.find_files(tmp_path, ["*.pdf", "a.*"])) == 2  # a.pdf matched twice, listed once


def test_temp_file_has_prefix_suffix_and_exists():
    path = FH.get_temp_file(suffix=".pdf", prefix="t_")
    try:
        assert path.name.startswith("t_") and path.suffix == ".pdf" and path.exists()
    finally:
        path.unlink()


def test_create_backup_never_overwrites_an_earlier_backup(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("v1")
    first = FH.create_backup(f)
    f.write_text("v2")
    second = FH.create_backup(f)
    assert first != second and first.read_text() == "v1" and second.read_text() == "v2"
