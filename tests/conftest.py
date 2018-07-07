import os
import pytest
import sqlite3

from twdft.env import TWDFT_DATA_DIR


@pytest.fixture(
    params=["Awful Site Name With Space", "Bad & Badder Site", "Test Site/1"]
)
def bad_site_names(request):
    print("\n-------------------------------------")
    print(f"fixturename     :   {request.fixturename}")
    yield request.param


@pytest.fixture(
    params=[
        ("Port of Harwich", "2010-10-10"),
        ("Port of Felixtowe", "2010-10-11"),
        ("Port of Leith", "2019-05-01"),
    ]
)
def date_location(request):
    print("\n--------------------------------------")
    print(f"fixturename     :   {request.fixturename}")
    print(f"scope           :   {request.scope}")
    print(f"function        :   {request.function.__name__}")
    print(f"cls             :   {request.cls}")
    print(f"module          :   {request.module.__name__}")
    print(f"fspath          :   {request.fspath}")
    yield request.param
    os.unlink("/home/lemon/.task-test/pending.data")


@pytest.fixture(
    params=[
        ("Port of Harwich", "2010-10-10T10:30"),
        ("Port of Felixtowe", "2010-10-11T10:30"),
        ("Port of Leith", "2019-05-01T10:30"),
    ]
)
def date_time_location(request):
    print("\n--------------------------------------")
    print(f"fixturename     :   {request.fixturename}")
    print(f"scope           :   {request.scope}")
    print(f"function        :   {request.function.__name__}")
    print(f"cls             :   {request.cls}")
    print(f"module          :   {request.module.__name__}")
    print(f"fspath          :   {request.fspath}")
    yield request.param
    os.unlink("/home/lemon/.task-test/pending.data")


@pytest.fixture
def date_natural_location():
    yield "20 August 2018"


#   we don't unlink here because the error means no data is created
#   os.unlink("/home/lemon/.task-test/pending.data")


@pytest.fixture
def date_time_natural_location():
    yield {"date": "20 August 2018", "time": "10:30am"}
    os.unlink("/home/lemon/.task-test/pending.data")


TEST_DB = os.path.join(TWDFT_DATA_DIR, "test-twdft.db")

INSPECTORS = ["John McClaren", "Kelvin Muclaleik", "Steven Chrosssol", "Aiden Snarlo"]


@pytest.fixture
def test_db():
    with sqlite3.connect(TEST_DB) as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS site")
        c.execute(
            """
                        CREATE TABLE site(
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        site_type TEXT,
                        sub_category TEXT,
                        address_1 TEXT,
                        address_2 TEXT,
                        town TEXT,
                        county TEXT,
                        country TEXT,
                        postcode TEXT,
                        site_category TEXT,
                        freq_target TEXT,
                        created TEXT,
                        notes TEXT,
                        last_inspection TEXT,
                        next_inspection TEXT,
                        pfsp_approval TEXT,
                        pfsp_expiry TEXT,
                        unlocode TEXT,
                        pfso TEXT,
                        pso TEXT,
                        pfsa_approval TEXT,
                        pfsa_expiry TEXT,
                        team TEXT,
                        created_by TEXT,
                        last_updated TEXT,
                        updated_by TEXT,
                        afp_loc TEXT,
                        rdf TEXT,
                        classification TEXT,
                        article24 TEXT,
                        psa_approval TEXT,
                        inspection_due TEXT
                        )
                        """
        )
        conn.commit()

        c.execute(
            """
            DROP TABLE IF EXISTS inspection
            """
        )
        conn.commit()

        c.execute(
            """
            CREATE TABLE inspection(
                id INTEGER PRIMARY KEY,
                site INTEGER,
                date TEXT,
                status TEXT,
                time TEXT,
                FOREIGN KEY(site) REFERENCES site(id)
            )
            """
        )
        conn.commit()

        c.execute("DROP TABLE IF EXISTS inspector")

        c.execute(
            """
            create table inspector(
                id integer primary key,
                first_name text,
                last_name text
            )
            """
        )
        conn.commit()

        for i in INSPECTORS:
            first = i.split(" ")[0]
            last = i.split(" ")[1]
            c.execute(
                "INSERT INTO inspector(first_name, last_name) VALUES (?,?)",
                (first, last),
            )
        c.execute("DROP TABLE IF EXISTS inspector_inspections")
        c.execute(
            """
            CREATE TABLE inspector_inspections(
            inspector INTEGER,
            inspection INTEGER,
            FOREIGN KEY (inspector) REFERENCES inspector(id),
            FOREIGN KEY (inspection) REFERENCES inspection(id)
            )
            """
        )
        conn.commit()

        c.execute(
            f"""
                    INSERT INTO site(
                            name,
                            site_type,
                            sub_category,
                            address_1,
                            address_2,
                            town,
                            county,
                            country,
                            postcode,
                            site_category,
                            freq_target,
                            created,
                            notes,
                            last_inspection,
                            next_inspection,
                            pfsp_approval,
                            pfsp_expiry,
                            unlocode,
                            pfso,
                            pso,
                            pfsa_approval,
                            pfsa_expiry,
                            team,
                            created_by,
                            last_updated,
                            updated_by,
                            afp_loc,
                            rdf,
                            classification,
                            article24,
                            psa_approval,
                            inspection_due
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "Macmillian Port",
                "Port",
                "COG 1",
                "Main Precinct",
                "Blubbery",
                "Tinseltown",
                "Northampton",
                "UK",
                "ZE1 1QP",
                "A",
                "12",
                "05-06-2014 10:57",
                "Moyra Hemphill used to be the PFSO here but moved on to Liverpool.",
                "15-06-2017 00:00",
                "",
                "16-11-2017 00:00",
                "",
                "GBSUL-001",
                "Harvey Lemon",
                "",
                "24-12-2012 0:00",
                "01-04-2018 0:00",
                "Maritime East",
                "20",
                "19-05-2016 0:00",
                "103",
                "",
                "0",
                "UK PF",
                "1",
                "19-09-2014 0:00",
                "20-10-2019 0:00",
            ),
        )
        conn.commit()

        # single inspector
        c.execute(
            """
            INSERT INTO inspection(site, date, status, time)
            VALUES (1, "2018-10-10", "forwardlook", "2pm");
            """
        )
        insp_id = c.lastrowid
        c.execute(f"""INSERT INTO inspector_inspections VALUES (?,?)""", (1, insp_id))

        # double inspector
        c.execute(
            """
            INSERT INTO inspection(site, date, status, time)
            VALUES (1, "2028-10-10", "forwardlook", "10:30");
            """
        )
        insp_id = c.lastrowid
        c.execute(f"""INSERT INTO inspector_inspections VALUES (?,?)""", (1, insp_id))
        c.execute(f"""INSERT INTO inspector_inspections VALUES (?,?)""", (2, insp_id))

        conn.commit()

    yield TEST_DB
    c.execute("DROP TABLE inspection")
    c.execute("DROP TABLE inspector_inspections")
    c.execute("DROP TABLE site")
    c.execute("DROP TABLE inspector")
