from easysnmp import Session
from wesp.oids import Oids
from wesp.helper import *

class Snmp():

    session = None

    def __init__(self, session, *args, **kwargs ):
        if not isinstance(session, Session):
            raise TypeError("Session must be of type easysnmp.Session. Unknown error at init of SNMP session")
       # TODO Uncomment
       # Snmp.session = session
        Snmp.session = ""
        print ("SNMP Session created", session.hostname, session.version, session.community)



    @staticmethod
    def get_session():
        return Snmp.session

    @staticmethod
    def is_ready():
        return Snmp.session is not None

    @staticmethod
    def walk(oid):
        return Snmp.session.walk(oid)

    @staticmethod
    def get(oid):
        return Snmp.session.get(oid).value

    @staticmethod
    def get_mac_from_ip(ip):
        all_items = Snmp.session.walk(Oids.client_ip_address)

        for item in all_items:

            # If IPs match extract mac address and return
            if compare_ips(ip, item.value):
                return extract_mac_from_oid(item.oid)

        # return None, if nothing was found
        return None

    @staticmethod
    def get_by_mac_address(oid, mac_address):
        # convert mac from hex to dec
        mac_int = mac_hex_to_dec(mac_address, ':')
        # add connecting dot, if not existing between end of oid and mac address
        oid = oid + mac_int if (oid[-1] == '.') else oid + '.' + mac_int
        return Snmp.session.get(oid).value


    @staticmethod
    def print_walk(oid):
        system_items = Snmp.session.walk(oid)

        # Each returned item can be used normally as its related type (str or int)
        # but also has several extended attributes with SNMP-specific information
        for item in system_items:
            print 'test:{oid}.{oid_index} {snmp_type} = {value}'.format(
                oid=item.oid,
                oid_index=item.oid_index,
                snmp_type=item.snmp_type,
                value=item.value
        )

        if (len(system_items) == 0):
            print("No items found for OID " + oid)

