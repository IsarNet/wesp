"""
This module contains helper functions for this program.
For further details look at the description of the corresponding function.
"""

from IPy import IP
from easysnmp import EasySNMPNoSuchInstanceError, EasySNMPNoSuchObjectError
import re
from click import UsageError
import types
from wesp.definitions import AllParameter

#
# Check or Compare functions
#


def check_ip_address(address):
    """
    This function ensures that the given address is a valid IP address.
    It will also complete addresses, e.g. 192.168.1 will become 192.168.1.0

    :param address: IP address to check
    :rtype: bool
    :return: True if IP is correct, False if not

    """

    try:
        ip = (IP(address))

    except:
        return None

    return ip.strNormal()


def check_mac_address(address):
    """
    This function will check if the given address is a valid hex MAC address (e.g. aa:bb:cc:dd:ee:ff).

    :param address: MAC address to check
    :rtype: bool
    :return: True if address is a correct, False if not.

    """

    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower())


def compare_ips(ip_a, ip_b):
    """
    This function will compare if two IPs are the same or not.

    :param ip_a: IP address A to compare
    :param ip_b: IP address B to compare
    :rtype: bool
    :return: True if IPs are the same, false if not

    """

    return IP(ip_a) == IP(ip_b)


def validate_snmp_type(response, oid):
    """
    This function will validate that the response from the WLC is valid.
    If not it will raise an exception.

    :param response: SNMP variable
    :raises: EasySNMPNoSuchInstanceError, EasySNMPNoSuchObjectError
    :return: True if everything is fine, exception if not
    """

    if response.snmp_type == "NOSUCHINSTANCE":

        # Check if OID was the client_ip OID
        if AllParameter.client_ip.oid in oid:
            # raise with hint, if search was for IP
            raise UsageError(
                "No IP address found for given MAC address. Is device connected?")

        else:
            parameter = AllParameter.get_parameter_by_oid(oid)

            if parameter is not None:
                # raise Error with name of parameter, handling is done in calling function
                raise EasySNMPNoSuchInstanceError(parameter.name)

            else:
                # raise Error without name of parameter, handling is done in calling function
                raise EasySNMPNoSuchInstanceError("No Parameter with OID found, maybe Ping or Mac Address?")

    if response.snmp_type == "NOSUCHOBJECT":
        parameter = AllParameter.get_parameter_by_oid(oid)

        if parameter is not None:
            # raise Error with name of parameter, handling is done in calling function
            raise EasySNMPNoSuchObjectError(parameter.name)

        else:
            # raise Error without name of parameter, handling is done in calling function
            raise EasySNMPNoSuchObjectError("No Parameter with OID found, maybe Ping or Mac Address?")

    # Everything okay? return true
    return True


#
# Convert functions
#

def mac_hex_to_dec(mac_address, separator):
    """
    This function will convert a hex MAC address into a decimal MAC address

    :param mac_address: MAC address in hex format (e.g. aa:bb:cc:dd:ee:ff)
    :param separator: the character which is used for the split
    :rtype: str
    :return: MAC address in decimal format

    """

    mac_array = mac_address.split(separator)
    for x in range(0, 6):
        mac_array[x] = str(int(mac_array[x], 16))
    return mac_array[0] + "." + mac_array[1] + "." + mac_array[2] + "." + mac_array[3] + "." + mac_array[4] + "." + mac_array[5]


def mac_dec_to_hex(mac_address):
    """
    This function will convert a decimal MAC address into a hex MAC address

    :param mac_address: MAC address in decimal format (e.g. 170.187.204.221.238.255)
    :rtype: str
    :return: MAC address in hex format

    """

    # if string split first
    if isinstance(mac_address, types.StringTypes):
        mac_address = mac_address.split('.')

    i = 0
    ma = []
    for x in range(0, 6):
        maca = mac_address[i]
        if len(maca) == 1:
            a = hex(int(maca)).replace("x", "")
        else:
            a = hex(int(maca))[2:]
        ma.append(a)
        i = i + 1
    return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]


def extract_mac_from_oid(oid):
    """
    This function will extract the MAC Address from the given OID and return it in Hex format.

    :param oid: OID which contains the decimal MAC address
    :rtype: str
    :return: Hex MAC address of device which was represented in given OID

    """

    # split at dot and return the last six items, which are the mac address in decimal
    oid_array = oid.split('.')[-6:]
    return mac_dec_to_hex(oid_array)


def decompress_nested_dict(nested_dict):
    """
    This function will decompress all sub dicts in the given nested dict
    and return only a single non nested dict.

    :param nested_dict: nested dict to decompress
    :rtype: dict
    :return: non nested dict based on the given nested dict

    """

    normal_dict = {}

    for key, value in nested_dict.items():

        # if item is a dict, add it
        if isinstance(value, dict):
            # add sub dict
            normal_dict.update(value)
        else:
            # add value
            normal_dict[key] = value

    # return non nested dict
    return normal_dict


def print_session_info(session):
    """
    Will print the info's of the current SNMP session to the CLI

    :param: session: current SNMP session
    :return: Nothing, Output will go directly to the CLI

    """

    print ("SNMP Session Info")
    for attr in dir(session):
        if not attr.startswith('__') and not callable(getattr(session,attr)):
            print("    " + str(attr) + ": " + str(getattr(session, attr)))


def get_option_with_name(self, ctx, name):
    """
    Will search all Click options and return the option with the given name
    or *None* if none was found

    :param: self: reference to Click group or command
    :param: ctx: current context
    :param: name: name of the option
    :rtype: click.core.Option
    :return: option with the name or None if no match exists

    """

    for option in self.get_params(ctx):
        if option.name == name:
            return option

    return None


def replace_last_occurrence(str, old, new):
    """
    Will replace the last occurrence of *old* with *new* in the given string *str*.

    :param: str: string to work on
    :param: old: character to replace
    :param: new: character to replace with
    :rtype: str
    :return: the given string with the last occurrence of *old* replaced by *new*

    """

    k = str.rfind(old)
    return str[:k] + new + str[k + 1:]


def generate_cli_output(client_data, ctx, time):
    """
    Will generate the CLI output based on the given *client_data*. It also includes the current time
    and the MAC address of the client. It always has the following form:

    YYYY-mm-dd HH:MM:SS [aa:bb:cc:dd:ee:ff] [[No] Reply from 192.168.123.123 (XX ms)] {other parameters}

    :param: client_data: dict of requested client data
    :param: ctx: current context
    :rtype: str
    :return: string representation of all requested data

    """

    # Add time and mac address to output
    # as well as ping, if ping was performed
    output = str(time.strftime("%Y-%m-%d %H:%M:%S")) \
             + " [" + str(ctx.obj['client_mac']) + "] " \
             + ping_to_str(client_data, ctx) + " { "

    # For all values in client_data which are not none, add their human readable name
    # and their values to the string and return it
    for key, value in client_data.items():

        if value is not None and key is not "ping":
            output += str(getattr(AllParameter, key).name) + "=" + str(value) + "; "

    return output + "}"


def ping_to_str(client_data, ctx):
    """
    This function checks if a ping has been made and will create a string
    based on the result.
    It will look like this *"Reply from 192.0.2.1 (12 ms)"* or *"No Reply from 192.0.2.1"*

    :rtype: str
    :param: client_data: dict of requested client data
    :return: string representation of the ping result

    """

    # Check if ping was performed
    if 'ping' not in client_data:
        return ""

    # Check if ping was successful
    if client_data['ping'] is False:
        return "No Reply from " + str(ctx.obj['client_ip'])
    else:
        return "Reply from " + str(ctx.obj['client_ip']) + " (" + str(client_data['ping']) + " ms)"


#
# Database related functions
#


def generate_parameter_create_statement():
    """
    This function will create the table create statement based on the represented parameters in :class:`AllParameter`.
    The statement will have the following form:

    *`Retries` int(11) DEFAULT NULL,`RSSI` double DEFAULT NULL,`Channel` int(11) DEFAULT NULL, [...]*

    Note that id, timestamp, front and end part of the statement will be added by the database init function.

    :rtype: str
    :return: SQL create statement for known parameters

    """
    parameter_statement = ""

    # for all parameter which have a data type add them to the create statement
    # with a Default Value of NULL
    for parameter in AllParameter.get_all_parameter():
        if parameter.db_data_type is not None:
            parameter_statement += "`" + str(parameter.name) + "` " +\
                                   str(parameter.db_data_type) + " DEFAULT NULL,"

    return parameter_statement


def generate_parameter_insert_statement(client_data):
    """
    This function will create the insert statement based on the represented parameters in *client_data*.
    The statement will have the following form:

    *INSERT INTO TableName (`Retries`, `Channel` ) VALUES (%(retries)s, %(channel)s );*

    The front part (up to *TableName*) and the final semicolon will be added by the database init function.

    :param client_data: dict of requested client data
    :rtype: str
    :return: SQL insert statement for known parameters

    """

    parameter_names = ""
    parameter_values = ""

    # Temporary add client_ip, client_mac and timestamp (which should not be represented in client_data
    # to prevent output to CLI)
    client_data = client_data.copy()
    client_data.update({'client_ip': None, 'client_mac': None, 'timestamp': None})

    # for all entries in the given client_data set, which are represented in the class AllParameter
    for entry in client_data:

        if hasattr(AllParameter, entry):
            parameter = getattr(AllParameter, entry)

            # Add the human readable name to the list parameter_names
            parameter_names += "`" + str(parameter.name) + "`, "

            # Add the name of the value of that parameter to the list parameter_values.
            #  The "%()s" allows the later replacement with the actual value
            parameter_values += "%(" + str(entry) + ")s, "

    # Remove the last ',' to prevent error
    parameter_names = replace_last_occurrence(parameter_names, ',', '')
    parameter_values = replace_last_occurrence(parameter_values, ',', '')

    # return statement with surrounding brackets.
    return '(' + parameter_names + ') VALUES ' + '(' + parameter_values + ')'


def generate_db_conf_from_context (ctx):
    """
    This function will create the config dict for the database
    from the context object

    :param: ctx: current context
    :rtype: dict
    :return: database config as dict based on the current context

    """

    return {
        'user': ctx.obj['db_user'],
        'password': ctx.obj['db_pass'],
        'host': ctx.obj['db_address'],
        'port': ctx.obj['db_port'],
        'database': ctx.obj['db_name'],
    }