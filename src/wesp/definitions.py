# TODO add tested version of WLC


# Basic Parameter with fundamental information about it
class Parameter:
    """
    Para aweseome
    """
    """human readable name, which will be used for the CLI output and the row name in the DB"""
    name = ""
    # OID at which parameter can be found, in case this parameter needs the mac address to work
    # don't enter it here. The mac address will be added in the parser, based on which callback
    # is used for this parameter
    oid = ""
    # DB Data Type which should be used for this parameter.
    # For string use varchar(255) with the length of the string in the brackets
    # For real numbers use int(11) with the length of the int in the brackets
    #   For real non negative numbers use int(11) unsigned
    # For rational numbers use double, no length needed. Be aware of the rounding problems in comparision
    # e.g. https://stackoverflow.com/questions/2567434/mysql-floating-point-comparison-issues
    db_data_type = ""

    def __init__(self, name, oid, db_data_type):
        self.name = name
        self.oid = oid
        self.db_data_type = db_data_type


# class which contains all Parameters, which can be requested by the user or
# are necessary for the program
# Ensure that the name of the attribute (e.g. channel) is the same as the name
# of the click option specified in the cli_parser. Note Lower and Uppercase

class AllParameter():
    """
    Aweseome description.
    """

    def __init__(self):
        pass

    #
    # Internal usage only
    #
    client_ip_address = Parameter("Client IP Address",
                                  "1.3.6.1.4.1.9.9.599.1.3.1.1.10",
                                  None)
    ap_mac_address = Parameter("AP Mac Address",
                               "1.3.6.1.4.1.9.9.599.1.3.1.1.39",
                               None)

    #
    # Callable optional Parameters
    #
    channel = Parameter("Channel",
                        "1.3.6.1.4.1.9.9.599.1.3.1.1.35",
                        'int(11)')
    #
    retries = Parameter("Retries",
                        "1.3.6.1.4.1.9.9.599.1.4.1.1.1",
                        'int(11)')
    # use with mac address of AP not Client
    ap_name = Parameter("AP Name",
                        "1.3.6.1.4.1.9.9.513.4.1.1.1.1.1",
                        'varchar(255)')
    #
    rx_packages = Parameter("RX Packages",
                            "1.3.6.1.4.1.9.9.599.1.4.1.1.27",
                            'int(11)')
    #
    tx_packages = Parameter("TX Packages",
                            "1.3.6.1.4.1.9.9.599.1.4.1.1.25",
                            'int(11)')
    #
    ping = Parameter("Ping (ms)",
                            None,
                            'double')

    #
    # Default Parameters
    #
    rssi_off = Parameter("RSSI",
                         "1.3.6.1.4.1.14179.2.1.6.1.1",
                         'double')
    #
    snr_off = Parameter("SNR",
                        "1.3.6.1.4.1.14179.2.1.6.1.26",
                        'double')
    #
    data_rate_off = Parameter("Client Data Rate",
                              "1.3.6.1.4.1.9.9.599.1.3.1.1.18",
                              'double')

    @staticmethod
    def get_all_parameter():
        """

        :rtype: list
        :return: a list of all parameters, which are defined in this class
        """
        list_of_all_parameter = []

        # loop through all fields of class AllParameter
        # and add all fields of type Parameter to the list
        for field in vars(AllParameter):

            if isinstance(getattr(AllParameter, field), Parameter):
                list_of_all_parameter.append(getattr(AllParameter, field))

        return list_of_all_parameter
