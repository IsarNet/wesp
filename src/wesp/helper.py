from IPy import IP
import re
import types
from easysnmp import Session

def check_ip_address(address):

    try:
        IP(address)

    except:
        return False

    return True

def check_mac_address(address):
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower())

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


# This function will compare if two IPs are the same or not
def compare_ips(ip_a, ip_b):
    return IP(ip_a) == IP(ip_b)


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

def print_session_info(session):
    print ("    SNMP Session Infos")
    for attr in dir(session):
        if not attr.startswith('__') and not callable(getattr(session,attr)):
            print("    " + str(attr) + ": " + str(getattr(session, attr)))
