import json
import webbrowser
from typing import Optional, Union
from urllib import request

from constants.app_info import CURRENT_TAG, APP_NAME
from constants.updates import API_UPDATE_URL, UPDATE_URL
from util.messages import show_error, show_info, yesno_info_box
from util.utils import compare_version


def check_new_version() -> Optional[Union[str, bool]]:
    """
    Check the latest version by making a request to the update URL and comparing it with the current tag.

    Returns:
        Optional[Union[str, False]]: The latest tag if it is greater than the current tag, False otherwise. None if an exception occurs.
    """
    try:
        with request.urlopen(API_UPDATE_URL) as response:
            data = json.loads(response.read().decode())
            latest_tag = data['tag_name']

            if compare_version(latest_tag, CURRENT_TAG) > 0:
                return latest_tag
            else:
                return False
    except:
        return None


def check_updates(silent: bool = False):
    new_version = check_new_version()

    if new_version is None:
        if not silent:
            show_error("Failed to check for updates. Please check your internet connection.")
    elif not new_version:
        if not silent:
            show_info("You are using the latest version.")
    else:
        message = f"A new version {new_version} is available. Would you like to update {APP_NAME} now?"

        if yesno_info_box(message):
            webbrowser.open(UPDATE_URL, new=0, autoraise=True)
