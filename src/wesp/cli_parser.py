import click
import time
import collections
from wesp.click_overloaded import *
from wesp.helper import *
from wesp.database import Database
from wesp.snmp import Snmp

# TODO Check Error Messages at wrong config file input, e.g. v2 instead of 2c
# TODO populate

# Order at which the Data is outputted, make sure to always add a None to each tuple!
order = [('channel', None), ('retries', None), ('snr_off', None),('rssi_off', None)]

# This dict will hold the requested information about the client
# If you want the entries to be sorted, like they are inputted or worked on
# (Default values will be last) then just remove the order argument from this statement:
CLIENT_DATA = collections.OrderedDict(order)


# This function will just add the given value
# in the context object under the param's name
def add_value_to_context(ctx, param, value):
    # print (param.name, value)
    ctx.obj[param.name] = value


# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value(ctx, param, flag_set):
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            pass
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get(getattr(AllParameter, param.name).oid)

        # TODO Remove
        # print(param.name)


# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value_with_mac(ctx, param, flag_set):
    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            pass
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(AllParameter, param.name).oid, ctx.obj['client_mac'])

        # TODO Remove
        # print('with mac', param.name)


# TODO Handle FQDN and Error
# This function will check if the WLC Address is a valid IP or FQDN
# If so it will set to the context, otherwise it will raise an error
def check_wlc_address(ctx, param, value):
    ip = check_ip_address(value)

    # If not IP is should be a FQDN
    if ip is None:
        ctx.obj[param.name] = value
    else:
        ctx.obj[param.name] = ip


# This function will validate the given Client Address
# and add it to the Context
def check_client_address(ctx, param, value):
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
              help='SNMP version, can either be 2c or 3')
#
@click.option('--community', '-c', 'snmp_community', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="2c",
              help='SNMP v2c community of WLC')
#
@click.option('--user', '-u', 'snmp_user', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 user of WLC')
#
@click.option('--pass', '-p', 'snmp_password', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 password/paraphrase of WLC')
#
@click.option('--encryption', '-e', 'snmp_encryption', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, is_eager=True, only_required_if_version="3",
              help='SNMP v3 encryption key of WLC')
#
# optional Options
#
@click.option('--interval', '-i', 'interval', required=False, callback=add_value_to_context,
              default=10, type=click.IntRange(1, 300),
              help='SNMP v3 User of WLC')
#
@click.option('--channel', '-ch', 'channel', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Channel used by Client')
#
@click.option('--retries', '-re', 'retries', required=False, callback=get_snmp_value_with_mac,
              is_flag=True,
              help='Number of Retries by Client')
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
# Function Definition
#
def cli_parser(ctx, wlc_address, client_address,
               snmp_version, snmp_community, snmp_user, snmp_password, snmp_encryption,
               interval, channel, retries,
               rssi_off, snr_off):
    """
    Example USAGE: WLC_AD CLI OPTIONS
    This tool ist awesome:

        WLC_..."""

    # TODO Remove
    # print("MAIN", ctx.default_map)


#
# Database Command
#
@cli_parser.command(cls=CommandAllowConfigFile)
#
@click.pass_context
#
@click.option("-n", "--name", "db_name", type=str, callback=add_value_to_context,
              default="WESP",
              help="Name of DB. Default: WESP")
#
@click.option("-t", "--table", "db_table", type=str, callback=add_value_to_context,
              default="data",
              help="Table to print in. Default: data")
#
@click.option("-a", "--address", "db_address", type=str, callback=add_value_to_context,
              default="127.0.0.1",
              help="IP address of database server. Default: 127.0.0.1 (localhost)")
#
@click.option("-po", "--port", "db_port", type=int, callback=add_value_to_context,
              default=3306,
              help="Port of database server. Default: 3306")
#
@click.option("-u", "--user", "db_user", callback=add_value_to_context,
              type=str,
              help="User of database server. ")
#
@click.option("-pa", "--password", "db_pass", callback=add_value_to_context,
              type=str,
              help="Password of database server.")
#
@click.option("-s", "--silent", "silent", callback=add_value_to_context,
              is_flag=True, default=False,
              help="Will only output data to the database")
#
#
def print_to_db(ctx, db_name, db_table, db_address, db_port, db_user, db_pass, silent):
    # Init Database with ctx
    # and a config which contains hostname, port etc.
    # and the create statement for the parameters listed in the definition file
    Database.init_database(ctx,
                           generate_db_conf_from_context(ctx),
                           generate_parameter_create_statement(),
                           generate_parameter_insert_statement(CLIENT_DATA))

    Database.insert_data_set(CLIENT_DATA)

    # TODO Remove
    # print ("DB", CLIENT_DATA)


# TODO add real Default Path
# TODO Add real Help Text
#
# Config File Command Definition
#
@cli_parser.command()
@click.option('-f', '--file', 'file_path', default="../../wesp_config.cfg", type=click.Path(exists=True),
              help="Optional Path to Config File")
@click.pass_context
def load_config(ctx, file_path):
    """Will load configfile. For more information see load_config --help.

    if no path is given the default path will be used

    """

    # TODO Remove
    # print("Load Config")

    # add path to Config File Processor
    ConfigFileProcessor.config_files = [file_path]


# This function will run after all parameters have been parsed
# It will make the CLI Output and the depending on the settings the
# Insert to the DB
# It also repeats the process until the user kills the programm
@cli_parser.resultcallback()
def process_result(result, **kwargs):
    click.echo('All parameters parsed')

    # get reference of context
    ctx = click.get_current_context()

    # if not silent print results to cli
    if not ctx.obj['silent']:
        print(generate_cli_output(CLIENT_DATA))

    # if print_to_db command was set, insert data
    if Database.is_ready():
        Database.insert_data_set(CLIENT_DATA)

    while True:
        # sleep for interval seconds
        time.sleep(ctx.obj['interval'])

        # fetch newest info from wlc
        update_client_data(ctx)

        # if not silent print to output again
        if not ctx.obj['silent']:
            print(generate_cli_output(CLIENT_DATA))

        # if print_to_db command was set, insert data again
        if Database.is_ready():
            Database.insert_data_set(CLIENT_DATA)


def update_client_data(ctx):

    # for each option stored in CLIENT_DATA search for corresponding
    # option object and runs in callback function again. This will update the
    # value
    for key, value in CLIENT_DATA.items():

        if value is not None:
            option = get_option_with_name(ctx.command, ctx, key)

            # run callback function for this option again
            option.callback(ctx, option, True)



