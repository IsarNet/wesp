# Basic Parameter with fundamental information about it
class Parameter:
    name = ""
    oid = ""
    db_data_type = ""

    def __init__(self, name, oid, db_data_type):
        self.name = name
        self.oid = oid
        self.db_data_type = db_data_type


# class which contains all OIDs for the attributes.
# tested with XXX
class AllParameter():
    def __init__(self):
        pass

    #
    client_ip_address = Parameter("Client IP Address",
                                  "1.3.6.1.4.1.9.9.599.1.3.1.1.10",
                                  None)
    #
    channel = Parameter("Channel",
                        "1.3.6.1.4.1.9.9.599.1.3.1.1.35",
                        'int(11)')
    #
    rssi = Parameter("RSSI",
                     "1.3.6.1.4.1.14179.2.2.18.1.2",
                     'double')
    #
    retries = Parameter("Retries",
                        "1.3.6.1.4.1.9.9.599.1.4.1.1.1",
                        'int(11)')
