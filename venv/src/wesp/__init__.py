from easysnmp import Session
from wesp.snmp import Snmp

if __name__ == '__main__':

    session = Session(hostname='192.168.178.240', community='MWb2JVBn', version=2)
    Snmp(session)
    Snmp.print_walk('.1.3.6.1.4.1.14179.2.1.6.1.1')

    #GitTest2
