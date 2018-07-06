import subprocess
import os
import sys

from colorama import init, Fore, Style, Back

from .helpers import completion_facility_names
from .helpers import get_inspection_status_choices as status_choice
from .helpers import task_card_path, get_card_file
from .helpers import CardComment
from .helpers import clean_date
from .helpers import clean_site_name_for_path
from .helpers import create_task
from .database import initial_db_setup
from .database import get_inspection_periods_all_sites
from .database import create_db_entry
from .database import clean_inspection_freq_data
from .database import days_since

from .env import TWDFTRC, TWDFT_DATA_DIR, DB_FILE

from tasklib import Task, TaskWarrior
import click

# you have to do this for colorama
init(autoreset=True)


def __complete_site():
    """Implemented to provide list of facility names to fish completion"""
    click.echo(completion_facility_names())


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


@cli.group()
def new():
    """Create a new something. Options are limited.
    Possible options are: inspection, proposed_inspection?, dn?
    """


"""
    TODO instead of creating the inspection type directly in taskwarrior,
    we want to create a new record in the database, therefore we need
    the requisite tables setting up for that. From that, we use THAT
    data to construct the taskwarrior item, maybe having a --mine option
    flag that will do that, allowing me to add inspections for other
    inspectors. These inspections are then concrete and have happened.
    These inspections become the record of what was done. They would need to
    be fully editable so that retrospective changes can be made. We have an
    edit command below that we can adapt.

    A proposed inspection could just have a 'proposed' flag set and then
    unset when it comes scheduled.
"""


@new.command()
@click.argument("site", type=click.STRING)
@click.option(
    "--inspectiondate",
    "-d",
    default="today",
    help="Date of inspection - natural language is fine. Defaults to 'today'.",
)
@click.option(
    "--inspectiontime",
    "-t",
    default="10am",
    help="Time of inspection - defaults to '10am'",
)
@click.option(
    "--opencard",
    "-o",
    default=False,
    is_flag=True,
    help="Immidiately opens the 'card' for the inspection in vim",
)
@click.option(
    "--mine",
    "-m",
    default=False,
    is_flag=True,
    help="The inspection will be added as a Taskwarrior task aswell as to the database.",
)
@click.option("--inspector", "-i", multiple=True)
@pass_config
def inspection(config, site, inspectiondate, inspectiontime, opencard, mine, inspector):
    """
    Create an inspection at a PORT_FACILITY.
    """
    date = clean_date(inspectiondate)
    if config.verbose:
        click.echo(click.style(f"TASKRC is set to {TWDFTRC}", fg="yellow"))
        click.echo(click.style(f"TASKDATA is set to {TWDFT_DATA_DIR}", fg="yellow"))
        click.echo(click.style(f'Setting task description to "{site}"', fg="green"))
        click.echo(click.style(f'Setting task inspection_date to "{date}"', fg="green"))
        click.echo(click.style(f"Setting inspectors to {inspector}", fg="green"))
        click.echo(
            click.style(
                f'Setting task inspection_time to "{inspectiontime}"', fg="green"
            )
        )
        # first, create the inspection in the db
        create_db_entry(
            site=site.strip(),
            inspection_date=date.isoformat(),
            inspection_time=inspectiontime,
            inspection_status="forwardlook",
            inspectors=inspector,
        )
        if mine:
            create_task(
                description=site.strip(),
                inspection_date=date,
                inspection_time=inspectiontime,
                inspection_status="forwardlook",
                inspectors=inspector,
                open_card=opencard,
                verbose=True,
            )
    # first, create the inspection in the db
    create_db_entry(
        site=site.strip(),
        inspection_date=date.isoformat(),
        inspection_time=inspectiontime,
        inspection_status="forwardlook",
        inspectors=inspector,
    )
    if mine:
        create_task(
            description=site.strip(),
            inspection_date=date,
            inspection_time=inspectiontime,
            inspection_status="forwardlook",
            open_card=opencard,
            inspectors=inspector,
        )


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@cli.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help="Override prompt and drop the database anyway",
    prompt="Are you sure you want to drop the database?",
)
def dropdb():
    """If there is a twdft.db file in TWDFT_DATA_DIR directory, it is removed and recreated.
    There must be a sites.csv file present for this. If you do not have a sites.csv file,
    export the Port and PSA Scheduling Aid report from Mallard, remove the header row,
    send to Libreoffice and save as 'sites.csv' and save it in TWDFT_DATA_DIR.

    All inspection planning data will be lost but site data will be re-established.

    This command will prompt for you to continue.
    """
    initial_db_setup()
    click.echo("Dropped all tables and recreated using site.csv!")


@cli.command()
@click.option(
    "--sortkey",
    default="along",
    help="Column on which to sort the table",
    type=click.Choice(["freq_target", "along", "days_since", "last_inspection"]),
)
@click.option(
    "--limit",
    default=None,
    help="Limit table to certain number of rows",
    type=click.INT,
)
@click.option(
    "--filter",
    default=None,
    help="Limit sites to a string - not fuzzy or fancy",
    type=click.STRING,
)
@click.option(
    "--team",
    type=click.Choice(["East", "West"]),
    help="Limite sites to a regional team",
)
@pass_config
def rate(config, sortkey, limit, filter, team):
    """
    Display data about inspection - last dates, frequency, etc.
    """
    db_file = DB_FILE
    # TODO Refactor the baws out of this
    d = get_inspection_periods_all_sites(db_file, team)
    data = clean_inspection_freq_data(d, sortkey, limit, filter)[1]
    print(
        Fore.CYAN
        + Style.BRIGHT
        + "{:<63}{:<1}{:^17}{:<1}{:^15}{:<1}{:^15}{:<1}{:^9}".format(
            "Site",
            "|",
            "Last Inspect.",
            "|",
            "Freq Target",
            "|",
            "Days Since",
            "|",
            "Along",
        )
    )
    print("{:-<121}".format(""))
    for item in data:
        if item[4] > 100:
            TERMCOL = Fore.RED
        else:
            TERMCOL = ""
        days = days_since(item[1])
        print("{:<63}".format(item[0]), end="")
        print("{:<1}".format("|"), end="")
        print("{:^17}".format(item[1].isoformat()), end="")
        print("{:<1}".format("|"), end="")
        print("{:^15}".format(item[2]), end="")
        print("{:<1}".format("|"), end="")
        print("{:^15}".format(days.days), end="")
        print("{:<1}".format("|"), end="")
        print(TERMCOL + "{:^9}".format(item[4]))
        print(Style.RESET_ALL, end="")
    if limit:
        print(
            Back.CYAN + Fore.BLACK + f"Limited to: {limit} rows | Sorted by: {sortkey}"
        )
    else:
        print(Back.CYAN + Fore.BLACK + f"All data | Sorted by: {sortkey}")


@cli.command()
@click.argument("task_id", type=click.INT)
@click.argument("comment", required=False, type=click.STRING)
@pass_config
def comment(config, task_id, comment):
    """
    Add a comment to an inspection task card. Add directly or you
    can pipe into the command, e.g xclip -o | twdft comment 1
    """
    # capturing sys.stdin() here allows me to pip in from stdout out of another
    # program such as xclip.
    # This will not allow me to put a breakpoint here though for some reason.
    if not comment:
        comment = sys.stdin.read()
    if config.verbose:
        c = CardComment(task_id, comment)
        click.echo(
            click.style(f"Added comment: {comment} to {c.card_file}", fg="yellow")
        )
        c.write_to_card()
    else:
        c = CardComment(task_id, comment)
        c.write_to_card()


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
def flip(config, task_number):
    """
    Flip the card on an inspection task to update metadata about the inspection.
    Opens in vim.
    """
    card_path = task_card_path(task_number)
    subprocess.run(f"vim {card_path}", shell=True)


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
@click.option("--inspectionstatus", type=click.Choice(status_choice()))
def edit(config, task_number, inspectionstatus):
    """
    Edit some element of an inspection task.
    """
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    try:
        task = tw.tasks.pending().get(id=task_number)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry")
        return
    if inspectionstatus:
        task["inspection_status"] = inspectionstatus
        task.save()
        if config.verbose:
            click.echo(
                click.style(
                    f"Changed inspection_status of {task} to " f"{inspectionstatus}",
                    fg="yellow",
                )
            )


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
def delete(config, task_number):
    """
    Removes a task and commits its card data to an annotation before deleting
    everything.
    """
    target = get_card_file(task_number)[0]
    task = get_card_file(task_number)[1]
    with open(target, "r", encoding="utf-8") as f:
        d = f.read()
        task.add_annotation(d)
        task.save()
    task.delete()
    os.unlink(target)


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
@click.argument("destination_directory", type=click.Path(exists=True))
def pdf(config, task_number, destination_directory):
    """
    Export the inspection card to a PDF file. Requires pandoc and wkhtmltopdf to
    be installed.
    """
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    try:
        task = tw.tasks.pending().get(id=task_number)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry.")
        sys.exit(1)
    card_path = task["card_path"]
    clean_name = clean_site_name_for_path(
        "_".join([task["description"], task["inspection_date"]])
    )
    subprocess.run(
        f"pandoc {card_path} -f markdown -t html5 -o {destination_directory}/{clean_name}.pdf",
        shell=True,
    )
