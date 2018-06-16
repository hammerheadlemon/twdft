import re
import csv
import os

from typing import List, Union

# these variables need to go elsewhere...
TWDFT_DATA_DIR = os.environ['TWDFT_DATA_DIR']
TWDFTRC = os.environ['TWDFTRC']


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
    with open(os.path.join(str(TWDFT_DATA_DIR), 'site_dump.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for line in csv_reader:
            if line['SiteTypeDesc'] == "Port":
                st = line['SiteName'].strip()
                sites_list.append(f"{st}\n")

    return " ".join(sites_list)
