from easysnmp import Session, EasySNMPConnectionError
from wesp.definitions import *
from wesp.helper import *
import click


# TODO Add Comments
# TODO Add error handling if mac address is not avaliable
class Snmp:
    """
    This class handles all interactions via SNMP with the WLC. It provided the basics function to get,
    walk or trap with SNMP.
    The SNMP session will be initialized in the init function.
    All functions have been made static to allow easy use without a reference to specific session.
    """

    # Internal session reference
    session = None

    def __init__(self, ctx):
        """
        This will initialize the SNMP session based on the information stored in the context object.
        The context object is populated as the parameter from the user are parsed.

        :param ctx: current Context, which contains snmp information

        """

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

        #print_session_info(session)

    @staticmethod
    def get_session():
        """
        :return: reference to current snmp session

        """
        return Snmp.session

    @staticmethod
    def is_ready():
        """
        :rtype: bool
        :return: True if session is ready, False if not

        """
        return Snmp.session is not None

    @staticmethod
    def walk(oid):
        """
        will walk the given OID

        :param oid: OID to walk
        :rtype: list or None
        :return: a list of SNMPVariable objects containing the values that were retrieved via SNMP

        """
        return Snmp.session.walk(oid)

    @staticmethod
    def get(oid):
        """
        will get the information stored at the given OID

        :param oid: OID to get from
        :rtype: SNMPVariable
        :return: an SNMPVariable object containing the value that was retrieved

        """
        return Snmp.session.get(oid).value

    @staticmethod
    def get_mac_from_ip(ip):
        """
        Will search for the associated Mac address to the given IP

        :param ip: IP address to get Mac address for
        :rtype: str or None
        :return: Mac address of client or None if no match was found

        """

        all_items = Snmp.session.walk(AllParameter.client_ip_address.oid)

        for item in all_items:

            # If IPs match extract mac address and return
            if compare_ips(ip, item.value):
                return extract_mac_from_oid(item.oid)

        # return None, if nothing was found
        return None

    @staticmethod
    def get_by_mac_address(oid, mac_address, separator=':'):
        """
        will return in the information which is stored at the given OID and
        is specific by the given Mac Address.
        It will append the Mac Address in decimal format to the given OID and
        get this.

        :param oid: Base OID to get for
        :param mac_address: Mac Address of client
        :param separator: optional separator to split the mac address. Default ':'
        :return: value stored at this OID. Type depends on value.

        """
        # convert mac from hex to dec
        mac_int = mac_hex_to_dec(mac_address, separator)
        # add connecting dot, if not existing between end of oid and mac address
        oid = oid + mac_int if (oid[-1] == '.') else oid + '.' + mac_int

        response = Snmp.session.get(oid)

        # if type is octet string remove surrounding quotation marks
        if response.snmp_type == 'OCTETSTR':

            # remove quotation marks
            return response.value.replace('"', '')

        return response.value

    @staticmethod
    def print_walk(oid):
        """

        :param oid: OID to walk
        :return: Nothing, result will be outputted directly to the CLI

        """
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
