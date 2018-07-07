import re
import subprocess
import uuid
import textwrap
import sys
import csv
import os
import datetime
import click
import fileinput
import sqlite3

import parsedatetime

from typing import List, Union, Dict, Tuple
from tasklib import TaskWarrior, Task

from .env import TWDFTRC, CARDS_DIR, TWDFT_DATA_DIR, SITE_DATA_FILE, DB_FILE


def inspection_line(inspection_id: int, db_file: Union[str, None] = None) -> Tuple:
    "Returns a tuple of key inspection data for listing in a terminal table."
    if db_file:
        db = db_file
    else:
        db = DB_FILE
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            f"""
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
            WHERE inspection.id={inspection_id}
            """
        )
    data = c.fetchall()
    if len(data) > 1:  # we have multiple inspectors
        names = [(x["first_name"], x["last_name"]) for x in data]
        row = data[0]
    else:
        row = data[0]
        names = [(row["first_name"], row["last_name"])]
    return (row["id"], row["name"], row["date"], names)


def get_inspection_data() -> List[Tuple]:
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        output = []
        c = conn.cursor()
        c.execute("SELECT * FROM inspection")
        for row in c.fetchall():
            output.append(inspection_line(row["id"]))
        return output


def clean_date(date) -> Union[datetime.date, datetime.datetime]:
    parsed_obj: Union[datetime.date, datetime.datetime]
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(date)
    if parse_status == 1:
        # it is a date object
        parsed_obj = datetime.date(*time_struct[:3])
    elif parse_status == 2:
        # it is a time
        click.echo(f"Cannot parse {date}. Give me something reasonable, buddy!")
        sys.exit(1)
    elif parse_status == 3:
        # it is a datetime
        parsed_obj = datetime.datetime(*time_struct[:6])
    elif parse_status == 0:
        click.echo(f"Cannot parse {date}. Give me something reasonable, buddy!")
        sys.exit(1)
    return parsed_obj


def create_task(**kwargs):
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)

    verbose = kwargs.pop("verbose", False)
    open_card = kwargs.pop("open_card", False)
    inspectors = kwargs.pop("inspectors", False)

    test_task = Task(tw, **kwargs)
    test_task.save()
    if open_card:
        card_path = create_card(
            inspection_name=kwargs["description"],
            inspection_date=kwargs["inspection_date"],
            inspection_time=kwargs["inspection_time"],
            open_card=True,
            inspectors=inspectors,
            verbose=verbose,
        )
        test_task["card_path"] = card_path[0]
        test_task["inspection_card_uuid"] = card_path[1]
        test_task.save()
    else:
        card_path = create_card(
            inspection_name=kwargs["description"],
            inspection_date=kwargs["inspection_date"],
            inspection_time=kwargs["inspection_time"],
            open_card=False,
            inspectors=inspectors,
            verbose=verbose,
        )
        test_task["card_path"] = card_path[0]
        test_task["inspection_card_uuid"] = card_path[1]
        test_task.save()


def create_card(
    inspection_name: str,
    inspection_date: str,
    inspection_time: str,
    inspectors: Tuple[str],
    open_card: bool,
    verbose: bool,
) -> Tuple[str, str]:

    site_data = lookup_site_data(inspection_name)
    site_notes = site_data[13]
    site_notes = site_notes.replace("\n", "")

    template = textwrap.dedent(
        f"""\
                               ## Inspection at: {inspection_name}
                               ### Region: {site_data[2]}
                               ### Site Category: {site_data[10]}
                               ### PFSO: {site_data[19]}
                               ### Protection Category: {site_data[3]}
                               ### Date: {inspection_date}
                               ### Time: {inspection_time}
                               ### Status: forwardlook
                               ### Inspectors: {inspectors}
                               ### Last Inspection: {site_data[14]}

                               ### Site Notes:

                               {site_notes}

                               ### Address

                               {site_data[4]}
                               {site_data[5]}
                               {site_data[6]}
                               {site_data[7]}
                               {site_data[8]}

                               ### Planning

                               * [ ] - Check Programme for specific inspection objective
                               * [ ] - Check proposed dates with colleages
                               * [ ] - Agree suitable hotel with colleague
                               * [ ] - Email PFSO for XXXX for proposed dates
                               * [ ] - Email PFSO for XXXX for proposed dates
                               * [ ] - Email PFSO for XXXX for proposed dates
                               * [ ] - Enter confirmed dates and details on Mallard and create appointments
                               * [ ] - Put inspections on Mallard
                               * [ ] - Find suitable hotel
                               * [ ] - Book hotel
                               * [ ] - Book car
                               * [ ] - Book train
                               * [ ] - Book flight

                               ### Preparation:

                               * [ ] - Print off previous inspection letters
                               * [ ] - Print off matrix PDF from ~/Nextcloud/dft/Templates/inspection_template.pdf
                               * [ ] - Sync up hotel confirmation email with folder in Outlook
                               * [ ] - Sync up car confirmation email with folder in Outlook
                               * [ ] - Email hotel confirmation to Trello Week Board
                               * [ ] - Email car hire confirmation to Trello Week Board
                               * [ ] - Ensure I have copies of train tickets if applicable
                               * [ ] - Copy packing list to Week board: Inspection Packing
                               * [ ] - Pack according to packing list

                               ### Post Inspection:

                               * [ ] - Write up notes and add to Mallard
                               * [ ] - Get comments from fellow inspectors if required
                               * [ ] - Generate letter on Mallard
                               * [ ] - Spellcheck letter
                               * [ ] - Get comments on letter if required
                               * [ ] - Send letter to PFSO
                               * [ ] - Link letter to entry on Mallard
                               * [ ] - Close inspection once letter has been sent
                               * [ ] - Add a Waiting label to this card and park on Backlog

                               ### Comments:
                               """
    )
    card_uuid = uuid.uuid4()
    flattened_name = clean_site_name_for_path(inspection_name)
    card_file = str(
        os.path.join(
            CARDS_DIR, f"{flattened_name}_{str(inspection_date)}_{card_uuid}.twdft"
        )
    )

    with open(card_file, "wt") as f:
        f.write(template)
    if open_card:
        subprocess.run(f"vim {str(card_file)}", shell=True)
    if verbose:
        click.echo(click.style(f"Card created at {card_file}", fg="green"))
    return card_file, str(card_uuid)


def clean_site_name_for_path(site_name: str) -> str:
    """
    Helper function to clean bad characters from a site name
    so that they don't screw up our path making.
    """
    s = site_name
    s = site_name.lower()
    s = s.lstrip()
    s = s.rstrip()
    s = s.replace(" ", "-")
    s = s.replace("&", "and")
    s = s.replace("/", "-")
    s = s.replace("(", "-")
    s = s.replace(")", "-")
    s = s.replace("{", "-")
    s = s.replace("}", "-")
    return s


def get_card_file(task_number):
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    target = ""
    try:
        task = tw.tasks.pending().get(id=task_number)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry.")
        sys.exit(1)
    uuid = task["inspection_card_uuid"]
    for f in os.listdir(CARDS_DIR):
        if uuid in f:
            target = os.path.join(CARDS_DIR, f)
            break
    if not target:
        raise RuntimeError("Cannot find card for this task. Use task to delete.")
    return target, task


def task_card_path(id) -> str:
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    try:
        task = tw.tasks.pending().get(id=id)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry.")
        sys.exit(1)
    card_path = task["card_path"]
    return card_path


class CardComment:
    """
    A CardComment is created to write a timestamped comment into an inspection
    card.

    comment = CardComment(1, "We organised a lot of stuff today!")
    comment.write_to_card(verbose=True)

    """

    def __init__(self, task_id, comment):
        self._comment = comment
        self._task_id = task_id
        self._get_task()
        self._get_now()
        self.card_file = task_card_path(self._task_id)

    def _get_task(self):
        tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
        try:
            self._task = tw.tasks.pending().get(id=self._task_id)
        except Task.DoesNotExist:
            click.echo("That task ID does not exist. Sorry.")
            sys.exit(1)

    def _get_now(self):
        self._time_now = str(datetime.datetime.now())

    def write_to_card(self, verbose=False):
        for line in fileinput.input(self.card_file, inplace=1):
            print(line, end="")
            if "### Comments:" in line:
                print(f"#### {self._time_now}")
                print(self._comment)
                print("\n")

    def __str__(self):
        return f"<CardComment for  - task {self._task_id}: {self._comment}>"


def get_inspection_status_choices() -> Union[List[str], List]:
    """Find inspection_status.values uda line from config."""
    regex = r"^uda\.inspection_status\.values=(.+$)"
    with open(TWDFTRC, "r") as f:
        for line in f.readlines():
            m = re.match(regex, line)
            if m:
                return m.group(1).split(",")
    return []


def completion_facility_names() -> str:
    """
    A function that returns a space-separated string of facility
    names for use in fish completion.
    """
    with sqlite3.connect(os.path.join(TWDFT_DATA_DIR, DB_FILE)) as conn:
        c = conn.cursor()
        # sites_list = c.execute("""SELECT name FROM site WHERE site_type="Port" AND team='Maritime East'""").fetchall()
        sites_list = c.execute(
            """SELECT name FROM site WHERE site_type='Port'"""
        ).fetchall()
        sts = [f"{x[0].strip()}\n" for x in sites_list]
    return " ".join(sts)


def lookup_site_data(site) -> Dict[str, str]:  # type: ignore
    """Lookup details of site from database."""
    with sqlite3.connect(os.path.join(TWDFT_DATA_DIR, DB_FILE)) as conn:
        c = conn.cursor()
        data = c.execute(
            "SELECT * FROM site WHERE site_type='Port' AND name=?", (site,)
        ).fetchone()
        return data
