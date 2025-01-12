import sys

from constants.app_info import STARTUP_TASK_NAME
from constants.resources import STARTUP_SCRIPT
from util.utils import is_portable
from util.windows_scheduler import WindowsTaskScheduler


def is_in_startup():
    """
    Check if the current application is set to run during system startup.

    Returns:
        bool: True if the application is set to run during system startup, False otherwise.
    """
    return WindowsTaskScheduler.check_task(STARTUP_TASK_NAME)


def add_to_startup():
    """
    Add the current application to the system's startup programs.
    """
    if is_in_startup():
        return

    WindowsTaskScheduler.create_startup_task(
        STARTUP_TASK_NAME,
        f"'{STARTUP_SCRIPT}' '{sys.executable}'"
    )


def remove_from_startup():
    """
    Remove the current application from the system's startup programs.
    """
    if is_in_startup():
        WindowsTaskScheduler.delete_task(STARTUP_TASK_NAME)


def toggle_startup():
    """
    Toggle the startup status of the application.
    """
    if is_in_startup():
        remove_from_startup()
    else:
        add_to_startup()


def update_startup():
    """
    Update autostart if the app has been moved.
    """
    if not is_portable():
        return

    if not is_in_startup():
        return

    remove_from_startup()
    add_to_startup()
