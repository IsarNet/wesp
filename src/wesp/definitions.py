"""
This module contains everything which can be changed by a user. It holds the OIDs for the Parameters,
as well as their name and database type. For more information see :class:`.Parameter`

In addition the class :class:`GlobalSettings` defines basic options like the help flags, the usage text
or the welcome string
\n\n
NOTE: Changes to name or db_data_type will only be reflected in the database, if the table is dropped
and recreated by this program
"""


# TODO add tested version of WLC


class Parameter:
    """
    Represents a basic Parameter with fundamental information about it.
    More information on the fields can be found below
    """

    name = ""
    """
    human readable name, which will be used for the CLI output and the row name in the DB
    """

    oid = ""
    """
    OID at which parameter can be found, in case this parameter needs the mac address to work
    don't enter it here. The mac address will be added in the parser, based on which callback
    is used for this parameter
    """

    db_data_type = ""
    """
    DB Data Type which should be used for this parameter.
    For string use varchar(255) with the length of the string in the brackets
    For real numbers use int(11) with a fixed maximum of 2147483647. Length in brackets is only for display 
    and will not effect this program
    For real non negative numbers use int(11) unsigned ot have a maximum of 4294967295
    For rational numbers use double, no length needed. Be aware of the rounding problems in comparision
    e.g. https://stackoverflow.com/questions/2567434/mysql-floating-point-comparison-issues
    \n
    NOTE: Changes here will only be reflected in the database, if the table is dropped and recreated by this program
    """

    def __init__(self, name, oid, db_data_type):
        """init function will set the variables"""
        self.name = name
        self.oid = oid
        self.db_data_type = db_data_type


class AllParameter:
    """
    Class that contains all Parameters, which can be requested by the user or
    are necessary for the program
    Ensure that the name of the attribute (e.g. channel) is the same as the name
    of the click option specified in the cli_parser. Note Lower and Uppercase
    """

    def __init__(self):
        """
        init is not needed. All fields are static
        """
        pass

    #
    # Internal usage only
    # !!!DO NOT CHANGE!!!
    #
    client_ip = Parameter("Client IP Address",
                          "1.3.6.1.4.1.9.9.599.1.3.1.1.10",
                          'varchar(15)')
    #
    client_mac = Parameter("Client Mac Address",
                           None,
                           'varchar(17)')
    #
    ap_mac_address = Parameter("AP Mac Address",
                               "1.3.6.1.4.1.9.9.599.1.3.1.1.39",
                               None)
    #
    timestamp = Parameter("Timestamp",
                               None,
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
    rx_packets = Parameter("RX Packets",
                            "1.3.6.1.4.1.9.9.599.1.4.1.1.27",
                            'int(11)')
    #
    tx_packets = Parameter("TX Packets",
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
                              "1.3.6.1.4.1.9.9.599.1.3.1.1.17",
                              'varchar(255)')

    @staticmethod
    def get_all_parameter():
        """
        Returns all parameters listed in this class

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

    @staticmethod
    def get_parameter_by_oid(oid):
        """
        Returns the parameter with the given oid or nothing if no existing

        :rtype: Parameter or None
        :return: parameter with the given oid or None if no existing
        """

        # loop through all fields of class AllParameter
        for field in vars(AllParameter):

            if isinstance(getattr(AllParameter, field), Parameter):
                candidate = getattr(AllParameter, field)

                # check parameter has a OID associated with it
                if candidate.oid is not None:
                    # OID matches, then return it
                    if candidate.oid in oid:
                        return candidate

        return None


class GlobalSettings:
    """
    This class holds global settings, which are not viable for the program flow.
    For Example one is able to change the Welcome text or the Usage String.
    """
    def __init__(self):
        """
        init is not needed. All fields are static
        """
        pass

    HELP_PARAMETERS = ['-h', '--help']
    """
    Name of help flags, will be set in the :meth:`wesp.click_overloaded.CustomGroup.parse_args` 
    or :meth:`wesp.click_overloaded.CommandAllowConfigFile.parse_args`
    """

    WELCOME_STRING = "Welcome to the wesp tool - Wireless Endpoint Statistics Program \n" \
                     "For help run wesp -h"
    """
    String which greets the user, if no parameters are given.
    Will be set in the :meth:`wesp.click_overloaded.CustomGroup.parse_args` 
    """

    PROGRAM_NAME = "wesp"
    """
    Name of the program, which appears as part of the Usage String.
    Will be set in the :meth:`wesp.click_overloaded.CustomGroup.format_usage` 
    """

    USAGE = "-W wlc_ip|wlc_fqdn -C client_ip|client_mac  [SNMP OPTIONS] [OTHER OPTIONS] " \
            "load_config [Options] print_to_db [Options]"
    """
    Usage String to help user understand the structure of the program. This string also
    appears at every error message. 
    
    Additional help on the usage is defined in the help text of the :class:`wesp.click_overloaded.CustomGroup` 
    
    Will be set in the :meth:`wesp.click_overloaded.CustomGroup.format_usage` 
    
    """
