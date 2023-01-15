import logging

class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return "btlewrap" not in record.name and "miflora" not in record.name