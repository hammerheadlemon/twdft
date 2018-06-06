import os
import pytest
import subprocess


@pytest.fixture
def remove_added_task():
    yield None
    os.unlink('/home/lemon/.task-test/pending.data')


def test_basic_inspection_with_date(remove_added_task):
    d = "2018-09-10"
    subprocess.run(
        f'/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6 tw-dft.py inspection -dt {d} -ds "Port of Harwich"',
        shell=True,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout.split('\n')
    assert "2018-09-10 Port of Harwich" in output[3]
