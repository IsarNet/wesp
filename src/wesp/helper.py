from IPy import IP
import re

def check_ip_address(address):

    try:
        IP(address)

    except:
        return False

    return True

def check_mac_address(address):
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower())
