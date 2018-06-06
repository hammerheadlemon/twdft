import os
import pytest
import subprocess

python_executable = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
task = "tw-dft.py"


@pytest.fixture
def cleanup():
    yield None
    os.unlink("/home/lemon/.task-test/pending.data")


def test_basic_inspection_with_date(cleanup):
    date = "2018-09-10"
    inspection = "Port of Harwich"
    subprocess.run(
        f'{python_executable} {task} inspection -dt {date} -ds "{inspection}"',
        shell=True,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout.split(
        "\n"
    )
    assert "2018-09-10 Port of Harwich" in output[3]
