"""
This module's main task is the parsing of the CLI parameters. This is done using the extension
click (http://click.pocoo.org/5/). Click separates three different parameters: commands, options and arguments.

This module is made up of one Group (:meth:`cli_parser`), which has two sub commands: :meth:`load_config`
and :meth:`print_to_db`

:meth:`cli_parser` contains all options to set up the main program (e.g. Client address and SNMP options),
as well as optional parameters to turn on or off (e.g. RSSI, SNR, Ping).

The command :meth:`load_config` triggers the loading of a config file for easier use. It has only one option
to load a different file than the default one. Note the priority of input:\n
1. CLI \n
2. Configfile\n
3. Default values\n
This means that although you defined an option in the configfile you can overwrite it by setting a flag on the CLI.

The command :meth:`print_to_db` triggers the output to the database. Through its options one is able to set
the basic connection settings as well as database and table names. For detailed usage run `print_to_db -h`.
Database and table are created, if they don't exist. The create statement is built automatically based on the
parameters defined in the module :mod:`wesp.definitions`.

"""
import collections
from multiping import *
from wesp.click_overloaded import *
from wesp.helper import *
from wesp.database import Database
from wesp.snmp import Snmp

# TODO Check Error Messages at wrong config file input, e.g. v2 instead of 2c
# TODO populate

# Order at which the Data is outputted, make sure to always add a None to each tuple!
order = [('channel', None), ('retries', None), ('snr_off', None),('rssi_off', None)]


"""
This dict will hold the requested information about the client
If you want the entries to be sorted, like they are inputted or worked on
(Default values will be last) then just remove the order argument from this statement:
"""
CLIENT_DATA = collections.OrderedDict(order)


def add_value_to_context(ctx, param, value):
    """
    This function will just add the given value in the context object under the param's name

    :param ctx:
    :param param:
    :param value:
    :return: Nothing, value will be stored in context object
    """
    ctx.obj[param.name] = value


def get_snmp_value(ctx, param, flag_set):
    """
    This function will request and save an attribute based on the corresponding OID and Mac Address

    :param ctx:
    :param param:
    :param flag_set:
    :return: Nothing, value will be stored in context object
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get(getattr(AllParameter, param.name).oid)

        # TODO Remove
        # print(param.name)


def get_snmp_value_with_mac(ctx, param, flag_set):
    """
    This function will request and save an attribute based on the corresponding OID and Mac Address

    :param ctx:
    :param param:
    :param flag_set:
    :return: Nothing, value will be stored in context object
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(AllParameter, param.name).oid, ctx.obj['client_mac'])

        # TODO Remove
        # print('with mac', param.name)


# TODO Handle FQDN and Error
def check_wlc_address(ctx, param, value):
    """
    This function will check if the WLC Address is a valid IP or FQDN
    If so it will set to the context, otherwise it will raise an error

    :param ctx:
    :param param:
    :param value:
    """
    ip = check_ip_address(value)

    # If not IP is should be a FQDN
    if ip is None:
        ctx.obj[param.name] = value
    else:
        ctx.obj[param.name] = ip


def check_client_address(ctx, param, value):
    """
    This function will validate the given Client Address and add it to the Context

    :param ctx:
    :param param:
    :param value:
    :return: Nothing, value will be stored in context object
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
    This function requests the Name of the associated AP of the Client.
    Therefore it will first request the MAC address of the AP from the cldcClientTable
    and then using the address to find its name in the clDLApBootTable
    :param ctx: Context of ...
    :param param:
    :param flag_set: True if flag is set, otherwise false
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
    This function will ping the client from the device, which runs this script.
    :param ctx:
    :param param:
    :param flag_set:
    :return: Nothing, value will be stored in context object
    """
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            Snmp(ctx)

        # wrap address in list
        address_list = [ctx.obj['client_ip']]

        # Ping the addresses up to 4 times (initial ping + 3 retries), over the
        # course of 2 seconds. This means that for those addresses that do not
        # respond another ping will be sent every 0.5 seconds.
        responses, no_responses = multi_ping(address_list, timeout=2, retry=3)

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
@click.group(chain=True, cls=CustomGroup, invoke_without_command=True)
#
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
# TODO is eager ensures parsing before everything else
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
@click.option('--rx_packages', '-re', 'rx_packages', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of client received packages')
#
@click.option('--tx_packages', '-re', 'tx_packages', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of client transmitted packages')
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
               interval, iterations, channel, retries, ap_name, rx_packages, tx_packages, ping,
               rssi_off, snr_off, data_rate_off):
    """
    Example USAGE: wesp -W wlc_address -C client_address [SNMP Options] [Options]
    This tool ist awesome:

        WLC_..."""

    # TODO Remove
    # print("MAIN", ctx.default_map)


"""________ DATABASE COMMAND _____________"""


#
# Database Command
#
@cli_parser.command(cls=CommandAllowConfigFile)
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

    :param ctx:
    :param db_name:
    :param db_table:
    :param db_address:
    :param db_port:
    :param db_user:
    :param db_pass:
    :param silent:
    :return:
    """

    # Init Database with ctx
    # and a config which contains hostname, port etc.
    # and the create statement for the parameters listed in the definition file
    Database.init_database(ctx,
                           generate_db_conf_from_context(ctx),
                           generate_parameter_create_statement(),
                           generate_parameter_insert_statement(CLIENT_DATA))


"""________ CONFIGFILE COMMAND _____________"""


# TODO add real Default Path
# TODO Add real Help Text
#
# Config File Command Definition
#
@cli_parser.command(cls=CommandAllowConfigFile)
@click.option('-f', '--file', 'file_path', default="../../wesp_config.cfg", type=click.Path(exists=True),
              help="Optional Path to Config File")
@click.pass_context
def load_config(ctx, file_path):
    """Will load configfile. For more information see load_config --help.

    if no path is given the default path will be used

    """

    # add path to Config File Processor
    ConfigFileProcessor.config_files = [file_path]


@cli_parser.resultcallback()
def process_result(result, **kwargs):
    """
    This function will run after all parameters have been parsed.
    It will make the CLI Output and depending on the settings the
    Insert to the DB.
    It also repeats the process until the user kills the program or
    an end end condition is met

    :param result:
    :param kwargs:
    :return: Nothing
    """
    click.echo('All parameters parsed')

    # get reference of context
    ctx = click.get_current_context()

    # if not silent print results to CLI
    if 'silent' not in ctx.obj or not ctx.obj['silent']:
        print(generate_cli_output(CLIENT_DATA, ctx))

    # if print_to_db command was set, insert data
    if Database.is_ready():
        Database.insert_data_set(CLIENT_DATA, ctx)

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
        update_client_data(ctx)

        # if not silent print to output again
        if 'silent' not in ctx.obj or not ctx.obj['silent']:
            print(generate_cli_output(CLIENT_DATA, ctx))

        # if print_to_db command was set, insert data again
        if Database.is_ready():
            Database.insert_data_set(CLIENT_DATA, ctx)


def update_client_data(ctx):
    """
    This function will update the values by re-retrieving the values from the WLC

    :param ctx: current Context
    :return: Nothing, results are saved in Context

    """

    # for each option stored in CLIENT_DATA search for corresponding
    # option object and runs in callback function again. This will update the
    # value
    for key, value in CLIENT_DATA.items():

        if value is not None:
            option = get_option_with_name(ctx.command, ctx, key)

            # run callback function for this option again
            option.callback(ctx, option, True)



