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
import sys
import configparser
import logging
import logging.handlers
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QApplication, QDialog

import gui
import utils

LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s@%(thread)d - %(message)s'
CONFIG_FILENAME = 'pyjtt.cfg'


def init_config(workdir):
    """
    Prepares config class for usage
    """
    defaults = {'log_level': 'INFO'}
    for item in ('jirahost', 'login', 'password', 'save_password'):
        defaults[item] = ''

    config_filename = path.join(workdir, CONFIG_FILENAME)
    config = configparser.ConfigParser(defaults=defaults)
    config.read(config_filename)

    if not config.has_section('main'):
        config.add_section('main')
    return config


def main():
    """
    Application entry point
    """
    workdir = utils.get_app_working_dir()
    if not path.isdir(workdir):
        mkdir(workdir)

    config = init_config(workdir)
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

    def app_quit():
        """
        Standard procedures before close application
        """
        with open(path.join(workdir, CONFIG_FILENAME), 'w') as configfile:
            config.write(configfile)
        app.quit()
        sys.exit(app.exec_())
    jira_host = config.get('main', 'jirahost')
    login = config.get('main', 'login')
    password = config.get('main', 'password')
    if any([x == '' for x in (jira_host, login, password)]):
        login_window = gui.LoginWindow(jira_host,
                                       login,
                                       password,
                                       bool(config.get('main', 'save_password')),)
        login_window.show()
        login_result = login_window.exec_()
        if login_result == QDialog.Accepted:
            jira_host = login_window.ui.lineEditHostAddress.text()
            login = login_window.ui.lineEditLogin.text()
            password = login_window.ui.lineEditPassword.text()

            config.set('main', 'jirahost', jira_host)
            config.set('main', 'login', login)

            if login_window.ui.checkBoxSaveCredentials.isChecked():
                config.set('main', 'password', password)
        else:
            app_quit()
    main_window = gui.MainWindow(jira_host, login, password)
    main_window.show()

    app_quit()


if __name__ == '__main__':
    main()