import pystray
from PIL import Image
from pystray import MenuItem, Menu
from pystray._win32 import Icon

from constants.app_info import APP_NAME_WITH_VERSION, APP_NAME
from constants.resources import APP_ICON
from constants.ui import OPEN_LOG_LABEL, OPEN_CONFIG_LABEL
from ui.settings import open_settings, is_opened_settings, get_settings
from util.files import open_log_file, open_config_file
from util.startup import toggle_startup, is_in_startup
from util.updates import check_updates
from util.utils import is_portable


def close_app(item):
    if not is_opened_settings():
        return item.stop()

    settings = get_settings()

    def close():
        if settings.close():
            item.stop()

    settings.after_idle(close)


def init_tray() -> Icon:
    """
    Initializes and returns a system tray icon.

    Returns:
        Icon: The system tray icon.
    """
    image: Image = Image.open(APP_ICON)

    menu: tuple[MenuItem, ...] = (
        MenuItem(APP_NAME_WITH_VERSION, lambda item: open_settings(), default=True),
        Menu.SEPARATOR,

        MenuItem(OPEN_CONFIG_LABEL, lambda _: open_config_file()),
        MenuItem(OPEN_LOG_LABEL, lambda _: open_log_file()),
        Menu.SEPARATOR,

        MenuItem(
            'Run on Startup',
            lambda item: toggle_startup(),
            lambda item: is_in_startup(),
            visible=is_portable()
        ),
        MenuItem(
            'Check for Updates',
            lambda item: check_updates()
        ),
        Menu.SEPARATOR,

        MenuItem('Quit', close_app),
    )

    return pystray.Icon("tray_icon", image, APP_NAME, menu)
