import click
from wesp.configfile import ConfigFileProcessor
from wesp.helper import decompress_nested_dict

# -- GLOBAL SETTINGS:
HELP_PARAMETERS = ['-h', '--help']


# this function will read and check the flag of the command
# load_config. It will inform about an missing file path or
# load the given or default config file.
def read_config_file_flag(self, ctx, args, idx):
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


# This class overloads click.Group
# It will ensure that the config file is loaded before any other parameter is evaluated
# In addition it will check, that the options are in the right order, because the
# required options (wlc_address, client_address, snmp_version) etc. need to be before
# any other optional options (-i, --ping etc.) to ensure that they are parsed before the rest.
# Otherwise the necessary data for the snmp session is not available at the time of the parsing of
# the optional options
class CustomGroup(click.Group):

    def parse_args(self, ctx, args):

        help_flag_set = False
        config_command_index = None

        # Iterate over args
        for idx, arg in enumerate(args):

            # check if help flag was set, if so exit loop
            # and let super function output help text
            if arg in HELP_PARAMETERS:
                help_flag_set = True
                break

            # check if load_config command is used
            # if so check if -f or --file flag is set
            # Then load config, has to be done before call to super
            if arg == "load_config":
                config_command_index = idx

        # Ensure help flag has priority
        if not help_flag_set:

            # load the config file, if command was given
            # has to happen before super call, otherwise values are not loaded
            if config_command_index is not None:
                read_config_file_flag(self, ctx, args, config_command_index)

        # add -h as help option in addition to --help
        ctx.help_option_names = HELP_PARAMETERS

        # run original or adapted argument list to parser
        super(CustomGroup, self).parse_args(ctx, args)


# This class overloads click.Options
# It enables the use of the only_required_if_version attribute
# This will ensure that that the option with this attribute is only
# required if the given version is presented.
# If version and option does not match (e.g. version 3 and a community string)
# an error is raised.
class OnlyRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.only_required_if_version = kwargs.pop('only_required_if_version')
        assert self.only_required_if_version, "'only_required_if_version' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.only_required_if_version
        ).strip()
        super(OnlyRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts

        # Check if present version and require one are not the same
        # If so change the required attribute of this option to False
        # If this option is presented anyway raise an error, because
        # it cannot be used with the given version
        if ctx.obj['snmp_version'] != self.only_required_if_version:

            self.required = False

            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with snmp version `%s`" % (
                        self.name, self.only_required_if_version))

        return super(OnlyRequiredIf, self).handle_parse_result(
            ctx, opts, args)