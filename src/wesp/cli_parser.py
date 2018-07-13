"""
This module's main task is the parsing of the CLI parameters. This is done using the extension
Click (http://click.pocoo.org/5/). Click separates three different parameters: commands, options and arguments.

This module consists of one Group (:meth:`cli_parser`), which has two sub commands: :meth:`load_config`
and :meth:`print_to_db`

:meth:`cli_parser` contains all options to set up the main program (e.g. client address and SNMP options),
as well as optional parameters to turn on or off certain features (e.g. RSSI, SNR, Ping).

The command :meth:`load_config` triggers the loading of a config file for easier use. It has only one option
to load a different file than the default one. Note the priority of inputs (1 has the highest priority):\n
1. CLI \n
2. Configfile\n
3. Default values\n
This means that an option set in the configfile can be overwritten by setting a flag on the CLI.

The command :meth:`print_to_db` triggers the output to the database. Through its options one is able to set
the basic connection settings as well as database and table names. For detailed usage run `print_to_db -h`.
Database and table are created if they don't exist. The create statement is built automatically based on the
parameters defined in the module :mod:`wesp.definitions`.

The project has been developed and tested using a Cisco 2500er series WLC (SW version 8.3.130.0) and
Cisco Aironet 802 11n Draft 2.0 Dual Band APs.


"""
import collections
from multiping import *
from wesp.click_overloaded import *
from wesp.helper import *
from wesp.database import Database
from wesp.snmp import Snmp
from datetime import datetime
import tzlocal

order = [('channel', None), ('retries', None), ('snr_off', None), ('ap_name', None), ('rssi_off', None)]
"""
This attribute sets the order in which the data is outputted. Make sure to always add a *None* to each tuple!
"""

"""
This dict will hold the requested information about the client.
The order at which the data is outputted can be changed by editing the order attribute in this module. 
If you want the entries to be sorted, in the order they are inputted or worked on
(Default values will be last) then just remove the order argument from this statement:
"""
CLIENT_DATA = collections.OrderedDict(order)


def add_value_to_context(ctx, param, value):
    """
    This function will just add the given value to the context object under the param's name

    :param ctx: current context object
    :param param: calling parameter
    :param value: value of parameter
    """
    ctx.obj[param.name] = value


def get_snmp_value(ctx, param, flag_set):
    """
    This function will request and save an attribute based on the corresponding OID. The OID
    is retrieved from the class :class:`wesp.definitions.AllParameter` using the name of the parameter.


    :param ctx: current context object
    :param param: calling parameter
    :param flag_set: True if flag is set, false if not
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get(getattr(AllParameter, param.name).oid)


def get_snmp_value_with_mac(ctx, param, flag_set):
    """
    This function will request and save an attribute based on the corresponding OID and MAC address. The OID
    is retrieved from the class :class:`wesp.definitions.AllParameter` using the name of the parameter. The MAC
    address is converted into the decimal format and appended to the OID.

    :param ctx: current context object
    :param param: calling parameter
    :param flag_set: True if flag is set, false if not
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(AllParameter, param.name).oid, ctx.obj['client_mac'])


def check_wlc_address(ctx, param, value):
    """
    This function will check if the WLC address is a valid IP or a resolvable FQDN address.
    If so it will add it to the context, otherwise it will raise an error.

    :param ctx: current context object
    :param param: calling parameter
    :param value: value of parameter
    """
    ip = check_ip_address(value)

    # If not IP is should be a FQDN
    if ip is None:

        # test if hostname can be resolved
        try:
            ip = socket.gethostbyname(value)
            ctx.obj[param.name] = ip

        # if not raise error
        except socket.error as err:
            raise click.UsageError(
                "Host Resolve error: '%s'" % err)
    else:
        ctx.obj[param.name] = ip


def check_client_address(ctx, param, value):
    """
    This function will validate the given client address and add it to the context.

    :param ctx: current context object
    :param param: calling parameter
    :param value: value of parameter
    """
    # ensure that Client Address is either a valid IP or Mac Address
    # If so add it to the Context Object for further use
    if check_ip_address(value) is not None:
        ctx.obj['client_ip'] = check_ip_address(value)

    else:
        if check_mac_address(value):
            ctx.obj['client_mac'] = value

        # Otherwise raise an error
        else:
            raise click.BadParameter(
                "Bad Parameter: `%s` is not a valid Hex Mac Address" % (
                    value,))


def get_ap_name(ctx, param, flag_set):
    """
    This function requests the name of the associated AP of the client.
    Therefore it will first request the MAC address of the AP from the *cldcClientTable*
    and then use the address to find its name in the *clDLApBootTable*.

    :param ctx: current context object
    :param param: calling parameter
    :param flag_set: True if flag is set, false if not
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # get mac address of associated AP
        ap_mac = Snmp.get_by_mac_address(getattr(AllParameter, 'ap_mac_address').oid, ctx.obj['client_mac'])

        # Retrieve name of AP using Mac Address form above using custom separator ' '
        CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(AllParameter, param.name).oid, ap_mac, ' ')


def get_ping(ctx, param, flag_set):
    """
    This function will ping the client from the device which runs this script.

    :param ctx: current context object
    :param param: calling parameter
    :param flag_set: True if flag is set, false if not
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # wrap address in list
        address_list = [ctx.obj['client_ip']]

        # try to ping, if not root raise error
        try:
            # Ping the addresses up to 4 times (initial ping + 3 retries), over the
            # course of 2 seconds. This means that for those addresses that do not
            # respond another ping will be sent every 0.5 seconds.
            responses, no_responses = multi_ping(address_list, timeout=2, retry=3)

        except MultiPingError as err:
            raise click.UsageError(
                "Ping error: '%s'" % err)

        # check if client responded
        if len(no_responses) > 0:
            CLIENT_DATA[param.name] = False
        else:
            # Result will be in milliseconds and correct to 5 decimal places
            CLIENT_DATA[param.name] = round(responses[ctx.obj['client_ip']] * 1000, 5)


"""________ MAIN COMMAND _____________"""


#
# Click Options
#
@click.group(chain=True, cls=CustomGroup, invoke_without_command=True,
             help="This program will automatically monitor a WiFi device for defined parameters using "
                  "the MAC or IPv4 address. In addition a ping can check if the client is reachable. "
                  "Per Default the results are outputted on the CLI but an command exists to write the data "
                  "to a database. All parameters can be inputted via a configfile. \n\n"
                  "An example usage can be found above, while details on the options can be found below:")
#
# make sure group has access to context
@click.pass_context
#
# Address Options
#
@click.option('--WLC', '-W', 'wlc_address', required=True, is_eager=True, callback=check_wlc_address,
              help='IP or FQDN address of WLC')
#
@click.option('--CLI', '-C', 'client_address', required=True, is_eager=True, callback=check_client_address,
              help='IP or MAC address of Client')
#
# SNMP Options
#
@click.option('--version', '-v', 'snmp_version', required=False, callback=add_value_to_context,
              type=click.Choice(['2c', '3']), is_eager=True, default="2c",
              help='SNMP version. ', show_default=True)
#
@click.option('--community', '-c', 'snmp_community', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="2c",
              help='SNMP v2c community of WLC. ', show_default=True)
#
@click.option('--user', '-u', 'snmp_user', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 user of WLC. ', show_default=True)
#
@click.option('--pass', '-p', 'snmp_password', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 password/paraphrase of WLC. ', show_default=True)
#
@click.option('--encryption', '-e', 'snmp_encryption', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 encryption key of WLC. ', show_default=True)
#
# optional Options
#
@click.option('--interval', '-in', 'interval', required=False, callback=add_value_to_context,
              default=10, type=click.IntRange(1, 300), show_default=True,
              help='Interval in seconds at which data is requested from the WLC. Range from 1-300 allowed. ')
#
@click.option('--iterations', '-it', 'iterations', required=False, callback=add_value_to_context,
              default=-1, type=int, show_default=False,
              help='Iterations after which the this program should be ended. '
                   'NOTE: Every value below 0 will cause infinite loop. [default: unlimited]  ')
#
@click.option('--channel', '-ch', 'channel', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Channel used by Client')
#
@click.option('--retries', '-re', 'retries', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of Retries by Client')
#
@click.option('--ap_name', '-ap', 'ap_name', required=False, callback=get_ap_name,
              is_flag=True,
              help='Name of Access Point the client is associated with')
#
@click.option('--rx_packets', '-rx', 'rx_packets', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of client received packets')
#
@click.option('--tx_packets', '-tx', 'tx_packets', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of client transmitted packets')
#
@click.option('--ping', '-pi', 'ping', required=False, callback=get_ping,
              is_flag=True,
              help='ICMP Ping to client from this device in ms. NOTE: root privileges required')

#
# Default Options off
#
@click.option('--rssi_off', '-ro', 'rssi_off', required=False, callback=get_snmp_value_with_mac,
              is_flag=True, default=True, flag_value=False,
              help='Will deactivate the Output of the RSSI (Received Signal Strength Indication) of the WLC')
#
@click.option('--snr_off', '-so', 'snr_off', required=False, callback=get_snmp_value_with_mac,
              is_flag=True, default=True, flag_value=False,
              help='Will deactivate the Output of the SNR (Signal to Noise Ratio) of the WLC')
#
@click.option('--data_rate_off', '-do', 'data_rate_off', required=False, callback=get_snmp_value_with_mac,
              is_flag=True, default=True, flag_value=False,
              help='Will deactivate the Output of the Client Data Rate')

#
# Function Definition
#
def cli_parser(ctx, wlc_address, client_address,
               snmp_version, snmp_community, snmp_user, snmp_password, snmp_encryption,
               interval, iterations, channel, retries, ap_name, rx_packets, tx_packets, ping,
               rssi_off, snr_off, data_rate_off):
    """

    This function represents the main command and contains all options ranging from WLC/client information,
    SNMP options to all options which enable or disable the output of certain parameters. A list of the
    associated options can be found below. Since this is a *Click Group* all other commands (e.g. for
    configfile and database) are sub commands of this command. The name of this group is *cli_parser*.

    Note, that this group command does not contain any logic, handling of the options is done in the
    specified callbacks. Click expects the click options to be inside the arguments of this command, although
    they are not used.

    Fore more information about click options and it's attributes see: http://click.pocoo.org/5/options/,
    http://click.pocoo.org/5/parameters/#differences and http://click.pocoo.org/5/commands/



    The following callbacks are implemented and may be used for future options:

    :meth:`add_value_to_context`: adds the value of the option to the context, without any modification. The name of the
    option is used as key.

    :meth:`get_snmp_value`: will search in :class:`wesp.definitions.AllParameter` for a matching OID and requests the
    data via GET from the WLC. The result is added to the context, using the name of the option.

    :meth:`get_snmp_value_with_mac`: will do the same as the latter function but will include the MAC address of the
    client to get client specific data.

    :meth:`check_wlc_address`: will check if the given address is a valid IP address or a resolvable hostname. If so it
    will add it to the context using the name of the option.

    :meth:`check_client_address`: will check if the given address is a valid IP or MAC address. If so it will add
    it to the context using the name of the option.

    :meth:`get_ap_name`: will retrieve the name of the AP of a client. For details see the function itself. The name of
    the option is used as key.

    :meth:`get_ping`: will try to ping the client. For details see the function itself. The name of the option
    is used as key.


    :param ctx: current Context
    :param wlc_address: click option (is not being used)
    :param client_address: click option (is not being used)
    :param snmp_version: click option (is not being used)
    :param snmp_community: click option (is not being used)
    :param snmp_user: click option (is not being used)
    :param snmp_password: click option (is not being used)
    :param snmp_encryption: click option (is not being used)
    :param interval: click option (is not being used)
    :param iterations: click option (is not being used)
    :param channel: click option (is not being used)
    :param retries: click option (is not being used)
    :param ap_name: click option (is not being used)
    :param rx_packets: click option (is not being used)
    :param tx_packets: click option (is not being used)
    :param ping: click option (is not being used)
    :param rssi_off: click option (is not being used)
    :param snr_off: click option (is not being used)
    :param data_rate_off: click option (is not being used)

    """


"""________ DATABASE COMMAND _____________"""


#
# Database Command
#
@cli_parser.command(cls=CommandAllowConfigFile,
                    short_help="Will output the results to a database. For more information see print_to_db --help.",
                    help="Will output the results to a database. Details on the options can be found below. \n\n"
                         "Ensure that an existing MySQL database is running at the default or given address. "
                         "The SQL installation is not part of this program! \n\n"
                         "The Database and the table will be created if they do not exist.")
#
@click.pass_context
#
@click.option("-n", "--name", "db_name", type=str, callback=add_value_to_context,
              default="WESP", show_default=True,
              help="Name of Database. It will be created, if it does not exist. ")
#
@click.option("-t", "--table", "db_table", type=str, callback=add_value_to_context,
              default="data", show_default=True,
              help="Name of table to print in. It will be created, if it does not exist. ")
#
@click.option("-a", "--address", "db_address", type=str, callback=add_value_to_context,
              default="127.0.0.1", show_default=True,
              help="IP address of database server. ")
#
@click.option("-po", "--port", "db_port", type=int, callback=add_value_to_context,
              default=3306, show_default=True,
              help="Port of database server. ")
#
@click.option("-u", "--user", "db_user", callback=add_value_to_context,
              type=str, default="root", show_default=True,
              help="User of database server. ")
#
@click.option("-pa", "--password", "db_pass", callback=add_value_to_context,
              type=str, default="", show_default=True,
              help="Password of database server.")
#
@click.option("-s", "--silent", "silent", callback=add_value_to_context,
              is_flag=True, default=False,
              help="Will only output data to the database and nothing to the CLI")
#
#
def print_to_db(ctx, db_name, db_table, db_address, db_port, db_user, db_pass, silent):
    """

    This function represents the command *print_to_db*, it takes the options and uses them
    to create a connection to the database. It also generates the statements for the creation of
    the table and the insertion of data into this table.

    Note that the Click options have to be inside the arguments of this command, since they are expected by
    click. The actual handling of them is done in the corresponding callback.


    :param ctx: current Context
    :param db_name: click option (is not being used)
    :param db_table: click option (is not being used)
    :param db_address: click option (is not being used)
    :param db_port: click option (is not being used)
    :param db_user: click option (is not being used)
    :param db_pass: click option (is not being used)
    :param silent: click option (is not being used)

    """

    # Init Database with ctx
    # and a config which contains hostname, port etc.
    # and the create statement for the parameters listed in the definition file,
    # as well as the insert statement
    Database.init_database(ctx,
                           generate_db_conf_from_context(ctx),
                           generate_parameter_create_statement(),
                           generate_parameter_insert_statement(CLIENT_DATA))


"""________ CONFIGFILE COMMAND _____________"""


#
# Config File Command Definition
#
@cli_parser.command(cls=CommandAllowConfigFile,
                    short_help = "Will load configfile. For more information see load_config --help",
                    help = "Will load configfile. If no path is given the default path will be used, "
                           "which can be found below.")
#
@click.option('-f', '--file', 'file_path', default="./wesp_config.cfg", type=click.Path(exists=True),
              help="Optional Path to Config File", show_default=True)
@click.pass_context
def load_config(ctx, file_path):
    """
    Will set the path of the configfile inside the class :class:`.ConfigFileProcessor`. The actual loading is done
    in the function :meth:`read_config_file_flag` in the module :mod:`wesp.click_overloaded`.

    Note that the Click options have to be inside the arguments of this command, since they are expected by
    Click.

    :param ctx: current Context
    :param file_path: click option (is not being used)

    """

    # add path to Config File Processor
    ConfigFileProcessor.config_files = [file_path]


@cli_parser.resultcallback()
def process_result(result, **kwargs):
    """
    This function will run after all parameters have been parsed.
    It will make the CLI output and depending on the settings the
    insert to the database.
    It also repeats the process until the user kills the program or
    an end condition is met

    """

    # get reference of context
    ctx = click.get_current_context()

    # check if at least one parameter has been turned on
    if 'client_ip' not in ctx.obj or 'client_mac' not in ctx.obj:
        raise click.UsageError(
            "Parameter Error: All parameters have been turned off'")

    # get current time with timezone
    current_time = datetime.now(tzlocal.get_localzone())

    # if not silent print results to CLI
    if 'silent' not in ctx.obj or not ctx.obj['silent']:
        print(generate_cli_output(CLIENT_DATA, ctx, current_time))

    # if print_to_db command was set, insert data
    if Database.is_ready():
        Database.insert_data_set(CLIENT_DATA, ctx, current_time)

    # decrease iteration by one
    ctx.obj['iterations'] -= 1

    # loop until iterations condition is met
    # if iteration is on default value -1 this will never happen,
    # since iteration will only get smaller and never hit 0
    while ctx.obj['iterations'] != 0:

        # decrease iteration by one
        ctx.obj['iterations'] -= 1

        # sleep for interval seconds
        time.sleep(ctx.obj['interval'])

        # fetch newest info from wlc
        error = update_client_data(ctx)

        # only output if no error, if at least one parameter raised an error
        # output error and proceed to next iteration
        if not error:

            # get current time with timezone
            current_time = datetime.now(tzlocal.get_localzone())

            # if not silent print to output again
            if 'silent' not in ctx.obj or not ctx.obj['silent']:
                print(generate_cli_output(CLIENT_DATA, ctx, current_time))

            # if print_to_db command was set, insert data again
            if Database.is_ready():
                # catch exception, if db connections drop during session
                # only output error message
                try:
                    Database.insert_data_set(CLIENT_DATA, ctx, current_time)
                except click.UsageError as ex:
                    click.echo(str(ex) + " ... Entry lost. Trying to reconnect ...", err=True)

        else:
            # output other error
            click.echo("Client not available ... Retrying next time ... (%s)" % (str(error)), err=True)


def update_client_data(ctx):
    """
    This function will update the values by re-retrieving the values from the WLC.

    :param ctx: current Context

    """

    # for each option stored in CLIENT_DATA search for corresponding
    # option object and runs in callback function again. This will update the
    # value
    for key, value in CLIENT_DATA.items():

        if value is not None:
            option = get_option_with_name(ctx.command, ctx, key)

            try:
                # run callback function for this option again
                option.callback(ctx, option, True)
            except click.UsageError as ex:
                return ex

    return False


