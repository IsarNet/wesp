import click
from wesp.definitions import *
from wesp.click_overloaded import *
from wesp.helper import *
from wesp.database import Database
from wesp.snmp import Snmp

# TODO Check Error Messages at wrong config file input, e.g. v2 instead of 2c
# TODO populate
# TODO leave empty to ensure user inputted order is outputed.
# This dict will hold the requested information about the client
CLIENT_DATA = {}


# This function will just add the given value
# in the context object under the param's name
def add_value_to_context(ctx, param, value):
    # print (param.name, value)
    ctx.obj[param.name] = value


# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value (ctx, param, flag_set):

    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            pass
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get(getattr(AllParameter, param.name).oid)
        print(param.name)


# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value_with_mac (ctx, param, flag_set):

    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            pass
            Snmp(ctx)

        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(AllParameter, param.name).oid, ctx.obj['client_mac'])
        print('with mac', param.name)


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

    print("MAIN", ctx.default_map)


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

    print("DB", ctx.default_map)

    # Init Database with ctx
    # and a config which contains hostname, port etc.
    # and the create statement for the parameters listed in the definition file
    Database.init_database(ctx,
                           generate_db_conf_from_context(ctx),
                           generate_parameter_create_statement(),
                           generate_parameter_insert_statement(CLIENT_DATA))

    Database.insert_data_set(CLIENT_DATA)

    print ("DB", CLIENT_DATA)





# TODO add real Default Path
# TODO Add real Help Text
#
# Config File Command Definition
#
@cli_parser.command()
@click.option('-f','--file', 'file_path', default="../../wesp_config.cfg", type=click.Path(exists=True), help="Optional Path to Config File")
@click.pass_context
def load_config(ctx, file_path):

    """Will load configfile. For more information see load_config --help.

    if no path is given the default path will be used

    """
    print("Load Config")
    # add path to Config File Processor
    ConfigFileProcessor.config_files = [file_path]

    print(ctx.default_map)


# This function will run after all parameters have been parsed
@cli_parser.resultcallback()
def process_result(result, **kwargs):
    click.echo('All parameters parsed')
    print(CLIENT_DATA)