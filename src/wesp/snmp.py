from easysnmp import Session


class Snmp():

    session = None

    def __init__(self, session, *args, **kwargs ):
        if not isinstance(session, Session):
            raise TypeError("session must be of type easysnmp.Session")
        Snmp.session = session
        print "created"

    @staticmethod
    def get_session():
        return Snmp.session

    @staticmethod
    def walk(oid):
        return Snmp.session.walk(oid)

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
