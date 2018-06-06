import os
import datetime
import subprocess
import argparse
import sys

from tasklib import Task, TaskWarrior

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


def run(*args):
    subprocess.run(f"task {' '.join(args)}", check=True, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices=['inspection', 'dft-task'], help="The type of object to create.", nargs="?", default=None)
    parser.add_argument("-dt", "--date", help="The date of the inspection")
    parser.add_argument("-ds", "--description", help="The description of the inspection")
    args = vars(parser.parse_args())

    if args['type'] == 'inspection':
        if args['date'] and args['description']:
            create_task(description=args['description'], inspection_date=args['date'])


if __name__ == "__main__":
    main()
