# MARKER-EXAMPLE:
# -- FILE: example_command_with_configfile.py (ALL PARTS: simplified)
from click_configfile import ConfigFileReader, Param, SectionSchema
from click_configfile import matches_section
import click

class ConfigSectionSchema(object):
    """Describes all config sections of this configuration file."""

    @matches_section("foo")
    class Foo(SectionSchema):
        name    = Param(type=str)
        flag    = Param(type=bool, default=True)
        numbers = Param(type=int, multiple=True)
        filenames = Param(type=click.Path(), multiple=True)

    @matches_section("person.*")   # Matches multiple sections
    class Person(SectionSchema):
        name      = Param(type=str)
        birthyear = Param(type=click.IntRange(1990, 2100))


class ConfigFileProcessor(ConfigFileReader):
    config_files = ["foo.ini", "../wesp_config.cfg"]
    config_section_schemas = [
        ConfigSectionSchema.Foo,     # PRIMARY SCHEMA
        ConfigSectionSchema.Person,
    ]

    # -- SIMPLIFIED STORAGE-SCHEMA:
    #   section:person.*        -> storage:person.*
    #   section:person.alice    -> storage:person.alice
    #   section:person.bob      -> storage:person.bob

    # -- ALTERNATIVES: Override ConfigFileReader methods:
    #  * process_config_section(config_section, storage)
    #  * get_storage_name_for(section_name)
    #  * get_storage_for(section_name, storage
    # )
