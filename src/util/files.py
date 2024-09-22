import ctypes
import os
import subprocess

import win32com.client

from constants.files import LOG_FILE_NAME, CONFIG_FILE_NAME
from util.messages import show_error


def open_log_file():
    return os.startfile(LOG_FILE_NAME)


def open_config_file():
    os.startfile(CONFIG_FILE_NAME)


FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
SHELL32 = ctypes.WinDLL('shell32', use_last_error=True)


def explore(path):
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', path])


def show_file_properties(filepath, hwnd=None):
    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' does not exist")

    SHELL32.SHObjectProperties(hwnd, 0x00000002, filepath, None)


__mmc = None


def show_service_properties(service_name):
    global __mmc

    try:
        __mmc.Document
    except:
        __mmc = None

    if __mmc is None:
        __mmc = win32com.client.Dispatch("MMC20.Application")
        __mmc.Load("services.msc")

    doc = __mmc.Document
    view = doc.ActiveView
    items = view.ListItems

    for item in items:
        if item.Name == service_name:
            __mmc.UserControl = True
            view.Select(item)
            view.DisplaySelectionPropertySheet()
            break
    else:
        __mmc.Quit()
        show_error(f"The properties window for the '{service_name}' service "
                   f"could not be opened, because the service was not found.")
