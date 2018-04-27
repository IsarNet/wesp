from setuptools import setup

setup(
    name='wesp',
    version='',
    packages=['wesp'],
    url='',
    license='',
    author='marcel',
    author_email='',
    description='',
    install_requires=[
        'easysnmp',
        'click',
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
