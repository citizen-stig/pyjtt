#!/usr/bin/env python
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import os, sys, logging
import db, utils, rest_wrapper, pyjtt
import login_screen, main_window

from PyQt4 import QtCore, QtGui


class LoginForm(QtGui.QDialog):
    def __init__(self, config_filename, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.config_filename = config_filename
        self.ui = login_screen.Ui_loginWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.handle_login)
        self.ui.buttonBox.rejected.connect(self.user_exit)

    def handle_login(self):
        # user interaction
        self.jira_host = str(self.ui.lineEditHostAddress.text())
        self.login = str(self.ui.lineEditLogin.text())
        self.password =  str(self.ui.lineEditPassword.text())
        if not self.jira_host:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter jira Host address')
        elif not self.login:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter login')
        elif not self.password:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Enter password')
        else:
            # TODO: add test request of user name for checking correct password
            if self._login(self.login, self.password, self.jira_host):
                self.accept()

    def user_exit(self):
        self.reject()

    def _login(self, login, password, jirahost):
        logging.debug('Trying to get user info')
        try:
            user_info = rest_wrapper.JiraUser(str(jirahost), str(login), str(password))
            logging.debug('Login successful')
            # TODO: add saving user info
            print self.ui.checkBoxSaveCredentials.isChecked()
            if self.ui.checkBoxSaveCredentials.isChecked():
                logging.debug('Saving Credentials')
                utils.save_settings(self.config_filename, (jirahost,  login, password))
            return True
        except rest_wrapper.urllib2.HTTPError as e:
            if e.code == 401:
                QtGui.QMessageBox.warning(self, 'Login Error', 'Wrong login or password')
            elif e.code == 403:
                QtGui.QMessageBox.warning(self, 'Login Error', 'Error %s %s. Try to login via Web' % (str(e.code), e.reason) )
            else:
                QtGui.QMessageBox.warning(self, 'Login Error', 'Error: %s - %s' % (str(e.code), e.reason))
        except rest_wrapper.urllib2.URLError as ue:
            QtGui.QMessageBox.warning(self, 'Login Error', 'Wrong jira url')


class MainWindow(QtGui.QMainWindow):
    def __init__(self, jirahost, login, password, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.jira_issues = {}

        local_db_name = utils.get_db_filename(login, jirahost)
        if not os.path.isfile(local_db_name):
            logging.debug('Local DB does not exist. Creating local database')
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
            self._refresh_issues_table()
        logging.debug('Issues have been loaded')
        self.creds = ( str(jirahost), str(login), str(password), db_conn, cursor )

        # add issue
        self.ui.AddIssue.clicked.connect(self._get_issue)

        # TODO: add event for filtering issues in table, when user enters key

    def _get_issue(self):
        logging.debug('Get issue button has been clicked')
        issue_key = str(self.ui.lineIssueKey.text())
        if issue_key and issue_key not in self.jira_issues:
            issue = pyjtt.get_issue_from_jira(self.creds, issue_key)
            self.jira_issues[issue_key] = issue
            logging.debug('Issue has been added')
            self._refresh_issues_table()
        self.ui.lineIssueKey.clear()

    def _refresh_issues_table(self):
        logging.debug('Refreshing table')
        self.ui.tableIssues.setRowCount(len(self.jira_issues))
        row = 0
        for issue_key in sorted(self.jira_issues.keys()):
            print issue_key, self.jira_issues[issue_key].summary
            self.ui.tableIssues.setItem(row, 0, QtGui.QTableWidgetItem(issue_key))
            self.ui.tableIssues.setItem(row, 1, QtGui.QTableWidgetItem(self.jira_issues[issue_key].summary))
            self.ui.tableIssues.setItem(row, 2, QtGui.QTableWidgetItem('N/A'))
            row += 1
        logging.debug('Table refresh has been completed')


    def __del__(self):
        # TODO: if creds is not defined yet
        pyjtt.normal_exit(self.creds[3])

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    logging.debug('Starting')

    # base constants
    app = QtGui.QApplication(sys.argv)
    config_filename = 'pyjtt.cfg'

    if not os.path.isfile(config_filename):
        login_window = LoginForm(config_filename)
        login_window.show()
        if login_window.exec_() == QtGui.QDialog.Accepted:
            logging.debug('Login successful')
            jirahost = login_window.jira_host
            login = login_window.login
            password = login_window.password
        else:
            logging.info('Exit')
            #TODO: add exit code, but without freezing
            sys.exit()
    else:
        logging.debug('Config file exists, reading settings')
        jirahost, login, password = utils.get_settings(config_filename)

    logging.debug('Start Main Application')
    pyjtt_main_window = MainWindow(jirahost, login, password)
    pyjtt_main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()