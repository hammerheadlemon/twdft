import datetime
import textwrap
import os
import parsedatetime

from tasklib import Task, TaskWarrior
import click

from pathlib import Path

HOME = Path.home()

# set up the taskrc file
if os.environ["TWDFTRC"]:
    TWDFTRC = os.environ["TWDFTRC"]
else:
    try:
        TWDFTRC = os.environ["TASKRC"]
    except KeyError:
        TWDFTRC = HOME / ".taskrc"

# set up the task data directory
if os.environ["TWDFT_DATA_DIR"]:
    TWDFT_DATA_DIR = os.environ["TWDFT_DATA_DIR"]
else:
    try:
        TWDFT_DATA_DIR = os.environ["TASKDATA"]
    except KeyError:
        TWDFT_DATA_DIR = HOME / ".task"


CARDS_DIR = HOME / ".tw-dft_cards"

# make the directory
if not os.path.exists(CARDS_DIR):
    os.makedirs(CARDS_DIR)


def _create_card(inspection_name, inspection_date, inspection_time, open_card, verbose):
    template = textwrap.dedent(
        f"""\
                               # Inspection at port: {inspection_name}
                               ## Date: {inspection_date}
                               ## Time: {inspection_time}

                               ## Post Inspection:

                               [ ] - Write up notes and add to Mallard
                               [ ] - Get comments from fellow inspectors if required
                               [ ] - Generate letter on Mallard
                               """
    )
    flattened_name = inspection_name.lower().replace(" ", "-")
    tmpfile = CARDS_DIR / f"{flattened_name}_{str(inspection_date)}"
    with open(tmpfile, "wt") as f:
        f.write(template)
    if open_card:
        os.system("vim " + str(tmpfile))
    if verbose:
        click.echo(click.style(f"Card created at {tmpfile}", fg='green'))
    return tmpfile


def create_task(**kwargs):
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)

    verbose = kwargs.pop('verbose', False)
    open_card = kwargs.pop('open_card', False)

    test_task = Task(tw, **kwargs)
    test_task.save()
    if open_card:
        card_path = _create_card(
            inspection_name=kwargs['description'],
            inspection_date=kwargs['inspection_date'],
            inspection_time=kwargs['inspection_time'],
            open_card=True,
            verbose=verbose
        )
        test_task['card_path'] = card_path
        test_task.save()
    else:
        card_path = _create_card(
            inspection_name=kwargs['description'],
            inspection_date=kwargs['inspection_date'],
            inspection_time=kwargs['inspection_time'],
            open_card=False,
            verbose=verbose
        )
        test_task['card_path'] = card_path
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
@click.option("--verbose", is_flag=True)
@pass_config
def cli(config, verbose):
    """
    Wrapper for task command, specifically for handling DfT inspection data. For personal use!

    To run in test mode, set the following environment variables:

        \b
        set TWDFTRC ~/.test_twrc
        set TWDFT_DATA_DIR ~/.test_tw_data

    To run in production mode, unset these environment variables:

        \b
        set -e TWDFTRC
        set -e TWDFT_DATA_DIR
    """
    config.verbose = verbose


@cli.command()
@click.argument(
    "port_facility",
    type=click.STRING
)
@click.option(
    "--inspectiondate",
    default="today",
    help="Date of inspection - natural language is fine. Defaults to 'today'.",
)
@click.option(
    "--inspectiontime",
    default="10am",
    help="Time of inspection - defaults to '10am'"
)
@click.option(
    "--opencard",
    default=False,
    is_flag=True)
@pass_config
def create_inspection(config, port_facility, inspectiondate, inspectiontime, opencard):
    """
    Create an inspection at a PORT_FACILITY.
    """
    date = clean_date(inspectiondate)
    if config.verbose:
        click.echo(click.style(f"TASKRC is set to {TWDFTRC}", fg='yellow'))
        click.echo(click.style(f"TASKDATA is set to {TWDFT_DATA_DIR}", fg='yellow'))
        click.echo(click.style(f'Setting task description to "{port_facility}"', fg='green'))
        click.echo(click.style(f'Setting task inspection_date to "{date}"', fg='green'))
        click.echo(click.style(f'Setting task inspection_time to "{inspectiontime}"', fg='green'))
        create_task(
            description=port_facility,
            inspection_date=date,
            inspection_time=inspectiontime,
            inspection_status="forwardlook",
            open_card=opencard,
            verbose=True
        )
    create_task(
        description=port_facility,
        inspection_date=date,
        inspection_time=inspectiontime,
        inspection_status="forwardlook",
        open_card=opencard,
    )
