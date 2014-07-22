import sys
import os
from cx_Freeze import setup, Executable

import base_setup

path = ["pyjtt"] + sys.path
icon_path = os.path.join("resources", "icons", "clock.ico")
build_exe_options = {"path": path,
                     "icon": icon_path,
                     "include_msvcr": True,   #skip error msvcr100.dll missing,
                     # Fix error with "This application failed to start because it could not find or load the QT platform plugin "windows"."
                     "include_files": ['C:\Python34\Lib\site-packages\PyQt5\libEGL.dll']
                     }

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "pyJTT",           	   # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]pyjtt.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     '%APPDATA%\pyjtt'     # WkDir
     ),
	 ("ProgramMenuShortcut",        # Shortcut
     "ProgramMenuFolder",          # Directory_
     "pyJTT",           	   # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]pyjtt.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     '%APPDATA%\pyjtt'     # WkDir
     )]
	 
 
# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

target_app = os.path.join("pyjtt", "app.py")

setup(  name = "pyjtt",
        version = "1.2.1",
        description = "Jira Time Tracker",
        maintainer="Nikolay Golub",
        maintainer_email="nikolay.v.golub@gmail.com",
        long_description = "Allows track time in JIRA online and manage worklogs",
        license = "GNU GENERAL PUBLIC LICENSE Version 3",
        options = {"build_exe": build_exe_options,
                   "bdist_msi": bdist_msi_options,},
        executables = [Executable(target_app,
                                  base=base,
                                  targetName="pyjtt.exe",
                                  shortcutName="pyJTT",
                                  shortcutDir="DesktopFolder")])
