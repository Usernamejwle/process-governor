import os
import subprocess

from constants.files import LOG_FILE_NAME, CONFIG_FILE_NAME


def open_log_file():
    return os.startfile(LOG_FILE_NAME)


def open_config_file():
    os.startfile(CONFIG_FILE_NAME)


FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


def explore(path):
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', path])
