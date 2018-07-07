import sqlite3

from twdft.helpers import inspection_line


def test_get_site_name(test_db):
    with sqlite3.connect(test_db) as conn:
        c = conn.cursor()
        row = c.execute(
            """
            select * from site;
            """
        ).fetchone()
        assert row[1] == "Macmillian Port"


def test_get_inspector_name(test_db):
    with sqlite3.connect(test_db) as conn:
        c = conn.cursor()
        row = c.execute(
            """
            SELECT * FROM inspector;
            """
        ).fetchone()
        assert row[0] == 1
        assert row[1] == "John"
        assert row[2] == "McClaren"


def test_get_inspection_data(test_db):
    with sqlite3.connect(test_db) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            """
            SELECT
                inspection.id,
                site.name,
                inspector.first_name,
                inspector.last_name,
                inspection.date,
                inspection.time
            FROM inspection
            INNER JOIN site ON inspection.site=site.id
            INNER JOIN inspector_inspections ON inspection.id=inspector_inspections.inspection
            INNER JOIN inspector ON inspector.id=inspector_inspections.inspector
            """
        )
        row = c.fetchone()
        assert row["id"] == 1
        assert row["name"] == "Macmillian Port"
        assert row["first_name"] == "John"
        assert row["last_name"] == "McClaren"
        assert row["date"] == "2018-10-10"
        assert row["time"] == "2pm"


def test_double_inspector_tuple(test_db):
    """
    When we specify an inspection id, we want the details of the inspection,
    including the inspectors, in a tuple. This is leading towards creating a
    table in the terminal.

    We know inspection 2 in the test_db has two inspectors assigned to it.
    """
    inspection_data = inspection_line(2, test_db)
    assert inspection_data[1] == "Macmillian Port"
    assert inspection_data[3][0] == ("John", "McClaren")
    assert inspection_data[3][1] == ("Kelvin", "Muclaleik")


def test_treble_inspector_tuple(test_db):
    """
    When we specify an inspection id, we want the details of the inspection,
    including the inspectors, in a tuple. This is leading towards creating a
    table in the terminal.

    We know inspection 2 in the test_db has two inspectors assigned to it.
    """
    inspection_data = inspection_line(3, test_db)
    assert inspection_data[1] == "Macmillian Port"
    assert ("John", "McClaren") in inspection_data[3]
    assert ("Kelvin", "Muclaleik") in inspection_data[3]
    assert ("Steven", "Chrosssol") in inspection_data[3]
