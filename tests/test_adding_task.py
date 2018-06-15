import subprocess
from twdft import twdft

PYTHON_EXECUTABLE = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
TASK = "twdft/twdft.py"


def test_basic_inspection_with_date(date_location):
    inspection = date_location[0]
    date = date_location[1]

    subprocess.run(
        f'twdft inspection "{inspection}" --inspectiondate "{date}"',
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
    assert f"{date} 10am forwardlook {inspection}" in output[3]


def test_basic_inspection_with_natural_date_and_location(date_natural_location):
    date = date_natural_location
    subprocess.run(
        f'twdft inspection "Haddington" --inspectiondate "{date}"', shell=True, stdout=subprocess.PIPE,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8").stdout.split("\n")
    assert "2018-08-20 10am forwardlook Haddington" in output[3]


def test_basic_inspection_with_natural_date_and_time_and_location(date_time_natural_location):
    date = date_time_natural_location['date']
    time = date_time_natural_location['time']
    subprocess.run(
        f'twdft inspection "Haddington" --inspectiondate "{date}" --inspectiontime "{time}"', shell=True, stdout=subprocess.PIPE,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8").stdout.split("\n")
    assert "2018-08-20 10:30am forwardlook Haddington" in output[3]


def test_task_no_subprocess():
    date = "20 November 2019"
    twdft.create_task(description="Testes!", date=date)

