import csv
import os

# these variables need to go elsewhere...
TWDFT_DATA_DIR = os.environ['TWDFT_DATA_DIR']


def completion_facility_names():
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
