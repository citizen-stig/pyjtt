#!/usr/bin/env python
import os
from os import path, mkdir
import sys

import logging
import logging.handlers
import pathlib

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import QtCore, QtGui

import gui
import utils

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"

logger = logging.getLogger(__name__)

LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s@%(thread)d - %(message)s'


def main():
    """
    Application entry point
    """
    workdir = utils.get_app_working_dir()
    if not path.isdir(workdir):
        mkdir(workdir)

    resources_path1 = os.path.normpath(os.path.join(
        pathlib.Path(__file__).parent, '..', 'resources')
    )

    resources_path2 = os.path.normpath(os.path.join(
        pathlib.Path(__file__).parent, 'resources')
    )
    print(resources_path1)
    # icons = os.path.join(resources_path, 'icons')
    # resources_qdri = QtCore.QDir(resources_path)
    # QtCore.QDir.addSearchPath('icons', icons)
    # QtCore.QDir.addSearchPath('', resources_path)
    QtCore.QDir.setSearchPaths('resources', [resources_path1, resources_path2])
    # QtCore.QDir.setSearchPaths('icons', [resources_path1, resources_path2])

    # print("Check")
    # print(QtCore.QDir.searchPaths('resources'))


    # print(QtCore.QDir.exists(resources_path))

    config = utils.init_config()

    # Initialize logging
    log_filename = path.join(workdir, 'application.log')
    log_rotater = logging.handlers.RotatingFileHandler(log_filename,
                                                       mode='a',
                                                       encoding='utf-8',
                                                       maxBytes=10485760,
                                                       backupCount=5)
    logging.basicConfig(format=LOGGING_FORMAT,
                        level=config.get('main', 'log_level'),
                        handlers=(log_rotater,))
    app = QApplication([])

    # qPixMap = QtGui.QPixmap("../resources/icons/icon.png")
    # print(qPixMap)
    # print(qPixMap.isNull())
    # print(qPixMap.size().width())
    # print(qPixMap.size().height())

    jira_host = config.get('main', 'jirahost')
    login = config.get('main', 'login')
    password = config.get('main', 'password')
    if any([x == '' for x in (jira_host, login, password)]):
        login_window = gui.LoginWindow(
            jira_host,
            login,
            password,
            bool(config.get('main', 'save_password')))
        login_window.show()
        login_result = login_window.exec()
        if login_result == QDialog.DialogCode.Accepted:
            jira_host = login_window.ui.lineEditHostAddress.text()
            login = login_window.ui.lineEditLogin.text()
            password = login_window.ui.lineEditPassword.text()

            config.set('main', 'jirahost', jira_host)
            config.set('main', 'login', login)

            if login_window.ui.checkBoxSaveCredentials.isChecked():
                config.set('main', 'password', password)
            utils.write_config(config)
            main_window = gui.MainWindow(jira_host, login, password)
            main_window.show()
            sys.exit(app.exec())
    else:
        main_window = gui.MainWindow(jira_host, login, password)
        main_window.show()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()
