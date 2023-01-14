import logging

class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return True# record.levelname != "debug"