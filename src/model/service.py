from dataclasses import dataclass


@dataclass
class Service:
    """
    The Service class represents information about a Windows service.

    It includes attributes such as service process ID (pid), name, display name and current status.
    """

    pid: int
    """
    The process ID (pid) associated with the Windows service.
    """

    name: str
    """
    The name of the Windows service.
    """

    display_name: str
    """
    The display name of the Windows service.
    """

    status: str
    """
    The current status of the Windows service.
    """
