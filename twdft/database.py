import csv
import datetime
import sqlite3
import os

from typing import List, Any, Union, NamedTuple, Tuple

from .env import TWDFT_DATA_DIR, INSPECTORS


def conv_site_name_to_id(site: str) -> str:
    db_filename = "twdft.db"
    db_path = os.path.join(TWDFT_DATA_DIR, db_filename)
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        return c.execute(f"SELECT id FROM site WHERE name={site}")


def create_db_entry(
    site: str,
    inspection_date: str,
    inspection_time: str,
    inspection_status: str,
    inspectors: Tuple[str],
) -> None:
    """Create an inspection object in the database."""
    db_filename = "twdft.db"
    db_path = os.path.join(TWDFT_DATA_DIR, db_filename)
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        site_id = c.execute(f'SELECT id FROM site WHERE name="{site}"').fetchone()[0]
        data = (site_id, inspection_date, inspection_status, inspection_time)
        c.execute(
            f"""INSERT INTO inspection(
                        site,
                        date,
                        status,
                        time) VALUES (?,?,?,?)""",
            data,
        )
        insp_id = c.lastrowid
        inspector_ids = [
            c.execute("SELECT id FROM inspector WHERE first_name=?", (x,)).fetchone()[0]
            for x in inspectors
        ]
        for iid in inspector_ids:
            c.execute(
                "INSERT INTO inspector_inspections(inspector, inspection) VALUES (?,?)",
                (iid, insp_id),
            )


class Site(NamedTuple):
    id: int
    name: str
    site_type: str
    sub_category: str
    address_1: str
    address_2: str
    town: str
    county: str
    country: str
    postcode: str
    site_category: str
    freq_target: str
    created: str
    notes: str
    last_inspection: str
    next_inspection: str
    pfsp_approval: str
    pfsp_expiry: str
    unlocode: str
    pfso: str
    pso: str
    pfsa_approval: str
    pfsa_expiry: str
    team: str
    created_by: str
    last_updated: str
    updated_by: str
    afp_loc: str
    rdf: str
    classification: str
    article24: str
    psa_approval: str
    inspection_due: str


def clean_inspection_freq_data(
    data: list, sortkey: str, limit: int, filter: str
) -> tuple:
    """
    takes a list of (site_name, last_inspection, frequence_target)
    tuples and concerts t[1] into a date and t[2] into an integer.
    """
    SORT_KEYS = {"last_inspection": 1, "freq_target": 2, "days_since": 3, "along": 4}

    errors = []
    out = []
    for t in data:
        frequency_target = int(t[2])
        days_in_freq = days_in_frequency_target(frequency_target)
        try:
            d_obj = convert_date_str(t[1])
            days = days_since(d_obj).days
            percent_along_frequency_period = int((days / days_in_freq) * 100)
            if filter:
                if filter in t[0]:
                    out.append(
                        (
                            t[0],
                            d_obj,
                            frequency_target,
                            days,
                            percent_along_frequency_period,
                        )
                    )
            else:
                out.append(
                    (
                        t[0],
                        d_obj,
                        frequency_target,
                        days,
                        percent_along_frequency_period,
                    )
                )
            out = sorted(out, key=lambda item: item[SORT_KEYS[sortkey]], reverse=True)
        except ValueError:
            errors.append(t)
    if limit:
        out = out[:limit]
    return errors, out


def get_inspection_periods_all_sites(db_name) -> List[Any]:
    """
    Provide data for how a single site fairs in terms
    of inspection frequency.
    """
    db_file = os.path.join(TWDFT_DATA_DIR, db_name)
    try:
        conn = sqlite3.connect(db_file)
    except FileNotFoundError:
        raise
    c = conn.cursor()
    c.execute("SELECT site_name, last_inspection, frequency_target FROM inspections;")
    result = c.fetchall()
    conn.close()
    return result


def get_inspection_periods(db_name, site_name) -> tuple:
    """
    Provide data for how a single site fairs in terms
    of inspection frequency.
    """
    db_file = os.path.join(TWDFT_DATA_DIR, db_name)
    try:
        conn = sqlite3.connect(db_file)
    except FileNotFoundError:
        raise
    c = conn.cursor()
    c.execute(
        "SELECT last_inspection, frequency_target FROM inspections WHERE site_name=?",
        (site_name,),
    )
    result = c.fetchone()
    conn.close()
    return result


def initial_db_setup() -> None:
    """
    Initial db file set up.
    """
    db_filename = "twdft.db"
    db_path = os.path.join(TWDFT_DATA_DIR, db_filename)
    csv_filename = "sites.csv"
    csv_path = os.path.join(TWDFT_DATA_DIR, csv_filename)
    db_is_new = not os.path.exists(db_path)
    sites_csv = os.path.join(TWDFT_DATA_DIR, csv_filename)

    if db_is_new:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # first we create a site object
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

            # next we want an inspection table

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

            # next we want an inspector table
            c.execute(
                """
                CREATE TABLE inspector(
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT
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

            # a table that links inspectors with inspections
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

            for site in map(Site._make, csv.reader(open(csv_path, "r"))):
                try:
                    c.execute(
                        f"""
                                INSERT INTO site(
                                    id,
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
                                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            site.id,
                            site.name,
                            site.site_type,
                            site.sub_category,
                            site.address_1,
                            site.address_2,
                            site.town,
                            site.county,
                            site.country,
                            site.postcode,
                            site.site_category,
                            site.freq_target,
                            site.created,
                            site.notes,
                            site.last_inspection,
                            site.next_inspection,
                            site.pfsp_approval,
                            site.pfsp_expiry,
                            site.unlocode,
                            site.pfso,
                            site.pso,
                            site.pfsa_approval,
                            site.pfsa_expiry,
                            site.team,
                            site.created_by,
                            site.last_updated,
                            site.updated_by,
                            site.afp_loc,
                            site.rdf,
                            site.classification,
                            site.article24,
                            site.psa_approval,
                            site.inspection_due,
                        ),
                    )
                except sqlite3.IntegrityError:
                    print("That hasnae worked", site.inspection_due)


def convert_date_str(date_str: str) -> datetime.date:
    "Convert from this 16-06-2016 0:00 into a date object."
    date_str = date_str.split(" ")[0]
    date_str_l: Union[List[str], List[int]] = date_str.split("-")
    try:
        date_str_l = [int(x) for x in date_str_l]
    except ValueError:
        raise
    date_str_l = [date_str_l[2], date_str_l[1], date_str_l[0]]
    return datetime.date(*date_str_l)


def days_since(d: datetime.date) -> datetime.timedelta:
    "Returns number of days since a date."
    return datetime.date.today() - d


def days_in_frequency_target(target: int) -> int:
    """
    Returns number in a frequence period.
    e.g. in Mallard, frequence period may be 12, 6,
    18, etc to represent the numbner of months between
    inspections - ideally. We are simply converting
    that to days.
    """
    return int((target / 12) * 365)
