from abc import ABC

import psutil
from psutil import STATUS_STOPPED, NoSuchProcess, ZombieProcess, AccessDenied
from psutil._pswindows import WindowsService

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
    The ServicesInfoService class provides methods for retrieving information about Windows services.
    """

    @staticmethod
    def get_running_services() -> dict[int, Service]:
        result: dict[int, Service] = {}

        for service in psutil.win_service_iter():
            try:
                # noinspection PyUnresolvedReferences
                info = service._query_status()
                status = info['status']
                pid = info['pid']

                if pid == STATUS_STOPPED:
                    continue

                result[pid] = Service(
                    pid,
                    service.name(),
                    service.display_name(),
                    status
                )
            except NoSuchProcess:
                pass

        return result

    @staticmethod
    def get_services() -> list[Service]:
        result: list[Service] = []

        for service in psutil.win_service_iter():
            try:
                # noinspection PyUnresolvedReferences
                info = service._query_status()

                result.append(Service(
                    info['pid'],
                    service.name(),
                    info['status']
                ))
            except NoSuchProcess:
                pass

        return result
