import datetime
import os
import parsedatetime
import subprocess
import argparse

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices=['inspection', 'dft-task'], help="The type of object to create.", nargs="?", default=None)
    parser.add_argument("-dt", "--date", help="The date of the inspection")
    parser.add_argument("-ds", "--description", help="The description of the inspection")
    args = vars(parser.parse_args())
    date = clean_date(args['date'])

    if args['type'] == 'inspection':
        if args['date'] and args['description']:
            create_task(description=args['description'], inspection_date=date)


if __name__ == "__main__":
    main()
