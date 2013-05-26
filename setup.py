import sys
from cx_Freeze import setup, Executable

#
path = sys.path + ["pyjtt"]
includes = ["custom_logging"]
build_exe_options = {
"path": path,
"icon": "resources\icons\clock.ico"}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "pyjtt",
        version = "1.1",
        description = "Jira Time Tracker",
        options = {"build_exe": build_exe_options},
        executables = [Executable("pyjtt\pyjtt_gui.py", base=base)])