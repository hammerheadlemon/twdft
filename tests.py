import os
import pytest
import subprocess

python_executable = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
task = "tw-dft.py"


@pytest.fixture(params=[
    ('Port of Harwich', '2010-10-10'),
    ('Port of Felixtowe', '2010-10-11'),
    ('Port of Leith', '2019-05-01')
]
)
def test_data(request):
    print('\n--------------------------------------')
    print(f'fixturename     :   {request.fixturename}')
    print(f'scope           :   {request.scope}')
    print(f'function        :   {request.function.__name__}')
    print(f'cls             :   {request.cls}')
    print(f'module          :   {request.module.__name__}')
    print(f'fspath          :   {request.fspath}')
    yield request.param
    os.unlink("/home/lemon/.task-test/pending.data")


def test_basic_inspection_with_date(test_data):
    inspection = test_data[0]
    date = test_data[1]
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
    assert f"{date} {inspection}" in output[3]
