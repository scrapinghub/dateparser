from pathlib import Path

import pytest

pytest.importorskip("ruamel")

from dateparser_scripts.write_complete_data import write_complete_data


def test_dateparser_data_integrity():
    files = write_complete_data(in_memory=True)

    for filename in files:
        assert Path(filename).read_bytes().strip() == files[filename].strip(), (
            f'The content of the file "{filename}" doesn\'t match the content'
            " of the generated file."
        )
