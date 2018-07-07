import sqlite3


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
        c = conn.cursor()
        row = c.execute(
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
        ).fetchall()
        assert row[0] == (1, 'Macmillian Port', 'John', 'McClaren', '2018-10-10', '2pm')
