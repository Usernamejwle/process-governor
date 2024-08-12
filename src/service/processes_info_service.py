from abc import ABC
from typing import List, Set

import psutil
from psutil import NoSuchProcess

from model.process import Process


class ProcessesInfoService(ABC):
    """
    The ProcessesInfoService class provides methods for retrieving information about running processes.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    __prev_pids: Set[int] = []

    @classmethod
    def get_list(cls, only_new: bool = False) -> dict[int, Process]:
        """
        Get a dictionary of running processes and their information.

        Args:
            only_new (bool): If True, return only the newly created processes since the last check.
                             If False, return all running processes.

        Returns:
            dict[int, Process]: A dictionary where keys are process IDs (pids) and values are Process objects
            representing the running processes.
        """
        result: dict[int, Process] = {}
        current_pids: List[int] = psutil.pids()

        for pid in current_pids:
            if only_new and pid in cls.__prev_pids:
                continue

            try:
                process = psutil.Process(pid)
                info = process.as_dict(attrs=['name', 'exe', 'nice', 'ionice', 'cpu_affinity', 'cmdline'])
                cmdline = ' '.join(process for process in info['cmdline'] or [''] if process)

                result[pid] = Process(
                    pid,
                    info['exe'],
                    cmdline,
                    info['name'],
                    int(info['nice']) if info['nice'] else None,
                    int(info['ionice']) if info['ionice'] else None,
                    info['cpu_affinity'],
                    process
                )
            except NoSuchProcess:
                pass

        cls.__prev_pids = set(current_pids)
        return result
