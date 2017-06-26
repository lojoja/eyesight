import logging
from logging.handlers import RotatingFileHandler

from click_log import ClickHandler, ColorFormatter as ClickFormatter

from eyesight import IS_ROOT, PROGRAM_NAME


# FILE = '/var/log/{}.log'.format(PROGRAM_NAME)
FILE = '{}.log'.format(PROGRAM_NAME)
RECORD_FORMAT = '%(asctime)s %(name)s [%(levelname)s]: %(message)s'
DATE_FORMAT = '%b %d %Y %H:%M:%S'
VERBOSITY_LEVELS = {True: logging.DEBUG, False: logging.WARNING}


def get_level(verbose):
    return VERBOSITY_LEVELS.get(verbose, logging.INFO)


def init(logger, verbose):
    click_handler = ClickHandler()
    click_handler.setLevel(get_level(verbose))
    click_handler.setFormatter(ClickFormatter())
    logger.addHandler(click_handler)

    if IS_ROOT:
        file_handler = RotatingFileHandler(FILE, maxBytes=10485760, backupCount=5, encoding='utf8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(RECORD_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)
