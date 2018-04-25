import click
from wesp.oids import Oids
from wesp.configfile import ConfigFileProcessor
from wesp.click_overloaded import CustomGroup
from wesp.click_overloaded import OnlyRequiredIf
from wesp.helper import *
from wesp.click_overloaded import raise_critical_error



def get_snmp_value (ctx, param, value):
    print ("Test func: " +  str(value))
    print("OID for Param: " + getattr(Oids, param.name))
    print(ctx.obj)

# TODO Handle FQDN
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
    # Otherwise raise an error
    if check_ip_address(value) or check_mac_address(value):
            ctx.obj[param.name] = value
    else:
        raise click.BadParameter(
            "Bad Parameter: `%s` is not a valid Mac Address" % (
                value,))




def add_value_to_context(ctx, param, value):
    print(param.name, value)

    ctx.obj[param.name] = value


def number_func (ctx, param, value):
    print ("Num func: " + str(value))
    print(ctx.obj)
    # ctx.invoke(cli)

def set_snmp_version(ctx, param, value):

    ctx.obj[param.name] = value
    print (param.name, value)





@click.group(chain=True, cls=CustomGroup, invoke_without_command=True)
@click.option('--num', '-n', 'number', help='Number of greetings.', callback=get_snmp_value)
#
@click.option('--WLC', '-W', 'wlc_address', required=True, callback=check_wlc_address,
              help = 'IP or FQDN address of WLC')
#
@click.option('--CLI', '-C', 'client_address', required=True, callback=check_client_address,
              help='IP or MAC address of Client')
#
@click.option('--version', '-v', 'snmp_version', required=True, callback=set_snmp_version,
              type=click.Choice(['2c', '3']), is_eager=True, default="2c",
              help='SNMP version, can either be 2c or 3')
#
@click.option('--community', '-c', 'snmp_community', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, only_required_if_version="2c",
              help='SNMP v2c Community of WLC')
#
@click.option('--user', '-u', 'snmp_user', required=True, callback=add_value_to_context,
              cls=OnlyRequiredIf, only_required_if_version="3",
              help='SNMP v3 User of WLC')




@click.pass_context
def cli_parser(ctx, number, wlc_address, client_address, snmp_community, snmp_version, snmp_user):
    """
    Additional USAGE: WLC_AD CLI OPTIONS
    This tool ist awesome:

        WLC_..."""
    print "Debug"




@cli_parser.command()
@click.pass_context
def sync(ctx):
    click.echo('Sync run')


@cli_parser.command()
@click.option('--count', '-c', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)

@cli_parser.resultcallback()
def process_result(result, **kwargs):
    click.echo('All parameters parsed')


@cli_parser.command()
@click.option("-d", "--db_name", "name", type=str, default="WESP", help="Name of DB")
@click.pass_context
def read_db_name(ctx, name):

    print (name)

# TODO add real Default Path
# TODO Add real Help Text

@cli_parser.command()
@click.option('-f','--file', 'file_path', default="../../wesp_config.cfg", type=click.Path(exists=True), help="Path to Config File")
@click.pass_context
def load_config(ctx, file_path):

    """Will load configfile. For more information see load_config --help.

    """

    # add path to Config File Processor
    ConfigFileProcessor.config_files = [file_path]
