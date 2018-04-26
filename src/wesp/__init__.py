from wesp.cli_parser import cli_parser





if __name__ == '__main__':

    #session = Session(hostname='192.168.1.240', community='MWb2JVBn', version=2)
   # Snmp(session)
    #Snmp.print_walk('.1.3.6.1.4.1.9.9.273.1.1.3')
    #print(Snmp.get_by_mac_address('.1.3.6.1.4.1.14179.2.1.6.1.1.', 'f4:f9:51:4e:63:a3'))

    #print(Oids.snr)
    #hello()
    #command_with_config()

    config = {
        'user': 'root',
        'password': 'root',
        'host': '127.0.0.1',
        'port': '8889',
        'database': 'WESP'
    }

    test_data = {
        'WLC_IPv4': '1234',
        'WLC_Mac': 'aa:bb'
    }

    # Database.create_database_and_table_if_not_existing(config)
    # Database.insert_data_set(config,test_data)

    cli_parser(obj={})
    #database()

