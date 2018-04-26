# MARKER-EXAMPLE:
# -- FILE: example_command_with_configfile.py (ALL PARTS: simplified)
from click_configfile import ConfigFileReader, Param, SectionSchema
from click_configfile import matches_section
import click


class ConfigSectionSchema(object):

    # Parse data for section General
    @matches_section("GENERAL")
    class General(SectionSchema):
        wlc_address = Param(type=str)
        client_address = Param(type=str)

    # parse data for section SNMP
    @matches_section("SNMP")
    class SNMP(SectionSchema):
        snmp_version = Param(type=click.Choice(['2c', '3']), default="2c")
        snmp_community = Param(type=str)
        snmp_user = Param(type=str)
        snmp_password = Param(type=str)
        snmp_encryption = Param(type=str)

    @matches_section("person.*")   # Matches multiple sections
    class Person(SectionSchema):
        name      = Param(type=str)
        birthyear = Param(type=click.IntRange(1990, 2100))


# This overloads the class ConfigFileProcessor to make the fields
# config_section_schemas and config_files available.
# config_files will be filled with a path with the
# command load_config in cli_parser
class ConfigFileProcessor(ConfigFileReader):

    def __init__(self):
        pass

    config_section_schemas = [
        ConfigSectionSchema.General,     # PRIMARY SCHEMA
        ConfigSectionSchema.SNMP,
    ]

    config_files = []
