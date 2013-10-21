import os
import platform


def get_app_working_dir():
    """Returns path to application operational folder.

    Options and local database are stored in this folder.
    """
    app_name = 'pyjtt'
    current_platform = platform.system()
    if 'Linux' == current_platform:
        return os.path.join(os.environ['HOME'], '.' + app_name)
    elif 'Windows' == current_platform:
        return os.path.join(os.environ['APPDATA'], app_name)
    else:
        return os.path.abspath('.' + app_name)


config_filename = os.path.join(get_app_working_dir(),'pyjtt.cfg')