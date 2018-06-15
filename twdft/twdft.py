import datetime
import os
import parsedatetime

from tasklib import Task, TaskWarrior
import click

from pathlib import Path

HOME = Path.home()

# set up the taskrc file
if os.environ['TWDFTRC']:
    TWDFTRC = os.environ['TWDFTRC']
else:
    try:
        TWDFTRC = os.environ['TASKRC']
    except KeyError:
        TWDFTRC = HOME / '.taskrc'

# set up the task data directory
if os.environ['TWDFT_DATA_DIR']:
    TWDFT_DATA_DIR = os.environ['TWDFT_DATA_DIR']
else:
    try:
        TWDFT_DATA_DIR = os.environ['TASKDATA']
    except KeyError:
        TWDFT_DATA_DIR = HOME / '.task'


CARDS_DIR = HOME / ".tw-dft_cards"

# make the directory
if not os.path.exists(CARDS_DIR):
    os.makedirs(CARDS_DIR)


def create_task(**kwargs):
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)

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


class Config:
    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--verbose', is_flag=True)
@pass_config
def cli(config, verbose):
    """
    Wrapper for task command, specifically for handling DfT inspection data. For personal use!
    Required argument: INSPECTION, a string describing the inspection (e.g. the facility name).
    """
    config.verbose = verbose


@cli.command()
@click.argument('inspection', type=click.STRING)
@click.option('--inspectiondate', default='today', help="Date of inspection - natural language is fine. Defaults to 'today'.")
@click.option('--inspectiontime', default='10am', help="Time of inspection - defaults to '10am'")
@pass_config
def inspection(config, inspection, inspectiondate, inspectiontime):
    """
    Create an inspection.
    """
    date = clean_date(inspectiondate)
    if config.verbose:
        click.echo(f"Setting task description to \"{inspection}\"")
        click.echo(f"Setting task inspection_date to \"{date}\"")
        click.echo(f"Setting task inspection_time to \"{inspectiontime}\"")
    create_task(description=inspection, inspection_date=date, inspection_time=inspectiontime)
