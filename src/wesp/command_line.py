"""
This module is only an entry point for the script and does not have any tasks.

It will start the :mod:`wesp.cli_parser`
"""
from wesp.cli_parser import cli_parser


def main():
    cli_parser(obj={})