from abc import ABC, abstractmethod
from .SQLDatabaseConnection import SQLDatabaseConnection

class SQLDatabase:

    def __init__(self, name : str, host : str) -> None:
        self._name : str = name
        self._host : str = host

    @abstractmethod
    def _connect(self, user : str, password : str) -> SQLDatabaseConnection:
        pass


    def Connect(self, user : str, password : str) -> SQLDatabaseConnection:
        #try:
        return self._connect(user, password)
        #except:
            #TODO handle
            #pass

    @property
    def Name(self) -> str:
        return self._name
    @property
    def Host(self) -> str:
        return self._host