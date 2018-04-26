# MARKER-EXAMPLE:
# -- FILE: example_command_with_configfile.py (ALL PARTS: simplified)
from click_configfile import ConfigFileReader, Param, SectionSchema, matches_section
import click

class ConfigSectionSchema(object):
    """Describes all config sections of this configuration file."""

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

    # parse data for section Options (non default options)
    @matches_section("OPTIONS")
    class Options(SectionSchema):
        interval = Param(type=click.IntRange(1, 300))
        retries = Param(type=bool)
        channel = Param(type=bool)

    # parse data for section DEFAULT_OFF (default options)
    @matches_section("DEFAULT_OFF")
    class Default(SectionSchema):
        rssi = Param(type=bool)
        channel = Param(type=bool)


class ConfigFileProcessor(ConfigFileReader):
    config_section_schemas = [
        ConfigSectionSchema.General, # PRIMARY SCHEMA
        ConfigSectionSchema.SNMP,
        ConfigSectionSchema.Options,
        ConfigSectionSchema.Default
    ]


    # -- SIMPLIFIED STORAGE-SCHEMA:
    #   section:person.*        -> storage:person.*
    #   section:person.alice    -> storage:person.alice
    #   section:person.bob      -> storage:person.bob

    # -- ALTERNATIVES: Override ConfigFileReader methods:
    #  * process_config_section(config_section, storage)
    #  * get_storage_name_for(section_name)
    #  * get_storage_for(section_name, storage)