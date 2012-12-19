#!/usr/bin/env python
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import os, sys, logging
import db, utils, rest_wrapper, pyjtt
import login_screen, main_window

from PyQt4 import QtCore, QtGui

def login_stub(login, password, jirahost):
    return True


class LoginForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = login_screen.Ui_loginWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.handle_login)
        self.ui.buttonBox.rejected.connect(self.user_exit)

    def handle_login(self):
        self.jira_host = self.ui.lineEditHostAddress.text()
        self.login = self.ui.lineEditLogin.text()
        self.password =  self.ui.lineEditPassword.text()
        if not self.jira_host:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter jira Host address')
        elif not self.login:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter login')
        elif not self.password:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter password')
        else:
            # TODO: add test request of user name for checking correct password
            if login_stub(self.login, self.password, self.jira_host):
                self.accept()
            else:
                QtGui.QMessageBox.warning(self, 'Login Error', 'Wrong credentials')

    def user_exit(self):
        self.reject()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, jirahost, login, password, first_start, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.jira_issues = {}

        if first_start:
            logging.debug('Creating local database')
            db_conn, cursor = db.create_local_db(utils.get_db_filename(login, jirahost))
        else:
            logging.debug('COnnecting to local database')
            db_conn, cursor = db.connect_to_db(utils.get_db_filename(login, jirahost))
            raw_issues = db.get_all_issues(cursor)
            for issue_entry in raw_issues:
                issue = rest_wrapper.JIRAIssue(jirahost, login, password, issue_entry[1])
            issue.issue_id = issue_entry[0]
            issue.summary = issue_entry[2]
            issue.worklog = db.get_issue_worklog(cursor, issue.issue_id)
            self.jira_issues[issue.issue_key] = issue
        logging.debug('Issues have been loaded')
        self.creds = ( jirahost, login, password, db_conn, cursor )

    def __del__(self):
        # TODO: if creds is not defined yet
        pyjtt.normal_exit(self.creds[3])


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    logging.debug('Starting')

    # base constants
    app = QtGui.QApplication(sys.argv)
    config_filename = 'test.cfg'

    if not os.path.isfile(config_filename):
        login_window = LoginForm()
        login_window.show()
        if login_window.exec_() == QtGui.QDialog.Accepted:
            logging.debug('Login successful')
            jirahost = login_window.jira_host
            login = login_window.login
            password = login_window.password
            first_start = True
        else:
            logging.info('Exit')
            #TODO: add exit code, but without freezing
            sys.exit()
    else:
        logging.debug('Read settings')
        jirahost, login, password = utils.get_settings(config_filename)
        first_start = False

    logging.debug('Start Main Application')
    pyjtt_main_window = MainWindow(jirahost, login, password, first_start=first_start)
    pyjtt_main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()