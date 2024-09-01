import os

from constants.files import LOG_FILE_NAME, CONFIG_FILE_NAME


def open_log_file():
    return os.startfile(LOG_FILE_NAME)


def open_config_file():
    os.startfile(CONFIG_FILE_NAME)
