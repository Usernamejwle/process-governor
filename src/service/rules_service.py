import os
from abc import ABC
from typing import Optional, List

import psutil
from psutil import AccessDenied, NoSuchProcess
from pyuac import isUserAdmin

from configuration.config import Config
from configuration.rule import ProcessRule, ServiceRule
from constants.log import LOG
from enums.io_priority import to_iopriority
from enums.priority import to_priority
from enums.process import ProcessParameter
from enums.selector import SelectorType
from model.process import Process
from model.service import Service
from service.processes_info_service import ProcessesInfoService
from service.services_info_service import ServicesInfoService
from util.cpu import format_affinity
from util.decorators import cached
from util.utils import path_match


class RulesService(ABC):
    """
    The RulesService class provides methods for applying rules to processes and services.
    It is an abstract base class (ABC) to be subclassed by specific implementation classes.
    """

    __ignore_pids: set[int] = {0, os.getpid()}
    __ignored_process_parameters: dict[tuple[int, str], set[ProcessParameter]] = {}

    @classmethod
    def apply_rules(cls, config: Config, force=False):
        """
        Apply the rules defined in the configuration to handle processes and services.

        Args:
            config (Config): The configuration object containing the rules.
            force (bool, optional): If set to True, all processes will be fetched,
                                    regardless of their status. Defaults to False.

        Returns:
            None
        """
        if not (config.serviceRules or config.processRules):
            return

        cls.__light_gc_ignored_process_parameters()

        services: dict[int, Service] = ServicesInfoService.get_list()
        processes: dict[int, Process]

        if force:
            LOG.info("Configuration file has been modified. Reloading all rules to apply changes.")
            processes = ProcessesInfoService.get_list()
        else:
            processes = ProcessesInfoService.get_list(True)

        cls.__handle_processes(config, processes, services)

    @classmethod
    def __handle_processes(cls, config: Config, processes: dict[int, Process], services: dict[int, Service]):
        for pid, process_info in processes.items():
            if pid in cls.__ignore_pids:
                continue

            try:
                service_info: Service = services.get(pid)
                rule: Optional[ProcessRule | ServiceRule] = cls.__first_rule_by_name(config, service_info, process_info)

                if not rule:
                    continue

                tuple_pid_name = (pid, process_info.name)
                ignored_process_parameters = cls.__ignored_process_parameters.get(tuple_pid_name, set())
                not_success: List[ProcessParameter] = []

                if ProcessParameter.AFFINITY not in ignored_process_parameters:
                    cls.__set_affinity(not_success, process_info, rule)

                if ProcessParameter.NICE not in ignored_process_parameters:
                    cls.__set_nice(not_success, process_info, rule)

                if ProcessParameter.IONICE not in ignored_process_parameters:
                    cls.__set_ionice(not_success, process_info, rule)

                if not_success:
                    cls.__ignore_process_parameter(tuple_pid_name, set(not_success))

                    LOG.warning(f"Set failed [{', '.join(map(str, not_success))}] "
                                f"for {process_info.name} ({process_info.pid}"
                                f"{', ' + service_info.name + '' if service_info else ''}"
                                f")")
            except NoSuchProcess:
                LOG.warning(f"No such process: {pid}")

    @classmethod
    def __set_ionice(cls, not_success, process_info, rule: ProcessRule | ServiceRule):
        if not rule.ioPriority or process_info.ionice == rule.ioPriority:
            return

        parameter = ProcessParameter.IONICE

        try:
            io_priority = to_iopriority[rule.ioPriority]
            process_info.process.ionice(io_priority)
            LOG.info(f"Set {parameter.value} {rule.ioPriority.value} for {process_info.name} ({process_info.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __set_nice(cls, not_success, process_info, rule: ProcessRule | ServiceRule):
        if not rule.priority or process_info.nice == rule.priority:
            return

        parameter = ProcessParameter.NICE

        try:
            priority = to_priority[rule.priority]
            process_info.process.nice(priority)
            LOG.info( f"Set {parameter.value} {rule.priority.value} for {process_info.name} ({process_info.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __set_affinity(cls, not_success, process_info: Process, rule: ProcessRule | ServiceRule):
        if not rule.affinity:
            return

        parameter = ProcessParameter.AFFINITY

        if process_info.affinity == rule.affinity:
            return

        try:
            process_info.process.cpu_affinity(rule.affinity)
            LOG.info(
                f"Set {parameter.value} {format_affinity(rule.affinity)} for {process_info.name} ({process_info.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __first_rule_by_name(
            cls,
            config: Config,
            service: Service,
            process: Process
    ) -> Optional[ProcessRule | ServiceRule]:
        if service:
            for serviceRule in config.serviceRules:
                value = service.name

                if serviceRule.selectorBy == SelectorType.PATH:
                    value = service.binpath
                elif serviceRule.selectorBy == SelectorType.CMDLINE:
                    value = process.cmdline

                if path_match(serviceRule.selector, value):
                    return serviceRule

        for processRule in config.processRules:
            value = process.name

            if processRule.selectorBy == SelectorType.PATH:
                value = process.binpath
            elif processRule.selectorBy == SelectorType.CMDLINE:
                value = process.cmdline

            if path_match(processRule.selector, value):
                return processRule

        return None

    @classmethod
    def __ignore_process_parameter(cls, tuple_pid_name: tuple[int, str], parameters: set[ProcessParameter]):
        if isUserAdmin():
            cls.__ignored_process_parameters[tuple_pid_name] = parameters

    @classmethod
    @cached(5)  # Workaround to ensure the procedure runs only once every 5 seconds
    def __light_gc_ignored_process_parameters(cls):
        pids = psutil.pids()
        remove_pids: List[tuple[int, str]] = []

        for item in cls.__ignored_process_parameters.keys():
            pid, _ = item

            if pid not in pids:
                remove_pids.append(item)

        for item in remove_pids:
            del cls.__ignored_process_parameters[item]
