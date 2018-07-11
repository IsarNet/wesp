from setuptools import setup

setup(
    name='wesp',
    version='1.0',
    packages=['wesp'],
    url='https://github.com/IsarNet/wesp',
    license='GNU GPLv3',
    author='Marcel Rummens and Maximilian Tichter',
    description='This program will automatically monitor a WiFi device for defined parameters using '
                'the MAC or IPv4 address. In addition a ping can check if the client is reachable.',
    install_requires=[
        'easysnmp',
        'click>=6.7',
        'click_configfile',
        'click-man',
        'mysql-connector',
        'multiping',
        'IPy',
        'mysql-connector',
        'tzlocal',
        'Sphinx',
        'sphinxcontrib-websupport'
    ],
    entry_points={
        'console_scripts': ['wesp=wesp.cli_parser:cli_parser'],
    },
    zip_safe=False

)
