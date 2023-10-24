import psycopg2
from ..SQLDatabaseConnection import SQLDatabaseConnection

class PostgresSQLDatabaseConnection(SQLDatabaseConnection):
    

    def __init__(self, connection : psycopg2.extensions.connection) -> None:
        self.__connection : psycopg2.extensions.connection = connection
        self.__connection.autocommit = False
        #0 -> autocommit
        #1 -> read committed
        #2 -> serialized (but not officially supported by pg)
        #3 -> serialized
        self.__connection.set_isolation_level(3)
        self.__cursor = self.__connection.cursor()

    def Execute(self, command : str, params : tuple) -> list[tuple]:
        self.__cursor.execute(command, params)
        return self.__cursor.fetchall()

    def _disconnect(self) -> None:
        self.__cursor.close()
        self.__connection.close()