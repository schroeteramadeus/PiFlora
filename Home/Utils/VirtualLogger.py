import logging
import re
import threading


class VirtualLogger(logging.Handler):

    def __init__(self, maximumRecords:int = 1000, level: int = 0) -> None:
        super().__init__(level)
        self.__maximumRecords = maximumRecords #type: int
        self.__records = [] #type: list[logging.LogRecord]
        self.__recordsLock = threading.Lock() #type : threading.Lock

    def emit(self, record):
        with self.__recordsLock:
            if len(self.__records) >= self.__maximumRecords:
                self.__records.pop()
            self.__records.append(record)

    def Fetch(self, minimumLevel: int = 0, filter:str = "") -> list[dict[str,str | int]]:
        logs = []
        expression = re.compile(filter)

        with self.__recordsLock:
            for record in self.__records:
                data = {}
                data["time"] = record.asctime
                data["message"] = record.message
                data["level"] = record.levelname
                data["logger"] = record.name
                data["file"] = record.filename
                data["line"] = record.lineno
                if record.levelno >= minimumLevel:
                    if expression.match(data["message"]) or expression.match(data["level"]) or expression.match(data["file"]):
                        logs.append(data)
        return logs

    @property
    def MaximumRecords(self, value):
        #type: (int) -> None
        self.__maximumRecords = value