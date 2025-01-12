import os
import sys

import psutil

from constants.app_info import APP_PROCESSES
from constants.files import LOCK_FILE_NAME
from constants.log import LOG
from util.messages import show_error


def is_process_running(pid):
    """
    Check if a process with the given PID is running.

    Args:
        pid: The process ID (PID) to check.

    Returns:
        bool: True if the process is running, False otherwise.
    """
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        return process.is_running() and process_name in APP_PROCESSES
    except psutil.NoSuchProcess:
        return False


def create_lock_file():
    """
    Create a lock file to prevent multiple instances of a process from running simultaneously.

    If the lock file already exists, it checks if the process that created it is still running. If it is,
    the current process exits to avoid running multiple instances.

    If the lock file does not exist or the process is no longer running, it creates the lock file with the
    current process's PID.
    """

    if os.path.isfile(LOCK_FILE_NAME):
        # Check if the process that created the lock file is still running
        with open(LOCK_FILE_NAME, "r") as file:
            pid_str = file.read().strip()
            if pid_str:
                if is_process_running(int(pid_str)):
                    message = ("The application is already running.\n"
                               "Please close the existing instance before starting a new one.")

                    LOG.error(message)
                    show_error(message)
                    sys.exit(1)

    # Create the lock file with the current process's PID
    with open(LOCK_FILE_NAME, "w") as file:
        file.write(str(os.getpid()))


def remove_lock_file():
    """
    Remove the lock file used to prevent multiple instances of the application.

    This function deletes the lock file created to ensure that only one instance of the application is running.
    """
    os.remove(LOCK_FILE_NAME)
