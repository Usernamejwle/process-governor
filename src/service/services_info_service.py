from abc import ABC

import psutil
from psutil import STATUS_STOPPED, NoSuchProcess, ZombieProcess, AccessDenied
from psutil._pswindows import WindowsService

from constants.log import LOG
from model.service import Service
from util.decorators import suppress_exception

# Fix bug of psutil
WindowsService.description = suppress_exception(
    WindowsService.description,
    (FileNotFoundError, ZombieProcess, AccessDenied, OSError),
    lambda: ""
)
WindowsService._query_config = suppress_exception(
    WindowsService._query_config,
    (FileNotFoundError, ZombieProcess, AccessDenied, OSError),
    lambda: dict(display_name="", binpath="", username="", start_type="")
)


class ServicesInfoService(ABC):
    """
    The ServicesInfoService class provides methods for retrieving information about running services.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    @staticmethod
    def get_services() -> dict[int, Service]:
        """
        Get a dictionary of running services and their information.

        Returns:
            dict[int, Service]: A dictionary where keys are process IDs (pids) and values are Service objects
            representing the running services.
        """
        result: dict[int, Service] = {}

        for service in psutil.win_service_iter():
            try:
                info = service.as_dict()

                if info['status'] == STATUS_STOPPED:
                    continue

                result[info['pid']] = Service(
                    info['pid'],
                    info['name'],
                    info['display_name'],
                    info['description'],
                    info['status'],
                    info['binpath']
                )
            except NoSuchProcess:
                LOG.warning(f"No such service: {service.name}")

        return result
