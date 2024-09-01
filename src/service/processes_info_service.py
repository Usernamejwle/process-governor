import subprocess
from abc import ABC

import psutil
from psutil import NoSuchProcess

from model.process import Process
from service.services_info_service import ServicesInfoService
from util.utils import none_int


class ProcessesInfoService(ABC):
    """
    The ProcessesInfoService class provides methods for retrieving information about running processes.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    __prev_pids: set[int] = []

    @classmethod
    def get_processes(
            cls,
            only_new: bool,
            force_return_pids: set[int] = None
    ) -> dict[int, Process]:
        """
        Retrieves a dictionary of running processes and their information.

        Args:
            only_new (bool): If True, returns only processes that have started since the last call.
                             If False, returns all currently running processes.
            force_return_pids (set[int], optional): A set of process IDs that should be included in the result
                                                    even if they are not new. Defaults to an empty set if not provided.
        Returns:
            dict[int, Process]: A dictionary where keys are process IDs and values are Process objects,
                                containing detailed information about each running process.
        """
        services = ServicesInfoService.get_services()
        result: dict[int, Process] = {}
        current_pids: list[int] = psutil.pids()
        force_return_pids = force_return_pids or set()

        for pid in current_pids:
            if only_new and pid in cls.__prev_pids and pid not in force_return_pids:
                continue

            try:
                process = psutil.Process(pid)
                service = services.get(pid)

                info = process.as_dict(attrs=['name', 'exe', 'nice', 'ionice', 'cpu_affinity', 'cmdline'])
                result[pid] = Process.model_construct(
                    pid=pid,
                    process_name=info['name'],
                    service_name=getattr(service, 'name', None),
                    bin_path=info['exe'],
                    cmd_line=cls._get_command_line(pid, info),
                    priority=none_int(info['nice']),
                    io_priority=none_int(info['ionice']),
                    affinity=info['cpu_affinity'],
                    process=process,
                    service=service
                )
            except NoSuchProcess:
                pass

        if only_new:
            cls.__prev_pids = set(current_pids)

        return result

    @staticmethod
    def _get_command_line(pid, info):
        if pid == 0:
            return ''

        cmdline = info['cmdline'] or ['']

        if not cmdline[0]:
            cmdline[0] = info['exe'] or info['name']

        if not cmdline[0]:
            return ''

        return subprocess.list2cmdline(cmdline)
