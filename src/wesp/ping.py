from multiping import *



def ping_adress(address):
    addrs = [address]

    # Ping the addresses up to 4 times (initial ping + 3 retries), over the
    # course of 2 seconds. This means that for those addresses that do not
    # respond another ping will be sent every 0.5 seconds.
    responses, no_responses = multi_ping(addrs, timeout=2, retry=3)

    if (len(no_responses) > 0):
        return False
    else:
        return responses[address]

print(ping_adress("192.168.122.240"))