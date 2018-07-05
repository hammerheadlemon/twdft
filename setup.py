from setuptools import setup

setup(
    name="twdft",
    version="1.0",
    py_modules=['twdft'],
    install_requires=[
        'Click',
        'tasklib',
        'colorama',
        'parsedatetime',
    ],
    entry_points={
        'console_scripts': [
            'twdft_complete_site=twdft.twdft:__complete_site',
            'twdft=twdft.twdft:cli'
        ]
    }
)
