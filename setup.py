from setuptools import setup

setup(
    name="twdft",
    version="1.0",
    py_modules=['twdft'],
    install_requires=[
        'Click',
        'tasklib',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'twdft=twdft.twdft:cli'
        ]
    }
)
