import csv
import io
import zipfile
from pathlib import Path

import pytest

from dateparser_scripts import article_dates


def test_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rows = io.StringIO()
    writer = csv.writer(rows)
    writer.writerow(
        ["suffix", "articleLanguage", "webPageLanguages", "datePublishedRaw"]
    )
    writer.writerow(["com", "en", "en", "October 22, 2020"])
    writer.writerow(["de", "de", "de", "05.03.2021"])
    writer.writerow(["de", "de", "de", "05.03.2021"])
    writer.writerow(["de", "de", "de", "Stellenangebot vom 04.11.2020"])
    data = tmp_path / "data.zip"
    with zipfile.ZipFile(data, "w") as archive:
        archive.writestr("data.csv", rows.getvalue())
    output = tmp_path / "output.tsv"

    article_dates.main(["--data", str(data), "--jobs", "1", "--output", str(output)])

    report = capsys.readouterr().out
    assert report.startswith("4 rows, 3 distinct\n")
    assert "\nunparsed: 1 (25.0%)\n" in report
    assert "\nsearchable: 1 (25.0%)\n" in report
    assert "\nfuture: 2 (50.0%)\n" in report
    assert "\nhint-dependent: 2 (50.0%)\n" in report
    assert "\n      2  '99.99.9999'\n" in report
    assert len(output.read_text().splitlines()) == 3
