import datetime
import os
import parsedatetime

from tasklib import Task, TaskWarrior
import click

from pathlib import Path

HOME = Path.home()
TEST_TWRC = HOME / '.test_twrc'
CARDS_DIR = HOME / ".tw-dft_cards"

# make the directory
if not os.path.exists(CARDS_DIR):
    os.makedirs(CARDS_DIR)


def create_task(**kwargs):
    tw = TaskWarrior(data_location=(HOME / '.task-test'), taskrc_location=TEST_TWRC)

    test_task = Task(tw, **kwargs)
    test_task.save()


def clean_date(date):
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(date)
    if parse_status == 1:
        # it is a date object
        parsed_obj = datetime.date(*time_struct[:3])
    elif parse_status == 3:
        # it is a datetime
        parsed_obj = datetime.datetime(*time_struct[:6])
    return parsed_obj


@click.group()
def cli():
    pass


@cli.command()
@click.argument('inspection', type=click.STRING)
@click.option('--inspectiondate', default='today', help="Date of inspection - natural language is fine. Defaults to 'today'.")
@click.option('--inspectiontime', default='10am', help="Time of inspection - defaults to '10am'")
def inspection(inspection, inspectiondate, inspectiontime):
    """
    Wrapper for task command, specifically for handling DfT inspection data. For personal use!
    Required argument: INSPECTION, a string describing the inspection (e.g. the facility name).
    """
    date = clean_date(inspectiondate)
    create_task(description=inspection, inspection_date=date, inspection_time=inspectiontime)
