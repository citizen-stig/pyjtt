#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# This file is part of PyJTT.
#
#    PyJTT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    PyJTT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyJTT.  If not, see <http://www.gnu.org/licenses/>.
#
#    This is module with a small utils functions


__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2014, Nikolay Golub"
__license__ = "GPL"


from os import path, mkdir
import logging
logger = logging.getLogger(__name__)
import sys
import configparser

from PyQt5.QtWidgets import QApplication, QDialog

import gui
import utils

LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s - %(message)s'


def main():
    # obtain application folder
    workdir = utils.get_app_working_dir()
    if not path.isdir(workdir):
        mkdir(workdir)
    print(workdir)
    # obtain configuration
    config_filename = path.join(workdir, 'pyjtt.cfg')
    config = configparser.ConfigParser()
    config.read(config_filename)
    # Configure logging

    logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)
    # initialize Qt application
    app = QApplication([])
    # Checking credentials
    login_form = gui.LoginForm('https://complexis.atlassian.net/',
                               'golub',
                               'lv4FZV65-trp',
                               False)
    login_form.show()
    if login_form.exec_() == QDialog.Accepted:
        jira_host = login_form.ui.lineEditHostAddress.text()
        login = login_form.ui.lineEditLogin.text()
        password = login_form.ui.lineEditPassword.text()
        if login_form.ui.checkBoxSaveCredentials.isChecked():
            # TODO: add saving credentials
            pass
    else:
        print('Exit motherfucker')
        sys.exit(app.exec_())
    # Initialize main window
    main_window = gui.MainWindow(jira_host, login, password)
    main_window.show()
    # exit application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()