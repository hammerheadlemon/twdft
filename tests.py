import os
import pytest
import subprocess

python_executable = "/home/lemon/.local/share/virtualenvs/tw-dev-qpewB347/bin/python3.6"
task = "tw-dft.py"


@pytest.fixture(params=['2010-10-10', '2010-10-11', '2019-05-01'])
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
    date = test_data
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
    assert f"{test_data} Port of Harwich" in output[3]
