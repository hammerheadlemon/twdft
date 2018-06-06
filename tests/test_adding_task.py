import os
import pytest
import subprocess

python_executable = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
task = "tw-dft.py"


def test_basic_inspection_with_date(date_location):
    inspection = date_location[0]
    date = date_location[1]
    subprocess.run(
        f'{python_executable} {task} inspection -dt "{date}" -ds "{inspection}"',
        shell=True,
        stdout=subprocess.PIPE,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout.split(
        "\n"
    )
    assert f"{date} {inspection}" in output[3]


def test_basic_inspection_with_natural_date_and_location(date_natural_location):
    date = date_natural_location
    subprocess.run(
        f'{python_executable} {task} inspection -dt "{date}" -ds "Haddington"', shell=True, stdout=subprocess.PIPE,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8").stdout.split("\n")
    assert "2018-08-20 Haddington" in output[3]
