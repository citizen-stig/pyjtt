import sys
import os
from cx_Freeze import setup, Executable

options = {}

path = ["pyjtt"] + sys.path
icon_path = os.path.join("resources", "icons", "icon.icns")

build_exe_options = {
    'path': path,
    'include_msvcr': True,
    "excludes": [
        "PyQt6.QtNetwork",
        "PyQt6.QtMultimedia",
        "PyQt6.QtBluetooth",
    ],
}

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",  # Shortcut
     "DesktopFolder",  # Directory_
     "pyJTT",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]pyjtt.exe",  # Target
     None,  # Arguments
     None,  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     None,  # ShowCmd
     '%APPDATA%\pyjtt'  # WkDir
     ),
    ("ProgramMenuShortcut",  # Shortcut
     "ProgramMenuFolder",  # Directory_
     "pyJTT",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]pyjtt.exe",  # Target
     None,  # Arguments
     None,  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     None,  # ShowCmd
     '%APPDATA%\pyjtt'  # WkDir
     )]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the
# use of the above defined tables
bdist_msi_options = {'data': msi_data}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    options["build_exe"] = build_exe_options
    options["bdist_msi"] = bdist_msi_options
elif sys.platform == "darwin":
    bdist_mac_options = {
        "bundle_name": "pyJTT",
        "iconfile": "resources/icons/icon.icns",
        "include_resources": [
            ("resources/icons/start.ico", "resources/icons/start.ico"),
            ("resources/icons/stop.ico", "resources/icons/stop.ico"),
            ("resources/icons/icon-tray.png", "resources/icons/icon-tray.png"),
        ]
    }
    codesign_identity = os.environ.get("PYJTT_CODESIGN_IDENTITY")
    if codesign_identity:
        bdist_mac_options["codesign_identity"] = codesign_identity
    codesign_entitlements = os.environ.get("PYJTT_CODESIGN_ENTITLEMENTS")
    if codesign_entitlements:
        bdist_mac_options["codesign_entitlements"] = codesign_entitlements
    codesign_resource_rules = os.environ.get("PYJTT_CODESIGN_RESOURCE_RULES")
    if codesign_resource_rules:
        bdist_mac_options["codesign_resource_rules"] = codesign_resource_rules
    options["bdist_mac"] = bdist_mac_options


target_app = os.path.join("pyjtt", "app.py")

setup(name="pyjtt",
      version="1.2.4",
      description="Jira Time Tracker",
      maintainer="Nikolai Golub",
      maintainer_email="nikolay.v.golub@gmail.com",
      long_description="Allows track time in JIRA online and manage worklogs",
      license="GNU GENERAL PUBLIC LICENSE Version 3",
      options=options,
      executables=[Executable(target_app,
                              base=base,
                              targetName="pyjtt.exe",
                              icon=icon_path,
                              shortcutName="pyJTT",
                              shortcutDir="DesktopFolder")])
