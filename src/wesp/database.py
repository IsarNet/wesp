import mysql.connector
from mysql.connector import errorcode
from mysql.connector.errors import *
import click
from wesp.definitions import AllParameter


class Database:
    """
    Contains all functions related to the database. To ensure that only one database connection is used, everything
    in this class is static.

    The different raw statements are completed in the
    :meth:`init_database` using the data inside of :class:`wesp.definitions.AllParameter`.

    The function :meth:`_create_database_and_table_if_not_existing` will check if the database and the table exist,
    otherwise it will create it using the *databaseCreateStatement*.

    The function :meth:`_check_if_columns_exist`  will check if all columns exists and have the right data type.

    Data can be inserted using the function :meth:`insert_data_set`. This function expects the data to be in the
    format of the dict *CLIENT_DATA* inside the :mod:`cli_parser` module.
    """

    databaseCreateStatement = "CREATE DATABASE IF NOT EXISTS %%DATABASE%%;"
    """This statement will be used to create the database. It will only trigger if the database does 
    not exists. Note the name of the database will be inserted in the :meth:`init_database` function."""

    tableCreateStatement = """CREATE TABLE IF NOT EXISTS %%DATABASE%%.%%TABLE%% (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      %%PARAMETER%%
      PRIMARY KEY (`id`),
      KEY `ipIndex` (`%%IP_INDEX%%`),
      KEY `macIndex` (`%%MAC_INDEX%%`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    """This statement creates the table. It will only trigger if the database does 
    not exists. Note the name of the database and table, as well as all other fields (based on 
    registered parameters in :class:`wesp.definitions.AllParameter`) will be inserted in the :meth:`init_database` 
    function. The generation of that data is done in the
    :meth:`wesp.helper.generate_parameter_create_statement` function but has to be ran by the caller of 
    the :meth:`init_database` function."""

    insertStatement = """INSERT INTO %%TABLE%% %%PARAMETER%%;""";
    """This statement is used to insert data. The names and a list of parameters are
    inserted in the function :meth:`init_database`. The corresponding values are inserted 
    in the :meth:`insert_data_set` function.
    The generation of that substring is done in the 
    :meth:`wesp.helper.generate_parameter_insert_statement` function but has to be ran by the caller of 
    the :meth:`init_database` function."""

    column_total_check = """SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA like '%%DATABASE%%' 
    AND TABLE_NAME like '%%TABLE%%' AND COLUMN_NAME like '%%COLUMN%%' AND COLUMN_TYPE like '%%DATA_TYPE%%'"""
    """
    This statement is used to check if a column exists. Here the name and the data type is checked. 
    """

    column_only_name_check = """SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA like '%%DATABASE%%' 
        AND TABLE_NAME like '%%TABLE%%' AND COLUMN_NAME like '%%COLUMN%%'"""
    """
    This statement is used to check if a column exists. Here only the name is checked. 
    """

    create_new_column = "ALTER TABLE %%DATABASE%%.%%TABLE%% ADD COLUMN `%%COLUMN%%` %%DATA_TYPE%%; "
    """
    This statement will created a new column in a existing table
    """

    modify_column = "ALTER TABLE %%DATABASE%%.%%TABLE%% MODIFY COLUMN `%%COLUMN%%` %%DATA_TYPE%%; "
    """
    This statement will modify the data type of an column to match the one registered in this program
    """

    table_name = ""
    db_name = ""
    global_config = None
    ready = False

    def __init__(self):
        pass

    @staticmethod
    def init_database(ctx, config, parameter_create, parameter_insert):
        """
        Will initialize the database and complete the SQL Statements with the given names and sub-statements

        :param ctx: current Context
        :param config: config for database connection, can be generated using :meth:`wesp.helper.generate_db_conf_from_context`
        :param parameter_create: parameter part of create statement, can be generated using :meth:`wesp.helper.generate_parameter_create_statement`
        :param parameter_insert: parameter part of insert statement, can be generated using :meth:`wesp.helper.generate_parameter_insert_statement`

        """
        Database.table_name = ctx.obj['db_table']
        Database.db_name = ctx.obj['db_name']

        # add given names to SQL statements
        Database.databaseCreateStatement = Database.databaseCreateStatement.replace('%%DATABASE%%', Database.db_name)
        Database.tableCreateStatement = Database.tableCreateStatement.replace('%%DATABASE%%', Database.db_name)

        Database.tableCreateStatement = Database.tableCreateStatement.replace('%%TABLE%%', Database.table_name)
        Database.insertStatement = Database.insertStatement.replace('%%TABLE%%', Database.table_name)

        # add the parameters create statement into the tableCreateStatement
        Database.tableCreateStatement = Database.tableCreateStatement.replace('%%PARAMETER%%', parameter_create)

        # add the human readable as well as their program name into the insert statement
        Database.insertStatement = Database.insertStatement.replace('%%PARAMETER%%', parameter_insert)

        # add names for the indices
        Database.tableCreateStatement = Database.tableCreateStatement.replace('%%IP_INDEX%%',
                                                                              AllParameter.client_ip.name)
        Database.tableCreateStatement = Database.tableCreateStatement.replace('%%MAC_INDEX%%',
                                                                              AllParameter.client_mac.name)
        # add the database config to the class
        Database.global_config = config

        Database._create_database_and_table_if_not_existing(config)

        Database.ready = True

    @staticmethod
    def _create_database_and_table_if_not_existing(config):

        """
        Will check the existence of the database and table with the names specified in the :meth:`init_database`
        function. If they do not exist they will be created.
        Therefore a connection to the database *Information_Schema* is performed.

        :param config: config for database connection, can be generated by :meth:`wesp.helper.generate_db_conf_from_context`

        """
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
                    "Unknown MySQL Error at initial connection: `%s`" % (
                        err))
        else:
            cur = cnx.cursor(buffered=True)
            # Create database, if not existing
            cur.execute(Database.databaseCreateStatement)

            # Create table if not existing
            cur.execute(Database.tableCreateStatement)

            # Make sure all columns exist and have the right data type
            Database._check_if_columns_exist(cur)

            # Make sure data is committed to the database
            cnx.commit()
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.close()

    @staticmethod
    def _check_if_columns_exist(cur):
        """
        Will check if all columns exists and have the right data type. This makes sure that the database always reflects
        the definition of this program. A column is checked in two ways. First a name and a data type check is performed.
        Should this fail, it is checked if a column with the same name exists, if so the data type will be modified. If
        no column exists it will be created.

        :param cur: cursor from current DB connection

        """

        # add database and table name to SQL statements
        Database.column_only_name_check = Database.column_only_name_check.replace('%%DATABASE%%', Database.db_name).replace('%%TABLE%%', Database.table_name)
        Database.column_total_check = Database.column_total_check.replace('%%DATABASE%%', Database.db_name).replace('%%TABLE%%', Database.table_name)
        Database.create_new_column = Database.create_new_column.replace('%%DATABASE%%', Database.db_name).replace('%%TABLE%%', Database.table_name)
        Database.modify_column = Database.modify_column.replace('%%DATABASE%%', Database.db_name).replace('%%TABLE%%', Database.table_name)

        # for all parameter which have a data type check if the corresponding column exist
        for parameter in AllParameter.get_all_parameter():
            if parameter.db_data_type is not None:

                # check if column with right name and data type exists
                query = Database.column_total_check.replace('%%COLUMN%%', parameter.name).replace('%%DATA_TYPE%%', parameter.db_data_type)
                cur.execute(query)

                # rowcount of zero means no columns with this name and data type exists
                if cur.rowcount == 0:

                    # check if column only with right name exists, if so modify data type
                    query = Database.column_only_name_check.replace('%%COLUMN%%', parameter.name)
                    cur.execute(query)

                    # rowcount of zero means no columns with this name exists
                    # above zero means that a column has been found with the name
                    if cur.rowcount == 0:

                        # column has to be created
                        query = Database.create_new_column.replace('%%COLUMN%%', parameter.name).replace('%%DATA_TYPE%%', parameter.db_data_type)
                        cur.execute(query)

                    else:
                        # column has to be modified
                        query = Database.modify_column.replace('%%COLUMN%%', parameter.name).replace('%%DATA_TYPE%%', parameter.db_data_type)
                        cur.execute(query)

    @staticmethod
    def insert_data_set(data_set, ctx, time):
        """
        Will insert the given data into the database based on the config
        and statement from the :meth:`init_database` function.

        :param data_set: data set to be inserted, must contain the same fields names as defined in the *insertStatement*
        :param ctx: current context

        """

        # Temporary add client_ip, client_mac and timestamp(which should not be represented in client_data
        # to prevent output to CLI)
        # convert timestamp to a format that is understood by the DB
        data_set = data_set.copy()
        data_set.update({'client_ip': ctx.obj['client_ip'],
                         'client_mac': ctx.obj['client_mac'],
                         'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})

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
                    "Unknown MySQL Error at insert connection: `%s`" % (
                        err))
        else:
            cur = cnx.cursor()

            try:
                # Insert new data set
                cur.execute(Database.insertStatement, data_set)
            except ProgrammingError as ex:
                raise click.UsageError(
                    "SQL error: `%s` "
                    "\n(If new field has been added, drop the table or add it manually to the table)" % ex)

            except (Error, DatabaseError, DataError, IntegrityError, InterfaceError, InternalError,
                    MySQLFabricError, NotSupportedError, OperationalError, PoolError) as ex:
                raise click.UsageError(
                    "Unknown SQL error at insert: `%s` " % ex)

            # Commit data to the database
            cnx.commit()
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.close()

    @staticmethod
    def is_ready():
        """
        Will check, if the database connection is ready, which means that the config has been set and the raw
        statements have been initialized.

        :return: True if database has been initialized, otherwise False

        """
        return Database.ready

