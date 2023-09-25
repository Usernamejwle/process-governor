from dataclasses import dataclass
from typing import Optional

from psutil._pswindows import Priority, IOPriority

from configuration.handler.io_priority import IoPriorityHandler
from configuration.handler.priority import PriorityHandler
from util.utils import parse_affinity


@dataclass
class Rule:
    """
    The Rule class defines a rule for configuring process and service behavior in Process Governor.

    Rules can be applied to processes or services based on criteria such as service selector, process selector, priority,
    I/O priority, and CPU core affinity.
    """

    serviceSelector: Optional[str] = None
    """
    A string specifying the name or pattern of the service to which this rule applies. Default is None.
    """

    processSelector: Optional[str] = None
    """
    A string specifying the name or pattern of the process to which this rule applies. Default is None.
    """

    priority: Optional[Priority] = None
    """
    The priority level to set for the process or service. Default is None (no priority specified).
    """

    ioPriority: Optional[IOPriority] = None
    """
    The I/O priority to set for the process or service. Default is None (no I/O priority specified).
    """

    affinity: Optional[str] = None
    """
    A string specifying the CPU core affinity for the process or service. Default is None (no affinity specified).
    """

    def affinity_as_list(self):
        """
        Get the CPU core affinity as a list of integers.

        This method parses the affinity string and returns a list of integers representing the CPU cores to which the
        process or service should be bound.
        """
        return parse_affinity(self.affinity)


PriorityHandler.handles(Priority)
IoPriorityHandler.handles(IOPriority)
