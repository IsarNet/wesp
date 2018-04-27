from IPy import IP
import re
import types
from wesp.definitions import AllParameter

#
# Check or Compare functions
#

# This functions ensure that the given address is a valid IP Address.
# It will also complete address, e.g. 192.168.1 will become 192.168.1.0
def check_ip_address(address):

    try:
        ip = (IP(address))

    except:
        return None

    return ip.strNormal()


# This function will check if the given address is a valid hex mac address
def check_mac_address(address):
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower())


# This function will compare if two IPs are the same or not
def compare_ips(ip_a, ip_b):
    return IP(ip_a) == IP(ip_b)


#
# Convert functions
#

# This function will convert hex mac address into a decimal mac address
def mac_hex_to_dec(mac_address, seperator):
    mac_array = mac_address.split(seperator)
    for x in range(0, 6):
        mac_array[x] = str(int(mac_array[x], 16))
    return mac_array[0] + "." + mac_array[1] + "." + mac_array[2] + "." + mac_array[3] + "." + mac_array[4] + "." + mac_array[5]


# This function will convert decimal mac address into a hex mac address
def mac_dec_to_hex(mac_address):

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


# This function will extract the Mac Address from the given OID and return it in Hex Format
def extract_mac_from_oid(oid):
    # split at dot and return the last six items, which are the mac address in decimal
    oid_array = oid.split('.')[-6:]
    return mac_dec_to_hex(oid_array)


# This function will decompress all sub dict in the given nested dict
# and return only single non nested dict
def decompress_nested_dict(nested_dict):

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


# This function will create the config dict for the database
# from the context object
def generate_db_conf_from_context (ctx):
    return {
        'user': ctx.obj['db_user'],
        'password': ctx.obj['db_pass'],
        'host': ctx.obj['db_address'],
        'port': ctx.obj['db_port'],
        'database': ctx.obj['db_name'],
    }


# will print the info's of the current session to Std out
def print_session_info(session):
    print ("    SNMP Session Infos")
    for attr in dir(session):
        if not attr.startswith('__') and not callable(getattr(session,attr)):
            print("    " + str(attr) + ": " + str(getattr(session, attr)))


# will search all click options and return the option with the given name
# or none if non was found
def get_option_with_name(self, ctx, name):

    for option in self.get_params(ctx):
        if option.name == name:
            return option

    return None


# will replace the last occurrence of old with new in the given string str
def replace_last_occurrence(str, old, new):
    k = str.rfind(old)
    return str[:k] + new + str[k + 1:]


# will generate the CLI output based on the given client_data
def generate_cli_output(client_data):

    output = ""

    for key, value in client_data.items():
        output += str(getattr(AllParameter, key).name) + ": " + str(value) + ", "

    return output

#
# Database related functions
#


# This function will create the table create statement based on the represented parameters in AllParameter.
# The statement will have the following form:
# `Retries` int(11) DEFAULT NULL,`RSSI` double DEFAULT NULL,`Channel` int(11) DEFAULT NULL,
# Note that id, timestamp and front and end part of the statement will be add by the database init function
def generate_parameter_create_statement():
    parameter_statement = ""

    # for all parameter which have a data type add them to the create statement
    # with a Default Value of NULL
    for parameter in AllParameter.get_all_parameter():
        if parameter.db_data_type is not None:
            parameter_statement += "`" + str(parameter.name) + "` " +\
                                   str(parameter.db_data_type) + " DEFAULT NULL,"

    return parameter_statement


# This function will create the insert statement based on the represented parameters in client_data.
# The statement will have the following form:
# INSERT INTO TableName (`Retries`, `Channel` ) VALUES (%(retries)s, %(channel)s );
# The front part (up to the TableName) and the final semicolon will be add by the database init function
def generate_parameter_insert_statement(client_data):

    parameter_names = ""
    parameter_values = ""

    # for all entries in the given client_data set, which are represented in the class AllParameter
    for entry in client_data:

        if hasattr(AllParameter, entry):
            parameter = getattr(AllParameter, entry)

            # Add the human readable name to the list parameter_names
            parameter_names += "`" + str(parameter.name) + "`, "

            # Add the name of the value of that parameter to the list parameter_values.
            #  The "%()s" allows the later replacment with the actual value
            parameter_values += "%(" + str(entry) + ")s, "

    # Remove the last ',' to prevent error
    parameter_names = replace_last_occurrence(parameter_names, ',', '')
    parameter_values = replace_last_occurrence(parameter_values, ',', '')

    # return statement with surrounding brackets.
    return '(' + parameter_names + ') VALUES ' + '(' + parameter_values + ')'

