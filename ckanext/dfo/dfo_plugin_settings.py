import os
import logging
from logging.handlers import TimedRotatingFileHandler

plugin_root = os.path.dirname(os.path.realpath(__file__))
log_folder = os.path.join(plugin_root, 'logs')
# Logging format
screen_fmt = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s(%(lineno)d) - %(message)s')


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # sh = logging.StreamHandler()
    # sh.setFormatter(screen_fmt)
    # sh.setLevel(level)
    # Only use file handler, don't fill up main CKAN log
    fh, log_file = get_file_logger()
    fh.setLevel(level)
    fh.setFormatter(screen_fmt)
    # if not logger.handlers:
    # logger.addHandler(sh)
    logger.addHandler(fh)
    logger.info('%s: Logging to %s' % (name, log_file))
    return logger


def get_file_logger():

    log_file = os.path.join(log_folder, 'dfoext.log')

    # Use rotating file handler, daily at midnight.
    fh = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        backupCount=30,
        encoding='utf-8')
    fh.setFormatter(screen_fmt)
    return fh, log_file