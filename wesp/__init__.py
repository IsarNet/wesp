from easysnmp import Session
from wesp.snmp import Snmp
from wesp.oids import Oids
from wesp.configfile import *
from wesp.database import Database
import click


@click.command()
@click.option('--count', '-c', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)

# -- COMMAND:
CONTEXT_SETTINGS = dict(default_map=ConfigFileProcessor.read_config())

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-nu", "--number", "numbers", type=int, multiple=True)
@click.pass_context
def command_with_config(ctx, numbers):
    # -- ACCESS ADDITIONAL DATA FROM CONFIG FILES: Using ctx.default_map
    for person_data_key in ctx.default_map.keys():
        print(person_data_key)

    print (ctx.default_map['numbers'])
    print (numbers)




if __name__ == '__main__':

    #session = Session(hostname='192.168.1.240', community='MWb2JVBn', version=2)
   # Snmp(session)
    #Snmp.print_walk('.1.3.6.1.4.1.9.9.273.1.1.3')
    #print(Snmp.get_by_mac_address('.1.3.6.1.4.1.14179.2.1.6.1.1.', 'f4:f9:51:4e:63:a3'))

    #print(Oids.snr)
    #hello()
    #command_with_config()

    config = {
        'user': 'root',
        'password': 'root',
        'host': '127.0.0.1',
        'port': '8889',
        'database': 'WESP'
    }

    test_data = {
        'WLC_IPv4': '1234',
        'WLC_Mac': 'aa:bb'
    }

    Database.create_database_and_table_if_not_existing(config)
    Database.insert_data_set(config,test_data)


