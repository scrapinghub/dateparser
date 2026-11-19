from pathlib import Path

import pytest

pytest.importorskip("ruamel")

from dateparser_scripts import write_complete_data as generator
from dateparser_scripts.write_complete_data import write_complete_data


@pytest.mark.parametrize("existing_output", [False, True])
def test_in_memory_preserves_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing_output: bool
) -> None:
    data_directory = tmp_path / "data"
    translation_directory = data_directory / "date_translation_data"
    monkeypatch.setattr(generator, "translation_data_directory", data_directory)
    monkeypatch.setattr(generator, "date_translation_directory", translation_directory)
    monkeypatch.setattr(generator, "all_languages", {"en"})
    initializers = [
        data_directory / "__init__.py",
        translation_directory / "__init__.py",
    ]
    if existing_output:
        translation_directory.mkdir(parents=True)
        for filename in initializers:
            filename.write_bytes(b"sentinel\n")

    files = write_complete_data(in_memory=True)

    assert set(files) == {*initializers, translation_directory / "en.py"}
    assert files[initializers[0]] == (
        "from dateparser.data import date_translation_data\n"
        "\n"
        "from .languages_info import language_locale_dict, language_order\n"
    )
    assert files[initializers[1]] == ""
    language_content = files[translation_directory / "en.py"]
    assert isinstance(language_content, bytes)
    assert language_content.startswith(b"info = ")
    if existing_output:
        for filename in initializers:
            assert filename.read_bytes() == b"sentinel\n"
        assert not (translation_directory / "en.py").exists()
    else:
        assert not data_directory.exists()


def test_disk_generation_matches_in_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_directory = tmp_path / "data"
    translation_directory = data_directory / "date_translation_data"
    monkeypatch.setattr(generator, "translation_data_directory", data_directory)
    monkeypatch.setattr(generator, "date_translation_directory", translation_directory)
    monkeypatch.setattr(generator, "all_languages", {"en"})

    files = write_complete_data(in_memory=True)
    assert not data_directory.exists()
    assert write_complete_data() == {}

    for filename, content in files.items():
        if isinstance(content, str):
            content = content.encode("utf-8")
        assert filename.read_bytes() == content

    stale_file = translation_directory / "stale.py"
    stale_file.write_bytes(b"stale\n")
    assert write_complete_data() == {}
    assert not stale_file.exists()
    for filename, content in files.items():
        if isinstance(content, str):
            content = content.encode("utf-8")
        assert filename.read_bytes() == content


def test_dateparser_data_integrity() -> None:
    files = write_complete_data(in_memory=True)

    for filename, content in files.items():
        if isinstance(content, str):
            content = content.encode("utf-8")
        assert Path(filename).read_bytes().strip() == content.strip(), (
            f'The content of the file "{filename}" doesn\'t match the content'
            " of the generated file."
        )
