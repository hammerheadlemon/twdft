import os
import subprocess

from twdft.database import initial_db_setup
from twdft.env import TWDFT_DATA_DIR


def test_initial_set_up():
    initial_db_setup()
    db_filename = "twdft.db"
    db_path = os.path.join(TWDFT_DATA_DIR, db_filename)

    inspector_name = "Bob"
    subprocess.run(f"sqlite3 -line {db_path} 'INSERT INTO inspectors (first_name) VALUES=({inspector_name})';", shell=True)
    output = subprocess.run("sqlite3 db_path 'SELECT * FROM inspectors;'", stdout=subprocess.PIPE, shell=True)
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    assert "Bob" in output
