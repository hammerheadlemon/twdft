import re
import csv
import os
import datetime
import click
import fileinput

from typing import List, Union, Dict, Tuple
from tasklib import TaskWarrior, Task

from .env import TWDFTRC, CARDS_DIR, TWDFT_DATA_DIR, SITE_DATA_FILE


def get_card_file(task_number):
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    target = ""
    try:
        task = tw.tasks.pending().get(id=task_number)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry.")
        return
    uuid = task['inspection_card_uuid']
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
        return
    card_path = task['card_path']
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
            return

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
    with open(TWDFTRC, 'r') as f:
        for line in f.readlines():
            m = re.match(regex, line)
            if m:
                return m.group(1).split(',')
    return []



def completion_facility_names() -> str:
    """
    A function that returns a space-separated string of facility
    names for use in fish completion.
    """
    sites_list = []
    with open(os.path.join(str(TWDFT_DATA_DIR), SITE_DATA_FILE), 'r') as f:
        csv_reader = csv.DictReader(f)
        for line in csv_reader:
            if line['SiteTypeDesc'] == "Port":
                st = line['SiteName'].strip()
                sites_list.append(f"{st}\n")

    return " ".join(sites_list)


def lookup_site_data(site) ->Dict[str, str]: # type: ignore
    """Lookup details of site from site_dump.csv."""
    with open(os.path.join(str(TWDFT_DATA_DIR), SITE_DATA_FILE), 'r') as f:
        csv_reader = csv.DictReader(f)
        for line in csv_reader:
            if line['SiteTypeDesc'] == "Port" and line['SiteName'] == site:
                return line
