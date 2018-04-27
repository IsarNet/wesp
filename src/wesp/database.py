import mysql.connector
from mysql.connector import errorcode
import click


class Database:

    databaseCreateStatement = "CREATE DATABASE IF NOT EXISTS $$DATABASE$$;"

    tableCreateStatement = """CREATE TABLE IF NOT EXISTS $$DATABASE$$.$$TABLE$$ (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      $$PARAMETER$$
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    insertStatement = """INSERT INTO $$TABLE$$ $$PARAMETER$$;""";

    table_name = ""
    db_name = ""
    global_config = None

    def __init__(self):
        pass

    # will initialize the database and complete the SQL Statements with the given names and sub-statements
    @staticmethod
    def init_database(ctx, config, parameter_create, parameter_insert):
        Database.table_name = ctx.obj['db_table']
        Database.db_name = ctx.obj['db_name']

        # add given names to SQL statements
        Database.databaseCreateStatement = Database.databaseCreateStatement.replace('$$DATABASE$$', Database.db_name)
        Database.tableCreateStatement = Database.tableCreateStatement.replace('$$DATABASE$$', Database.db_name)

        Database.tableCreateStatement = Database.tableCreateStatement.replace('$$TABLE$$', Database.table_name)
        Database.insertStatement = Database.insertStatement.replace('$$TABLE$$', Database.table_name)

        # add the parameters create statement into the tableCreateStatement
        Database.tableCreateStatement = Database.tableCreateStatement.replace('$$PARAMETER$$', parameter_create)

        # add the human readable as well as their programm name into the insert statement
        Database.insertStatement = Database.insertStatement.replace('$$PARAMETER$$', parameter_insert)

        # TODO Remove
        # print(Database.tableCreateStatement)

        # add the database config to the class
        Database.global_config = config

        Database.create_database_and_table_if_not_existing(config)

    # Will check the existence of the database and the Table with the names specified in the init_database function.
    # If they do not exist they will be created
    # Therefore a connection to the DB Information_Schema is performed.
    @staticmethod
    def create_database_and_table_if_not_existing(config):

        # copy dict to prevent changes in original config
        config_information_schema = dict(config)

        # change to Information Schema DB in case WESP does not exist
        config_information_schema['database'] = "INFORMATION_SCHEMA"

        cnx = cur = None
        try:
            cnx = mysql.connector.connect(**config_information_schema)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise click.UsageError(
                    "MySQL Error: Something is wrong with your user name or password'")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise click.UsageError(
                    "MySQL Error: Database INFORMATION_SCHEMA does not exist. Check your MySQL installation.'")
            else:
                raise click.UsageError(
                    "Unknown MySQL Error: `%s`" % (
                        err))
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
    def insert_data_set(data_set):

        cnx = cur = None
        try:
            cnx = mysql.connector.connect(**Database.global_config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise click.UsageError(
                    "MySQL Error: Something is wrong with your user name or password'")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise click.UsageError(
                    "MySQL Error: Database" + str(Database.db_name) + "does not exist. Check your MySQL installation.'")
            else:
                raise click.UsageError(
                    "Unknown MySQL Error: `%s`" % (
                        err))
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