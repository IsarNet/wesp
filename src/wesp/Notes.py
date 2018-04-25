def parse_args(self, ctx, args):
    help_flag_set = False
    config_command_index = None
    first_command_index = None
    reorder_needed = check_position_of_options(self, ctx, args)

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

        # Search for index of first command
        # Check if arg is a command
        if reorder_needed and \
                first_command_index is None and \
                arg in self.commands:
            first_command_index = idx

    # Ensure help flag has priority
    if not help_flag_set:

        # load the config file, if command was given
        # has to happen before super call, otherwise values are not loaded
        if config_command_index is not None:
            read_config_file_flag(self, ctx, args, config_command_index)

        # if options are not up front, reorder parameter
        if reorder_needed:
            args = reorder_options(self, ctx, args, first_command_index)

    # add -h as help option in addition to --help
    ctx.help_option_names = HELP_PARAMETERS

    # run original or adapted argument list to parser
    super(AdaptiveGroup, self).parse_args(ctx, args)


def get_usage(self, ctx):
    print ("USAGE")
    super(AdaptiveGroup, self).get_usage(self, ctx)


# enable CLI command of form WLC_ADDRESS CLIENT_ADDRESS [OPTIONS] COMMAND
# click requires to be the OPTIONS be up front
# this function will reorder the parameter to be the Options up front
# In addition it will check, if WLC or Client Address is missing
def reorder_options(self, ctx, args, idx):
    # get all params and save them into all_params
    all_options = []
    for param in self.get_params(ctx):
        all_options.extend(param.opts)

    # First OPTION is at position 3, because 1 and 2 are WLC and Client Address
    # If commands are given (ind != None) the options span until the first command
    # If no commands are given the options span until the end of args
    options = args[2:idx] if idx is not None else args[2:]

    # Remove Options from Argument List
    args = [e for e in args if e not in options]

    # Check if required Arguments are given, if not raise Error
    if len(args) == 0 or args[0] in all_options or args[0] in self.commands:
        raise_critical_error(self, ctx, "Missing argument WLC_ADDRESS")

    if len(args) == 1 or args[1] in all_options or args[1] in self.commands:
        raise_critical_error(self, ctx, "Missing argument CLIENT_ADDRESS")

    # Append Options in the beginning
    args = options + args

    return args

    def get_usage(self, ctx):
        print ("USAGE")
        super(AdaptiveGroup, self).get_usage(ctx)