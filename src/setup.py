from setuptools import setup

setup(
    name='wesp',
    version='1.0',
    packages=['wesp'],
    url='https://github.com/IsarNet/wesp',
    license='GNU GPLv3',
    author='Marcel Rummens and Maximilian Tichter',
    description='TODO',
    install_requires=[
        'easysnmp',
        'Click',
        'click_configfile',
        'mysql-connector',
        'multiping',
        'IPy',
        'mysql-connector',
    ],
    entry_points={
        'console_scripts': ['wesp=wesp.command_line:main'],
    },
    zip_safe=False

)
