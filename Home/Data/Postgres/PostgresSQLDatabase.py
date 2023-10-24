import psycopg2
from .PostgresSQLDatabaseConnection import PostgresSQLDatabaseConnection
from ..SQLDatabase import SQLDatabase
from ..SQLDatabaseConnection import SQLDatabaseConnection

class PostgresSQLDatabase(SQLDatabase):
    def _connect(self, user : str, password : str) -> SQLDatabaseConnection:  
        return PostgresSQLDatabaseConnection(psycopg2.connect(
            host=self.Host,
            database=self.Name,
            user=user,
            password=password
        ))

database = PostgresSQLDatabase("test_db", "localhost")

connection = database.Connect("test_user", "test")

#conn.autocommit = False;
#0 -> autocommit
#1 -> read committed
#2 -> serialized (but not officially supported by pg)
#3 -> serialized
#conn.set_isolation_level(3)
#conn.tpc_begin(conn.xid)
#cursor = conn.cursor();

#cursor.execute("SELECT * FROM information_schema.tables WHERE table_catalog = %(database)s AND table_schema NOT IN ('information_schema', 'pg_catalog');", {'database': 'test_db'})
#conn.rollback()
#print(cursor.fetchall())

#conn.close()