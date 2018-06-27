import csv
import datetime
import sqlite3
import os

from .env import TWDFT_DATA_DIR


def _clean_inspection_freq_data(data: list) -> tuple:
    """
    Takes a list of (site_name, last_inspection, frequence_target)
    tuples and concerts t[1] into a date and t[2] into an integer.
    """
    errors = []
    out = []
    for t in data:
        try:
            out.append(
                (t[0], convert_date_str(t[1]), int(t[2]))
            )
        except ValueError:
            errors.append(t)
    return errors, out


def get_inspection_periods_all_sites(db_name) -> tuple:
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
    c.execute("SELECT last_inspection, frequency_target FROM inspections WHERE site_name=?", (site_name,))
    result = c.fetchone()
    conn.close()
    return result


def import_csv_to_db(csv_file, db_name):
    db_file = os.path.join(TWDFT_DATA_DIR, db_name)
    sites_csv = os.path.join(TWDFT_DATA_DIR, csv_file)

    conn = sqlite3.connect(db_file)

    c = conn.cursor()

    c.execute("""
              DROP TABLE IF EXISTS inspections;
              """)

    c.execute("""
            CREATE TABLE inspections(
            site_name TEXT,
            prot_category TEXT,
            site_category TEXT,
            frequency_target TEXT,
            last_inspection TEXT
              )
            """
              )

    with open(sites_csv, 'r') as f:
        csv_reader = csv.DictReader(f)

        for line in csv_reader:
            data = (line['SiteName'],
                    line['SubCategoryDesc'],
                    line['SiteCategoryDesc'],
                    line['FrequencyTarget'],
                    line['DateOfLastInspection'])
            c.execute("INSERT INTO inspections VALUES(?,?,?,?,?)", data)
    conn.commit()
    conn.close()


def convert_date_str(date_str: str) -> datetime.date:
    "Convert from this 16-06-2016 0:00 into a date object."
    date_str = date_str.split(" ")[0]
    date_str = date_str.split("-")
    try:
        date_str = [int(x) for x in date_str]
    except ValueError:
        raise
    date_str = [date_str[2], date_str[1], date_str[0]]
    return datetime.date(*date_str)


def days_since(d: datetime.date) -> int:
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
