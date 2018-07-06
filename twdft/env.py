import os
import click
import sys

# set up the taskrc file
try:
    TWDFTRC = os.environ["TWDFTRC"]
except KeyError:
    click.echo(f"Cannot find TWDFTRC environment variable. Set it!")
    sys.exit(1)

# set up the task data directory
try:
    TWDFT_DATA_DIR = os.environ["TWDFT_DATA_DIR"]
except KeyError:
    click.echo(f"Cannot find TWDFT_DATA_DIR environment variable. Set it!")
    sys.exit(1)

try:
    CARDS_DIR = os.environ["TWDFT_CARD_DIR"]
except KeyError:
    click.echo(f"Cannot find TWDFT_CARD_DIR environment variable. Set it!")
    sys.exit(1)

# make the directory
if not os.path.exists(CARDS_DIR):
    os.makedirs(CARDS_DIR)

SITE_DATA_FILE = 'site_address.csv'

DB_FILE = os.path.join(TWDFT_DATA_DIR, 'twdft.db')

INSPECTORS = [
    "Matt Lemon",
    "Graham East",
    "Tim Light",
    "Simon Corkill",
    "Paul Nagle",
]
