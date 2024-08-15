import shlex
from abc import ABC
from typing import List, Set

import psutil
from psutil import NoSuchProcess

from model.process import Process
from service.services_info_service import ServicesInfoService


class ProcessesInfoService(ABC):
    """
    The ProcessesInfoService class provides methods for retrieving information about running processes.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    __prev_pids: Set[int] = []

    @classmethod
    def get_list(cls, only_new: bool, return_pids: set[int]) -> dict[int, Process]:
        """
        Retrieves a dictionary of running processes and their information.

        Args:
            only_new (bool): If True, returns only processes that have started since the last call.
                             If False, returns all currently running processes.
            return_pids (list[int]): A list of process IDs to include even if they are not new.

        Returns:
            dict[int, Process]: A dictionary with process IDs as keys and Process objects as values.
        """
        services = ServicesInfoService.get_list()
        result: dict[int, Process] = {}
        current_pids: List[int] = psutil.pids()

        for pid in current_pids:
            if only_new and pid in cls.__prev_pids and pid not in return_pids:
                continue

            try:
                process = psutil.Process(pid)
                info = process.as_dict(attrs=['name', 'exe', 'nice', 'ionice', 'cpu_affinity', 'cmdline'])
                cmdline = shlex.join(info['cmdline'] or [])

                result[pid] = Process(
                    pid,
                    info['exe'],
                    cmdline,
                    info['name'],
                    int(info['nice']) if info['nice'] else None,
                    int(info['ionice']) if info['ionice'] else None,
                    info['cpu_affinity'],
                    process,
                    services.get(pid)
                )
            except NoSuchProcess:
                pass

        cls.__prev_pids = set(current_pids)
        return result
