import os
from time import sleep
from typing import Optional

import psutil
from psutil._pswindows import Priority, IOPriority
from pystray._win32 import Icon

from configuration.config import Config
from configuration.migration.all_migration import run_all_migration
from constants.app_info import APP_NAME
from constants.files import LOG_FILE_NAME
from constants.log import LOG
from constants.threads import THREAD_SETTINGS, THREAD_TRAY
from constants.ui import SETTINGS_TITLE
from service.config_service import ConfigService
from service.rules_service import RulesService
from ui.settings import open_settings
from ui.tray import init_tray
from util.messages import yesno_error_box, show_error
from util.scheduler import TaskScheduler
from util.startup import update_startup
from util.updates import check_updates


def priority_setup():
    """
    Set process priority and I/O priority.

    This function sets the process priority to BELOW_NORMAL_PRIORITY_CLASS and the I/O priority to IOPRIO_LOW.
    """
    try:
        process = psutil.Process()
        process.nice(Priority.BELOW_NORMAL_PRIORITY_CLASS)
        process.ionice(IOPriority.IOPRIO_LOW)
    except psutil.Error:
        pass


def main_loop(tray: Icon):
    """
    Main application loop for applying rules at regular intervals, updating the configuration, and managing the system tray icon.

    Args:
        tray (Icon): The system tray icon instance to be managed within the loop. It will be stopped gracefully
            when the loop exits.
    """
    TaskScheduler.schedule_task(THREAD_TRAY, tray.run)

    LOG.info('Application started')

    config: Optional[Config] = None
    is_changed: bool
    last_error_message = None

    while TaskScheduler.check_task(THREAD_TRAY):
        try:
            config, is_changed = ConfigService.reload_if_changed(config)

            if is_changed:
                LOG.info("Configuration file has been modified. Reloading all rules to apply changes.")

            RulesService.apply_rules(config, not is_changed)
            last_error_message = None
        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            if not config:
                config = Config()

            current_error_message = str(e)

            if current_error_message != last_error_message:
                LOG.exception("Error in the loop of loading and applying rules.")

                last_error_message = current_error_message

                if ConfigService.rules_has_error():
                    show_rules_error_message()
                else:
                    show_abstract_error_message(False)

        sleep(config.ruleApplyIntervalSeconds)

    LOG.info('The application has stopped')


def start_app():
    """
    Start application.

    This function loads the configuration, sets up logging and process priorities, and starts the main application loop.
    """
    tray: Optional[Icon] = None

    try:
        run_all_migration()
        update_startup()
        priority_setup()
        check_updates(True)

        tray: Icon = init_tray()
        main_loop(tray)
    except KeyboardInterrupt:
        pass
    except:
        LOG.exception("A critical error occurred, causing the application to stop.")
        show_abstract_error_message(True)
    finally:
        if tray:
            tray.stop()


def show_rules_error_message():
    message = "An error has occurred while loading or applying the rules.\n"

    if TaskScheduler.check_task(THREAD_SETTINGS):
        message += "Please check the correctness of the rules."
        show_error(message)
    else:
        message += f"Would you like to open the {SETTINGS_TITLE} to review and correct the rules?"
        if yesno_error_box(message):
            open_settings()


def show_abstract_error_message(will_closed: bool):
    will_closed_text = 'The application will now close.' if will_closed else ''
    message = (
        f"An error has occurred in the {APP_NAME} application. {will_closed_text}\n"
        f"To troubleshoot, please check the log file `{LOG_FILE_NAME}` for details.\n\n"
        f"Would you like to open the log file?"
    )

    if yesno_error_box(message):
        os.startfile(LOG_FILE_NAME)
