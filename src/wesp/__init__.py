from easysnmp import Session
from wesp.snmp import Snmp
import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)



if __name__ == '__main__':

    session = Session(hostname='192.168.178.240', community='MWb2JVBn', version=2)
    Snmp(session)
    Snmp.print_walk('.1.3.6.1.4.1.14179.2.1.6.1.1')
    hello()


