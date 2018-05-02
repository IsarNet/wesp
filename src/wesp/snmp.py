from easysnmp import Session, EasySNMPConnectionError
from wesp.definitions import *
from wesp.helper import *
import click


# TODO Add Comments
# TODO Add error handling if mac address is not avaliable
class Snmp:

    # Internal session reference
    session = None

    def __init__(self, ctx):
        # Create v2c Session
        # use_sprint_value automatically converts values to non binary
        if ctx.obj['snmp_version'] == "2c":
            session = Session(hostname=ctx.obj['wlc_address'],
                              community=ctx.obj['snmp_community'],
                              version=2,
                              use_sprint_value=True)

        # Create v3 Session
        # Default settings:
        # security_level = auth_with_privacy
        # auth_protocol = SHA
        # privacy_protocol = AES
        # use_sprint_value automatically converts values to non binary
        if ctx.obj['snmp_version'] == "3":
            try:
                session = Session(hostname=ctx.obj['wlc_address'],
                                  security_level='auth_with_privacy',
                                  security_username=ctx.obj['snmp_user'],
                                  privacy_password=ctx.obj['snmp_encryption'],
                                  privacy_protocol='AES',
                                  auth_password=ctx.obj['snmp_password'],
                                  auth_protocol='SHA',
                                  version=3,
                                  use_sprint_value=True)
            except EasySNMPConnectionError, e:
                raise click.UsageError(
                    "SNMP Connection Error: `%s`" % (
                        e.message))

        # init Snmp with generated Session
        Snmp.session = session

        # Check if the Client Mac Address was given
        # or only the Client IP,
        # because Mac address is mandatory to find Cisco attributes
        if 'client_mac' not in ctx.obj:
            ctx.obj['client_mac'] = Snmp.get_mac_from_ip(ctx.obj['client_ip'])
            # TODO Remove
            print(ctx.obj['client_mac'])

        # Check if the Client IP Address was given
        # or only the Client Mac,
        # because IP address is mandatory to ping
        if 'client_ip' not in ctx.obj:
            ctx.obj['client_ip'] = Snmp.get_by_mac_address(AllParameter.client_ip_address.oid, ctx.obj['client_mac'])
            # TODO Remove
            print(ctx.obj['client_ip'])

        # print_session_info(session)

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
        all_items = Snmp.session.walk(AllParameter.client_ip_address.oid)

        for item in all_items:

            # If IPs match extract mac address and return
            if compare_ips(ip, item.value):
                return extract_mac_from_oid(item.oid)

        # return None, if nothing was found
        return None

    @staticmethod
    def get_by_mac_address(oid, mac_address, separator=':'):
        # convert mac from hex to dec
        mac_int = mac_hex_to_dec(mac_address, separator)
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
