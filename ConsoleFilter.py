import logging

#TODO if critical: send email
class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return "gpio" in record.name.lower() or "plantsensor" in record.name.lower() or "plantmanager" in record.name.lower()