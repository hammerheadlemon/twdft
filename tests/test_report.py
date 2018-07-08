import pytest
import sqlite3

from twdft.report import Report, ReportHeader, ReportBody, ReportLine, ReportCell
from twdft.env import TWDFT_DATA_DIR


def test_cell_padding():
    t = " Test Text  "
    rc = ReportCell(t)
    assert rc[0] == "SPACE"
    assert rc[1] == "WORD"
    assert rc[2] == "SPACE"
    assert rc[3] == "WORD"
    assert rc[4] == "SPACE"
    assert rc[5] == "SPACE"


@pytest.mark.xfail
def test_report():
    test_data = [
        (1, "Test Port", "2018-02-01", [("Paul", "Smith")]),
        (2, "Test Port 2", "2018-02-02", [("Paul", "Smith")]),
    ]
    titles = ["ID", "Facility", "Date", "Inspector 1"]

    r = Report(test_data, titles)
    assert r[0] == "ID | Facility    | Date       | Inspector 1 "
    assert r[1] == "--------------------------------------------"
    assert r[2] == "1 | Test Port   | 2018-02-01 | Paul Smith"
