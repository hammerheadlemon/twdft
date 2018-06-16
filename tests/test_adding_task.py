import subprocess
from twdft import twdft

PYTHON_EXECUTABLE = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
TASK = "twdft/twdft.py"


def test_basic_inspection_with_date(date_location):
    inspection = date_location[0]
    date = date_location[1]

    subprocess.run(
        f'twdft create_inspection "{inspection}" --inspectiondate "{date}"',
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
    assert f"{date}" in output[3]
    assert f"{inspection}" in output[3]


def test_no_command_issued(date_natural_location):
    """Run without the 'create_inspection' command itself."""
    date = date_natural_location
    err = subprocess.run(
        f'twdft "Haddington" --inspectiondate "{date}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8").stderr.split("\n")
    assert "Error: No such command \"Haddington\"" in err[2]


def test_basic_inspection_with_natural_date_and_time_and_location(date_time_natural_location):
    date = date_time_natural_location['date']
    time = date_time_natural_location['time']
    subprocess.run(
        f'twdft create_inspection "Haddington" --inspectiondate "{date}" --inspectiontime "{time}"', shell=True, stdout=subprocess.PIPE,
    )
    output = subprocess.run(
        "env TASKRC=~/.test_twrc TASKDATA=~/.task-test task inspections",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8").stdout.split("\n")
    assert "2018-08-20 10:30am forwardlook Haddington" in output[3]

