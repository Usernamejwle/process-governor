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

    _cache: dict[int, Process] = {}

    @classmethod
    def get_processes(cls) -> dict[int, Process]:
        """
        Returns a dictionary with information about running processes.

        Returns:
            dict[int, Process]: A dictionary with information about running processes.
        """

        cache = cls._cache
        services = ServicesInfoService.get_services()
        pids = set(psutil.pids())

        for pid in pids:
            try:
                process_info = psutil.Process(pid)
                info = process_info.as_dict(attrs=[
                    'exe',
                    'nice', 'ionice', 'cpu_affinity'
                ])

                if pid in cache:
                    process = cache[pid]

                    if process.bin_path == info['exe']:
                        process.priority = none_int(info['nice'])
                        process.io_priority = none_int(info['ionice'])
                        process.affinity = info['cpu_affinity']
                        process.is_new = False
                        continue

                service = services.get(pid)
                info = process_info.as_dict(attrs=[
                    'name', 'exe', 'cmdline',
                    'nice', 'ionice', 'cpu_affinity'
                ])

                cache[pid] = Process.model_construct(
                    pid=pid,
                    process_name=info['name'],
                    service_name=getattr(service, 'name', None),
                    bin_path=info['exe'],
                    cmd_line=cls._get_command_line(pid, info),
                    priority=none_int(info['nice']),
                    io_priority=none_int(info['ionice']),
                    affinity=info['cpu_affinity'],
                    process=process_info,
                    service=service,
                    is_new=True
                )
            except NoSuchProcess:
                pass

        deleted_pids = cache.keys() - pids

        for pid in deleted_pids:
            del cache[pid]

        return cache.copy()

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
