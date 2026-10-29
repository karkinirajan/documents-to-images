import pytest
import yaml

from doc_converter.utils.config import Config


def test_defaults_are_available_with_dot_notation():
    cfg = Config()
    assert cfg.get("output.image_format") == "jpeg"
    assert cfg.get("conversion.max_workers") == 4
    assert cfg.get("missing.key", "fallback") == "fallback"
    assert cfg.get("output.image_format.deeper") is None  # walking into a string is not an error


def test_set_creates_nested_keys():
    cfg = Config()
    cfg.set("custom.section.value", 42)
    assert cfg.get("custom.section.value") == 42


def test_instances_do_not_share_state_through_the_class_defaults():
    first = Config()
    first.set("output.image_format", "png")
    first.set("conversion.max_workers", 99)
    second = Config()
    assert second.get("output.image_format") == "jpeg"
    assert second.get("conversion.max_workers") == 4
    assert Config.DEFAULT_CONFIG["output"]["image_format"] == "jpeg"


def test_loading_a_file_merges_over_the_defaults_without_touching_them(tmp_path):
    path = tmp_path / "c.yaml"
    path.write_text(yaml.safe_dump({"output": {"image_dpi": 300}, "extra": {"x": 1}}))
    cfg = Config(path)
    assert cfg.get("output.image_dpi") == 300
    assert cfg.get("output.image_format") == "jpeg"  # sibling default survives the merge
    assert cfg.get("extra.x") == 1
    assert Config().get("output.image_dpi") == 200  # defaults untouched for later instances


def test_empty_config_file_is_accepted(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("")
    assert Config(path).get("output.image_dpi") == 200


def test_missing_and_invalid_config_files_raise(tmp_path):
    with pytest.raises(FileNotFoundError):
        Config(tmp_path / "nope.yaml")
    bad = tmp_path / "bad.yaml"
    bad.write_text("a: [unclosed")
    with pytest.raises(yaml.YAMLError):
        Config(bad)


def test_save_and_reload_round_trip(tmp_path):
    cfg = Config()
    cfg.set("output.image_dpi", 123)
    target = tmp_path / "nested" / "out.yaml"
    cfg.save_to_file(target)
    assert Config(target).get("output.image_dpi") == 123


def test_section_getters_return_the_right_sections():
    cfg = Config()
    assert cfg.get_output_config()["image_quality"] == 95
    assert cfg.get_conversion_config()["batch_size"] == 10
    assert cfg.get_paths_config()["output_dir"] == "./output"
    assert cfg.get_libreoffice_config()["headless"] is True
    assert cfg.get_wkhtmltopdf_config()["page_size"] == "A4"
