import click
from wesp.oids import Oids
from wesp.click_overloaded import *
from wesp.helper import *
from wesp.database import Database
from wesp.snmp import Snmp
from easysnmp import Session, EasySNMPConnectionError


# TODO populate
# TODO leave empty to ensure user inputted order is outputed.
# This dict will hold the requested information about the client
CLIENT_DATA = {}

CONTEXT_SETTINGS = dict(default_map=ConfigFileProcessor.read_config())


# This function will init the SNMP Session with the data from the CLI
def init_snmp_session(ctx):
    session = None

    # Create v2c Session
    if ctx.obj['snmp_version'] == "2c":
        session = Session(hostname=ctx.obj['wlc_address'],
                          community=ctx.obj['snmp_community'],
                          version=2)

    # TODO Make v3 work
    # Create v3 Session
    # Default settings:
    # security_level = auth_with_privacy
    # auth_protocol = SHA
    # privacy_protocol = AES
    if ctx.obj['snmp_version'] == "3":
        try:
            session = Session(hostname=ctx.obj['wlc_address'],
                              security_level='auth_with_privacy',
                              security_username=ctx.obj['snmp_user'],
                              privacy_password=ctx.obj['snmp_password'],
                              privacy_protocol='AES',
                              auth_password=ctx.obj['snmp_encryption'],
                              auth_protocol='SHA',
                              version=3)
        except EasySNMPConnectionError, e:
            raise click.UsageError(
                "SNMP Connection Error: `%s`" % (
                    e.message))

    # init Snmp with generated Session
    Snmp(session)

    # Check if the Client Mac Address was given
    # or only the Client IP,
    # because Mac address is mandatory to find Cisco attributes
    if 'client_mac' not in ctx.obj:
        ctx.obj['client_mac'] = Snmp.get_mac_from_ip(ctx.obj['client_ip'])


# This function will just add the given value
# in the context object under the param's name
def add_value_to_context(ctx, param, value):


   # print(param.name, value, ctx.default_map)

    ctx.obj[param.name] = value






# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value (ctx, param, flag_set):

    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            init_snmp_session(ctx)

        # TODO Uncomment
        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        #CLIENT_DATA[param.name] = Snmp.get(getattr(Oids, param.name))
        print(param.name)


# This function will request and save an attribute based on the corresponding OID and Mac Address
def get_snmp_value_with_mac (ctx, param, flag_set):

    # ensure flag is set
    if flag_set:
        # ensure SNMP Class is ready and initialized
        if not Snmp.is_ready():
            init_snmp_session(ctx)

        # TODO Uncomment
        # load data via get request and save it a the corresponding slot in the CLIENT_DATA dictionary
        #CLIENT_DATA[param.name] = Snmp.get_by_mac_address(getattr(Oids, param.name), ctx.obj['client_mac'])
        print('with mac', param.name)


# TODO Handle FQDN and Error
# This function will check if the WLC Address is a valid IP or FQDN
# If so it will set to the context, otherwise it will raise an error
def check_wlc_address(ctx, param, value):
    if check_ip_address(value):
        print(value)
    else:
        print("Bad IP")

    ctx.obj[param.name] = value


# This function will validate the given Client Address
# and add it to the Context
def check_client_address(ctx, param, value):
    # ensure that Client Address is either a valid IP or Mac Address
    # If so add it to the Context Object for further use

    if check_ip_address(value):
        ctx.obj['client_ip'] = value
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
@click.group(chain=True, cls=CustomGroup, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
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
@click.option('--rssi_off', '-ro', 'rssi', required=False, callback=get_snmp_value,
              is_flag=True, default=True, flag_value=False,
              help='Will deactivate the Output of the RSSI (Received Signal Strength Indication) of the WLC')
#
# Function Definition
#
def cli_parser(ctx, wlc_address, client_address,
               snmp_version, snmp_community, snmp_user, snmp_password, snmp_encryption,
               interval, channel, retries, rssi):
    """
    Additional USAGE: WLC_AD CLI OPTIONS
    This tool ist awesome:

        WLC_..."""
    print "CLI Parser Main"


#
# Database Command
#
@cli_parser.command()
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

@click.pass_context
def print_to_db(ctx, db_name, db_table, db_address, db_port, db_user, db_pass, silent):

    print ("Database run")

    Database.init_database(ctx.obj['db_table'], ctx.obj['db_name'], generate_db_conf_from_context(ctx))




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
