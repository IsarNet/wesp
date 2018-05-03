"""
This module contains overloads of click classes to allow custom reactions.
The class CustomGroup overloads the class click.Group to allow custom parsing and rearranging of the options

The class OnlyRequiredIf overloads the class click.Option to allow an option to be required if a certain
snmp version has been set

The class CommandAllowConfigFile overloads the class click.Command to allow a command to access the configfile
"""

import click
import sys
from wesp.configfile import ConfigFileProcessor
from wesp.helper import decompress_nested_dict, get_option_with_name

# -- GLOBAL SETTINGS:
HELP_PARAMETERS = ['-h', '--help']
"""Flags of Help parameter"""


def read_config_file_flag(self, ctx, args, idx):
    """
    This function will read and check the flag of the command
    load_config. It will inform about an missing file path or
    load the given or default config file.

    :param self: Reference to CustomGroup
    :param ctx: Reference to current Context
    :param args: list of given args
    :param idx: index at which the load_config command has been found
    :raise: BadParameter if argument for -f option is missing
    :return: Nothing, result will be saved in default map of context

    """

    # Check if file flag is set, if so load given file
    # Existence of file flag requires at least index +1 arguments
    if len(args) > idx + 1 and args[idx + 1] in ['-f', '--file']:

        # check if argument file path is given
        # Existence requires at least index + 2 arguments
        if len(args) <= idx + 2:
            # TODO Change Usage Output
            raise click.BadParameter(
                "Bad Parameter: Missing argument for -f/--file")

        # Invoke load_config with given file
        ctx.invoke(self.get_command(ctx, "load_config"), file_path=args[idx + 2])

    # If not load default file
    else:
        ctx.invoke(self.get_command(ctx, "load_config"))

    # load config file and ensure that default map consists of a non nested dict
    ctx.default_map = decompress_nested_dict(ConfigFileProcessor.read_config())


class CustomGroup(click.Group):
    """
    This class overloads click.Group
    It will ensure that the config file is loaded before any other parameter is evaluated and
    the required options do not suppress the help option.
    In addition the version parameter is moved to the front of the args list to enable the class
    OnlyRequiredIf to set an option (e.g. community) only to required if an version is set (e.g. 2c)

    """

    def parse_args(self, ctx, args):
        """
        Overloads the function parse_args of click.Group, which runs before the parsing of
        the parameter of the super class

        :param ctx: current Context object
        :param args: list of given parameters
        :return: result of super function

        """

        # define help vars
        help_flag_set = False
        version_flag_index = None
        config_command_index = None
        command_found = None

        # per default no config is loaded
        ctx.obj['load_conf'] = False

        # retrieve version flags of version option and list of commands
        version_flags = get_option_with_name(self, ctx, 'snmp_version').opts
        command_list = self.list_commands(ctx)

        # Iterate over args
        for idx, arg in enumerate(args):

            if arg in command_list:
                command_found = arg;

            # check if help flag was set, if so exit loop
            # and let super function output help text
            if arg in HELP_PARAMETERS:
                help_flag_set = True
                break

            # check if version flag was set and if it is on
            # the first position. If not it has to be moved to the
            # first
            if arg in version_flags \
                    and idx != 0:
                version_flag_index = idx

            # check if load_config command is used
            # if so check if -f or --file flag is set
            # Then load config, has to be done before call to super
            if arg == "load_config":
                config_command_index = idx

        # Ensure help flag has priority
        # If flat is set, print help and do not call super
        if help_flag_set:

            if command_found is not None:
                # print command specific help
                click.echo(self.get_command(ctx, command_found).get_help(ctx))

            else:
                # print general help
                click.echo(self.get_help(ctx))

            # end program
            sys.exit(0)

        else:

            # Ensure that the version flag is the first parameter
            # If it was not set, set the context to the default value
            if version_flag_index is not None:
                version_flag = args[version_flag_index:version_flag_index + 2]
                args = version_flag + args

            else:
                ctx.obj['snmp_version'] = get_option_with_name(self, ctx, 'snmp_version').default

            # load the config file, if command was given
            # has to happen before super call, otherwise values are not loaded
            if config_command_index is not None:
                read_config_file_flag(self, ctx, args, config_command_index)
                # set context var to true, so sub command will load the conf as well
                ctx.obj['load_conf'] = True

            # add -h as help option in addition to --help
            ctx.help_option_names = HELP_PARAMETERS

            # run original or adapted argument list to parser
            return super(CustomGroup, self).parse_args(ctx, args)


class OnlyRequiredIf(click.Option):
    """
    This class overloads click.Options
    It enables the use of the only_required_if_version attribute
    This will ensure that that the option with this attribute is only
    required if the given version is presented.
    If version and option does not match (e.g. version 3 and a community string)
    an error is raised.
    """

    def __init__(self, *args, **kwargs):
        """
        This function overloads the init function of click.Option and set specific help texts and
        warnings
        :param args:
        :param kwargs:

        """

        self.only_required_if_version = kwargs.pop('only_required_if_version')
        assert self.only_required_if_version, "'only_required_if_version' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' NOTE: This argument is mutually exclusive with snmp version %s' %
                          self.only_required_if_version
                          ).strip()
        super(OnlyRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        """
        Overloads the function parse_args of click.Option, which runs after the super class has parsed the arguments
        and handles the reaction to it.

        :param ctx: current Context
        :param opts: options given by user
        :param args: arguments given by user
        :return: result of super function

        """

        option_present = self.name in opts

        # Check if present version and require one are not the same
        # If so change the required attribute of this option to False
        # If this option is presented anyway raise an error, because
        # it cannot be used with the given version
        if ctx.obj['snmp_version'] != self.only_required_if_version:

            self.required = False

            # if option is present, although the option is not needed raise error
            if option_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with snmp version `%s`" % (
                        self.name, self.only_required_if_version))

        return super(OnlyRequiredIf, self).handle_parse_result(
            ctx, opts, args)


class CommandAllowConfigFile(click.Command):
    """
    Overrides the click.Command class to allow a command
    to read the config file

    """

    def parse_args(self, ctx, args):
        """
        Overloads the function parse_args of click.Command, which runs before the parsing of
        the parameter of the super class.

        :param ctx: current Context
        :param args: arguments given by user
        :return: result of super function

        """

        # check if CustomGroup found load_config command
        # if so read it into this command's default map

        if ctx.obj['load_conf']:
            # load config file and ensure that default map consists of a non nested dict
            ctx.default_map = decompress_nested_dict(ConfigFileProcessor.read_config())

        # add -h as help option in addition to --help
        ctx.help_option_names = HELP_PARAMETERS

        # run original or adapted argument list to parser
        return super(CommandAllowConfigFile, self).parse_args(ctx, args)
