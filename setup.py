import sys
import os
from cx_Freeze import setup, Executable

path = ["pyjtt"] + sys.path
includes = ["custom_logging"]
build_exe_options = {
"path": path,
"icon": "resources\icons\clock.ico"}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
target_app = os.path.join("pyjtt", "pyjtt_gui.py")
	
setup(  name = "pyjtt",
        version = "1.1",
        description = "Jira Time Tracker",
        options = {"build_exe": build_exe_options},
        executables = [Executable(target_app, base=base)])