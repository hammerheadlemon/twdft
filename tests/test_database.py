import os
import subprocess

from twdft.database import initial_db_setup
from twdft.env import TWDFT_DATA_DIR


def test_initial_set_up():
    initial_db_setup()
    db_filename = "twdft.db"
    db_path = os.path.join(TWDFT_DATA_DIR, db_filename)

    inspector_name = "Bob"
    subprocess.run(
        f"sqlite3 {db_path} 'INSERT INTO inspector (first_name) VALUES (\"{inspector_name}\")'",
        check=True,
        shell=True,
    )
    output = subprocess.run(
        f"sqlite3 {db_path} 'SELECT * FROM inspector'",
        stdout=subprocess.PIPE,
        encoding="utf-8",
        check=True,
        shell=True,
    )
    assert "Bob" in output.stdout
