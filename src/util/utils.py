import re
import sys
from enum import Enum
from functools import lru_cache, cache
from re import Pattern
from types import NoneType
from typing import get_origin, get_args, Union, Annotated, Optional

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image


@cache
def path_pattern_to_regex(pattern: str) -> Optional[Pattern]:
    """
    Converts a glob-like path pattern to a regular expression, with partial support for glob syntax.

    Args:
        pattern (str): The path pattern to convert.

    Returns:
        re.Pattern: The compiled regular expression.

    Supports:
        - "*" matches any sequence of characters except the path separator.
        - "?" matches any single character except the path separator.
        - "**/" matches any number of nested directories.
    """

    pattern = pattern.strip()

    if not pattern:
        return None

    pattern = re.escape(pattern.replace('\\', '/'))
    pattern = pattern.replace(r'/', '[/]')
    pattern = pattern.replace('\\*\\*[/]', '(.*[/])?')
    pattern = pattern.replace('\\?', '[^/]')
    pattern = pattern.replace('\\*', '[^/]*')
    pattern = pattern.replace('/', r'\\/')

    return re.compile(f"^{pattern}$", re.IGNORECASE)


@lru_cache
def path_match(pattern: str, value: str) -> bool:
    """
    Checks if any of the provided values match the given pattern.

    Args:
        pattern (str): The pattern to match against, supporting wildcards.
        value (str): The value to test against the pattern.

    Returns:
        bool: True if any value matches the pattern, False otherwise.
    """

    if not pattern:
        return False

    if pattern == value:
        return True

    regex = path_pattern_to_regex(pattern)

    if not pattern:
        return False

    return regex.match(value) is not None


def is_portable():
    """
    Check if the script is running in a portable environment.
    """
    return getattr(sys, 'frozen', False)


def compare_version(version1, version2):
    """
    Compare two version numbers.

    Parameters:
        version1 (str): The first version number.
        version2 (str): The second version number.

    Returns:
        int: 1 if version1 is greater than version2, -1 if version1 is less than version2, 0 if they are equal.
    """
    version1 = version1.lstrip('v')
    version2 = version2.lstrip('v')

    versions1 = [int(v) for v in version1.split(".")]
    versions2 = [int(v) for v in version2.split(".")]

    for i in range(max(len(versions1), len(versions2))):
        v1 = versions1[i] if i < len(versions1) else 0
        v2 = versions2[i] if i < len(versions2) else 0

        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1

    return 0


def extract_type(annotation):
    origin = get_origin(annotation)

    if origin is None:
        return annotation

    args = get_args(annotation)

    if origin == Union:
        non_none_args = [arg for arg in args if arg != NoneType]
        if len(non_none_args) == 1:
            return extract_type(non_none_args[0])
        else:
            return [extract_type(arg) for arg in non_none_args]

    elif origin == Annotated:
        return extract_type(args[0])

    elif args:
        return origin[tuple(extract_type(arg) for arg in args)]

    return annotation


def is_optional_type(annotation):
    if get_origin(annotation) == Union:
        union_args = get_args(annotation)
        for arg in union_args:
            if arg == NoneType or is_optional_type(arg):
                return True
    return False


def none_int(value: str) -> Optional[int]:
    return int(value) if value else None


def get_values_from_enum(annotation):
    origin_type = extract_type(annotation)
    values = []

    if not issubclass(origin_type, Enum):
        return values

    if is_optional_type(annotation):
        values.append('')

    for e in origin_type:
        values.append(str(e.value))

    return values


@cache
def get_icon_from_exe(exe_path, icon_index=0, large=False):
    if large:
        icon_size = (
            win32api.GetSystemMetrics(win32con.SM_CXICON),
            win32api.GetSystemMetrics(win32con.SM_CYICON)
        )
    else:
        icon_size = (
            win32api.GetSystemMetrics(win32con.SM_CXSMICON),
            win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        )

    hdc = None
    hdc_mem = None
    bmp = None
    list_of_large_hicon = []
    list_of_small_hicon = []

    try:
        list_of_large_hicon, list_of_small_hicon = win32gui.ExtractIconEx(exe_path, icon_index)
        list_of_hicon = list_of_large_hicon if large else list_of_small_hicon

        if not list_of_hicon:
            return

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hdc_mem = hdc.CreateCompatibleDC()

        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, icon_size[0], icon_size[1])

        hdc_mem.SelectObject(bmp)

        win32gui.DrawIconEx(
            hdc_mem.GetSafeHdc(),
            0,
            0,
            list_of_hicon[0],
            icon_size[0],
            icon_size[1],
            0,
            None,
            win32con.DI_NORMAL
        )

        bmp_info = bmp.GetInfo()
        bmp_bits = bmp.GetBitmapBits(True)

        return Image.frombuffer(
            'RGBA',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_bits, 'raw', 'BGRA', 0, 1
        )
    finally:
        if bmp:
            handle = bmp.GetHandle()

            if handle:
                win32gui.DeleteObject(handle)

        if hdc_mem:
            hdc_mem.DeleteDC()

        if hdc:
            hdc.DeleteDC()
            win32gui.ReleaseDC(0, hdc.GetSafeHdc())

        for hicon in list_of_large_hicon:
            win32gui.DestroyIcon(hicon)

        for hicon in list_of_small_hicon:
            win32gui.DestroyIcon(hicon)
