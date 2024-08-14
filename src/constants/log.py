import logging
import sys
from logging import StreamHandler, Logger, WARNING
from logging.handlers import RotatingFileHandler
from typing import Final

from configuration.logs import Logs
from constants.files import LOG_FILE_NAME

logging.addLevelName(WARNING, 'WARN')


def __log_setup() -> Logger:
    """
    Sets up the logging configuration.

    Retrieves the logging configuration from the `ConfigService` and sets up the logging handlers and formatters
    accordingly. If the logging configuration is disabled, the function does nothing.
    """

    log: Logger = logging.getLogger("proc-gov")
    log_cfg: Logs = Logs()

    log.setLevel(log_cfg.level_as_int())

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    if not log_cfg.enable:
        return log

    file_handler = RotatingFileHandler(
        LOG_FILE_NAME,
        maxBytes=log_cfg.maxBytes,
        backupCount=log_cfg.backupCount,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    return log


LOG: Final[logging.Logger] = __log_setup()
