import mysql.connector
from mysql.connector import errorcode


class Database:

    databaseCreateStatement = "CREATE DATABASE IF NOT EXISTS $$DATABASE$$;"

    tableCreateStatement = """CREATE TABLE IF NOT EXISTS WESP.data (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `WLC_IPv4` varchar(15) NOT NULL DEFAULT '',
      `WLC_Mac` varchar(17) NOT NULL DEFAULT '',
      `Client_IP` varchar(15) NOT NULL DEFAULT '',
      `Client_Mac` varchar(17) NOT NULL DEFAULT '',
      `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `RSSI` double DEFAULT NULL,
      `SNR` double DEFAULT NULL,
      `Data_Rate` double DEFAULT NULL,
      `Clean_Air_Average` double DEFAULT NULL,
      `RX_Packages` int(11) DEFAULT NULL,
      `TX_Packages` int(11) DEFAULT NULL,
      `Retries` int(11) DEFAULT NULL,
      `Ping` double DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    insertStatement = """INSERT INTO `data` (`WLC_IPv4`, `WLC_Mac`)
       VALUES
       (%(WLC_IPv4)s, %(WLC_Mac)s);""";

    table_name = ""
    db_name = ""
    global_config = None

    def __init__(self):
        pass

    # will initialize the database and complete the SQL Statement with the given names
    @staticmethod
    def init_database(table_name, db_name, config):
        Database.table_name = table_name
        Database.db_name = db_name

        # add given names to SQL statements
        Database.databaseCreateStatement = Database.databaseCreateStatement.replace('$$DATABASE$$', db_name)
        Database.tableCreateStatement = Database.databaseCreateStatement.replace('$$DATABASE$$', db_name)

        Database.tableCreateStatement = Database.databaseCreateStatement.replace('$$TABLE$$', table_name)
        Database.insertStatement = Database.databaseCreateStatement.replace('$$TABLE$$', table_name)

        Database.global_config = config

    # Will check the existence of the database and the Table with the names specified in the init_database function.
    # If they do not exist they will be created
    # Therefore a connection to the DB Information_Schema is performed.
    @staticmethod
    def create_database_and_table_if_not_existing(config=global_config):

        # copy dict to prevent changes in original config
        config_information_schema = dict(config)

        # change to Information Schema DB in case WESP does not exist
        config_information_schema['database'] = "INFORMATION_SCHEMA"

        cnx = cur = None
        try:
            cnx = mysql.connector.connect(**config_information_schema)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Something is wrong with your user name or password')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist. Check your MySQL installation.")
            else:
                print(err)
        else:
            cur = cnx.cursor()
            # Create database, if not existing
            cur.execute(Database.databaseCreateStatement)

            # Create table if not existing
            cur.execute(Database.tableCreateStatement)
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.close()


    @staticmethod
    def insert_data_set(data_set, config=global_config):

        cnx = cur = None
        try:
            cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Something is wrong with your user name or password')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist. Should not have happened.")
            else:
                print(err)
        else:
            cur = cnx.cursor()
            # Insert new data set
            cur.execute(Database.insertStatement, data_set)

            # Commit data to the database
            cnx.commit()
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.close()