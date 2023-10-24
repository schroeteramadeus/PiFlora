from abc import ABC, abstractmethod

class SQLDatabaseConnection:

    @abstractmethod
    def Execute(self, command : str, params : tuple) -> list[list]:
        pass
    
    @abstractmethod
    def _disconnect(self) -> None:
        pass

    def __del__(self) -> None:
        try:
            self._disconnect()
        except:
            #ignore errors
            pass