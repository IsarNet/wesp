from easysnmp import Session


class Snmp():

    session = None

    def __init__(self, session, *args, **kwargs ):
        if not isinstance(session, Session):
            raise TypeError("session must be of type easysnmp.Session")
        Snmp.session = session
        print "created"

    @staticmethod
    def mac_hex_to_dec(mac_address, seperator):
        mac_array = mac_address.split(seperator)
        for x in range(0, 6):
            mac_array[x] = str(int(mac_array[x], 16))
        return mac_array[0] + "." + mac_array[1] + "." + mac_array[2] + "." + mac_array[3] + "." + mac_array[4] + "." + mac_array[5]

    @staticmethod
    def get_session():
        return Snmp.session

    @staticmethod
    def walk(oid):
        return Snmp.session.walk(oid)

    @staticmethod
    def get(oid):
        return Snmp.session.get(oid)

    @staticmethod
    def get_by_mac_address(oid,mac_address):
        mac_int = Snmp.mac_hex_to_dec(mac_address, ':')
        # add connecting dot, if not existing
        id = oid + mac_int if (oid[-1] == '.') else oid + '.' + mac_int
        return Snmp.session.get(id)

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

