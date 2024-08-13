import os
from abc import ABC
from typing import Optional, List

import psutil
from psutil import AccessDenied, NoSuchProcess
from pyuac import isUserAdmin

from configuration.config import Config
from configuration.rule import ProcessRule, ServiceRule
from constants.log import LOG
from enums.bool import BoolStr
from enums.io_priority import to_iopriority
from enums.priority import to_priority
from enums.process import ProcessParameter
from enums.selector import SelectorType
from model.process import Process
from service.processes_info_service import ProcessesInfoService
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
    __force_pids: set[int] = set()

    @classmethod
    def apply_rules(cls, config: Config, only_new: bool):
        """
        Apply the rules defined in the configuration to handle processes and services.

        Args:
            config (Config): The configuration object containing the rules.
            only_new (bool, optional): If set to True, all processes will be fetched, regardless of their status.

        Returns:
            None
        """
        if not (config.serviceRules or config.processRules):
            return

        cls.__light_gc_ignored_process_parameters()
        cls.__force_pids = cls.__handle_processes(
            config,
            ProcessesInfoService.get_list(only_new, cls.__force_pids)
        )

    @classmethod
    def __handle_processes(cls, config: Config, processes: dict[int, Process]) -> set[int]:
        force_pids: set[int] = set()

        for pid, process in processes.items():
            if pid in cls.__ignore_pids:
                continue

            try:
                rule: Optional[ProcessRule | ServiceRule] = cls.__first_rule_by_name(config, process)

                if not rule:
                    continue

                if rule.force == BoolStr.YES:
                    force_pids.add(pid)

                tuple_pid_name = (pid, process.name)
                ignored_process_parameters = cls.__ignored_process_parameters.get(tuple_pid_name, set())
                not_success: List[ProcessParameter] = []

                if ProcessParameter.AFFINITY not in ignored_process_parameters:
                    cls.__set_affinity(not_success, process, rule)

                if ProcessParameter.NICE not in ignored_process_parameters:
                    cls.__set_nice(not_success, process, rule)

                if ProcessParameter.IONICE not in ignored_process_parameters:
                    cls.__set_ionice(not_success, process, rule)

                if not_success:
                    cls.__ignore_process_parameter(tuple_pid_name, set(not_success))

                    LOG.warning(f"Set failed [{', '.join(map(str, not_success))}] "
                                f"for {process.name} ({process.pid}"
                                f"{', ' + process.service.name + '' if process.service else ''}"
                                f")")
            except NoSuchProcess:
                LOG.warning(f"No such process: {pid}")

        return force_pids

    @classmethod
    def __set_ionice(cls, not_success, process: Process, rule: ProcessRule | ServiceRule):
        io_priority = to_iopriority[rule.ioPriority]

        if not io_priority or process.ionice == io_priority:
            return

        parameter = ProcessParameter.IONICE

        try:
            process.process.ionice(io_priority)
            LOG.info(f"Set {parameter.value} {rule.ioPriority.value} for {process.name} ({process.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __set_nice(cls, not_success, process: Process, rule: ProcessRule | ServiceRule):
        priority = to_priority[rule.priority]

        if not priority or process.nice == priority:
            return

        parameter = ProcessParameter.NICE

        try:
            process.process.nice(priority)
            LOG.info(f"Set {parameter.value} {rule.priority.value} for {process.name} ({process.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __set_affinity(cls, not_success, process: Process, rule: ProcessRule | ServiceRule):
        if not rule.affinity or process.affinity == rule.affinity:
            return

        parameter = ProcessParameter.AFFINITY

        try:
            process.process.cpu_affinity(rule.affinity)
            affinity = format_affinity(rule.affinity)
            LOG.info(f"Set {parameter.value} {affinity} for {process.name} ({process.pid})")
        except AccessDenied:
            not_success.append(parameter)

    @classmethod
    def __first_rule_by_name(
            cls,
            config: Config,
            process: Process
    ) -> Optional[ProcessRule | ServiceRule]:
        service = process.service

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