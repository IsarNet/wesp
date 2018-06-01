"""
This module is responsible for the configfile. It loads it and matches its content to the defined
parameters in the module :mod:`wesp.cli_parser`.
The schema of the configfile it described in the class :class:`.ConfigSectionSchema`, while the parsing
is triggered and performed by :class:`.ConfigFileReader` and its derivative :class:`.ConfigFileProcessor`.

This module uses the click extension Click-configfile (https://github.com/click-contrib/click-configfile).

More information on how to add a parameter can be found in the individual classes.
"""

from click_configfile import ConfigFileReader, Param, SectionSchema, matches_section
import click
from click import BadParameter


class ConfigSectionSchema(object):
    """This class contains a description of each configfile section.
    Each section contains the parameter which can be configured by the configfile.

    To add a new section just create a new class and add a `@matches_section` decorator to it.
    Ensure that the name of the section is written in capital letters and does not contain any brackets.

    In the created class add the exact name of the parameter as defined in the :mod:`wesp.cli_parser` and
    set it to a a Click param.
    More information about the param types can be found here: http://click.pocoo.org/5/parameters/#parameter-types

    The last step is to add the schema to the parsing list in the class :class:`.ConfigFileProcessor` below.
    """

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
        iterations = Param(type=int)
        retries = Param(type=bool)
        channel = Param(type=bool)
        ap_name = Param(type=bool)
        rx_packets = Param(type=bool)
        tx_packets = Param(type=bool)
        ping = Param(type=bool)

    # parse data for section DEFAULT_OFF (default options)
    @matches_section("DEFAULT_OFF")
    class Default(SectionSchema):
        rssi_off = Param(type=bool)
        snr_off = Param(type=bool)
        data_rate_off = Param(type=bool)

    # parse data for section DEFAULT_OFF (default options)
    @matches_section("DATABASE")
    class Database(SectionSchema):
        db_name = Param(type=str)
        db_table = Param(type=str)
        db_address = Param(type=str)
        db_port = Param(type=str)
        db_user = Param(type=str)
        db_pass = Param(type=str)
        silent = Param(type=bool)


class ConfigFileProcessor(ConfigFileReader):
    """
    This class overloads the class :class:`.ConfigFileReader` from click-configfile.
    It allows to set the schemas of the sections.
    It also holds the path to the configfile (attribute *config_files*) but this field is set
    by the command :meth:`load_config` in :mod:`wesp.cli_parser`. It is triggered by the class :class:`.CustomGroup`.

    """
    config_section_schemas = [
        ConfigSectionSchema.General,  # PRIMARY SCHEMA
        ConfigSectionSchema.SNMP,
        ConfigSectionSchema.Options,
        ConfigSectionSchema.Default,
        ConfigSectionSchema.Database
    ]

    @classmethod
    def process_config_section(cls, config_section, storage):
        """
        This function overrides the *process_config_section* function
        of the class :class:`.ConfigFileReader`.
        It inverts all boolean values of the section *DEFAULT_OFF* to make all
        parameters in this section to off switches, since they describe the default behaviour.

        """

        try:
            # parse config section
            super(ConfigFileProcessor, cls).process_config_section(config_section, storage)

        # catch Bad Parameter exception to prevent error inside of click.
        # Reformat error to enhance user experience
        except BadParameter as ex:

            raise click.UsageError(
                "Usage error in configfile: `%s`" % ex)

        # if section is DEFAULT_OFF, then find corresponding dict in storage
        # and invert all values
        if config_section.name == "DEFAULT_OFF":

            for key, value in storage['DEFAULT_OFF'].items():

                if value:
                    storage['DEFAULT_OFF'][key] = False
                else:
                    storage['DEFAULT_OFF'][key] = True
