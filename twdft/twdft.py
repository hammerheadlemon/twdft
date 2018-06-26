import datetime
import uuid
import textwrap
import subprocess
import os
import parsedatetime

from typing import Tuple

from .helpers import completion_facility_names, lookup_site_data
from .helpers import get_inspection_status_choices as status_choice

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
        TWDFTRC = str(HOME / ".taskrc")

# set up the task data directory
if os.environ["TWDFT_DATA_DIR"]:
    TWDFT_DATA_DIR = os.environ["TWDFT_DATA_DIR"]
else:
    try:
        TWDFT_DATA_DIR = os.environ["TASKDATA"]
    except KeyError:
        TWDFT_DATA_DIR = str(HOME / ".task")

CARDS_DIR = HOME / ".tw-dft_cards"

# make the directory
if not os.path.exists(CARDS_DIR):
    os.makedirs(CARDS_DIR)


def _create_card(inspection_name: str, inspection_date: str,
                 inspection_time: str, open_card: bool, verbose: bool) -> Tuple[str, str]:

    site_data = lookup_site_data(inspection_name)
    site_notes = site_data.get('SiteNotes', 'No notes available')
    site_notes = site_notes.replace('\n', '')


    template = textwrap.dedent(f"""\
                               ## Inspection at port: {inspection_name}
                               ### Region: {site_data.get('TeamDesc', 'UNKNOWN')}
                               ### Site Category: {site_data.get('SiteCategoryDesc')}
                               ### PFSO: {site_data.get('PFSO', 'Unknown PFSO')}
                               ### Protection Category: {site_data.get('SubCategoryDesc', 'Unknown')}
                               ### Date: {inspection_date}
                               ### Time: {inspection_time}
                               ### Status: forwardlook
                               ### Last Inspection: {site_data.get('DateOfLastInspection', 'UNKNOWN')}

                               ### Site Notes:

                               {site_notes}

                               ### Address

                               {site_data.get('Address1', 'UNKNOWN')},
                               {site_data.get('Address2', 'UNKNOWN')},
                               {site_data.get('Town', 'UNKNOWN')},
                               {site_data.get('County', 'UNKNOWN')},
                               {site_data.get('Postcode', 'UNKNOWN')},

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
                               """)
    # TODO something about this abberration!
    card_uuid = uuid.uuid4()
    flattened_name = inspection_name.lower().replace(" ", "-").replace(
        "/", "-").replace("(", "-").replace(")", "-")

    card_file = str(CARDS_DIR / f"{flattened_name}_{str(inspection_date)}_{card_uuid}.twdft")

    with open(card_file, "wt") as f:
        f.write(template)
    if open_card:
        subprocess.run(f"vim {str(card_file)}", shell=True)
    if verbose:
        click.echo(click.style(f"Card created at {card_file}", fg='green'))
    return card_file, str(card_uuid)


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
            verbose=verbose)
        test_task['card_path'] = card_path[0]
        test_task['inspection_card_uuid'] = card_path[1]
        test_task.save()
    else:
        card_path = _create_card(
            inspection_name=kwargs['description'],
            inspection_date=kwargs['inspection_date'],
            inspection_time=kwargs['inspection_time'],
            open_card=False,
            verbose=verbose)
        test_task['card_path'] = card_path[0]
        test_task['inspection_card_uuid'] = card_path[1]
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
def __complete_site():
    """Implemented to provide list of facility names to fish completion"""
    click.echo(completion_facility_names())


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
def flip(config, task_number):
    """
    Flip the card on an inspection task to update metadata about the inspection.
    Opens in vim.
    """
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    task = tw.tasks.pending().get(id=task_number)
    card_path = task['card_path']
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
        task['inspection_status'] = inspectionstatus
        task.save()
        if config.verbose:
            click.echo(
                click.style(
                    f"Changed inspection_status of {task} to "
                    f"{inspectionstatus}",
                    fg="yellow"))


@cli.command()
@pass_config
@click.argument("task_number", type=click.INT)
def delete(config, task_number):
    """
    Removes a task and commits its card data to an annotation before deleting
    everything.
    """
    tw = TaskWarrior(data_location=(TWDFT_DATA_DIR), taskrc_location=TWDFTRC)
    target = ""
    try:
        task = tw.tasks.pending().get(id=task_number)
    except Task.DoesNotExist:
        click.echo("That task ID does not exist. Sorry")
        return
    uuid = task['inspection_card_uuid']
    for f in os.listdir(CARDS_DIR):
        if uuid in f:
            target = os.path.join(CARDS_DIR, f)
            break
    if not target:
        raise RuntimeError("Cannot find card for this task. Use task to delete.")
    with open(target, 'r', encoding="utf-8") as f:
        d = f.read()
        task.add_annotation(d)
        task.save()
    task.delete()
    os.unlink(target)


@cli.command()
@click.argument("port_facility", type=click.STRING)
@click.option(
    "--inspectiondate",
    default="today",
    help="Date of inspection - natural language is fine. Defaults to 'today'.")
@click.option(
    "--inspectiontime",
    default="10am",
    help="Time of inspection - defaults to '10am'")
@click.option("--opencard", default=False, is_flag=True)
@pass_config
def create_inspection(config, port_facility, inspectiondate, inspectiontime,
                      opencard):
    """
    Create an inspection at a PORT_FACILITY.
    """
    date = clean_date(inspectiondate)
    if config.verbose:
        click.echo(click.style(f"TASKRC is set to {TWDFTRC}", fg='yellow'))
        click.echo(
            click.style(f"TASKDATA is set to {TWDFT_DATA_DIR}", fg='yellow'))
        click.echo(
            click.style(
                f'Setting task description to "{port_facility}"', fg='green'))
        click.echo(
            click.style(
                f'Setting task inspection_date to "{date}"', fg='green'))
        click.echo(
            click.style(
                f'Setting task inspection_time to "{inspectiontime}"',
                fg='green'))
        create_task(
            description=port_facility.strip(),
            inspection_date=date,
            inspection_time=inspectiontime,
            inspection_status="forwardlook",
            open_card=opencard,
            verbose=True)
    create_task(
        description=port_facility.strip(),
        inspection_date=date,
        inspection_time=inspectiontime,
        inspection_status="forwardlook",
        open_card=opencard,
    )
