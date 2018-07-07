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
