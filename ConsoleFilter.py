import logging

#TODO if critical: send email
class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return "btlewrap" not in record.name and "miflora" not in record.name and ("action" in record.getMessage().lower() or "fixing" in record.getMessage().lower())