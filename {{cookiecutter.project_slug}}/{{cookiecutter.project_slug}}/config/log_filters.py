import logging


class InfoLogFilter(logging.Filter):

    def filter(self, record):
        """Only let records through that have log level INFO"""
        return record.levelno == logging.INFO
