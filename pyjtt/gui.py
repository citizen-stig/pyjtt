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

from datetime import timedelta
import queue
from urllib import error
from functools import partial
import logging
logger = logging.getLogger(__name__)

from PyQt5 import QtWidgets, QtCore

import core
import utils
import workers
from widgets import login_window, main_window, worklog_window


class LoginForm(QtWidgets.QDialog):

    def __init__(self,
                 jirahost,
                 login,
                 password,
                 save_credentials,
                 parent=None):
        super(LoginForm, self).__init__(parent)
        self.ui = login_window.Ui_loginWindow()
        self.ui.setupUi(self)

        if jirahost:
            self.ui.lineEditHostAddress.setText(jirahost)
        if login:
            self.ui.lineEditLogin.setText(login)
        if password:
            self.ui.lineEditPassword.setText(password)
        if save_credentials:
            self.ui.checkBoxSaveCredentials.setCheckState(save_credentials)

        self.ui.buttonBox.accepted.connect(self.handle_login_input)
        self.ui.buttonBox.rejected.connect(self.user_exit)

    def handle_login_input(self):
        # user interaction
        jira_host = str(self.ui.lineEditHostAddress.text())
        login = str(self.ui.lineEditLogin.text())
        password = str(self.ui.lineEditPassword.text())
        if not jira_host:
            QtWidgets.QMessageBox.warning(self, 'Login error', 'Enter JIRA host address')
        elif not login:
            QtWidgets.QMessageBox.warning(self, 'Login error', 'Enter login')
        elif not password:
            QtWidgets.QMessageBox.warning(self, 'Login error', 'Enter password')
        else:
            logger.debug('Starting Login')
            if self._login(jira_host, login, password):
                self.accept()

    def user_exit(self):
        self.reject()

    def _login(self, jira_host, login, password):
        logger.debug('Trying to get user info')
        try:
            app = core.TimeTrackerApp(jira_host, login, password)
            app.get_user_info()
            return True
        except error.HTTPError as http_error:
            # TODO: add dict with advices, based on return code
            QtWidgets.QMessageBox.warning(self, 'Login Error',
                                          'Error %s %s. Try to login via Web'
                                          % (str(http_error.code), http_error.reason))


class MainWindow(QtWidgets.QMainWindow):
    ui = main_window.Ui_MainWindow()
    number_of_workers = 10
    tasks_queue = queue.Queue()

    def __init__(self, jirahost, login, password, parent=None):
        super(MainWindow, self).__init__()
        self.init_ui()

        # Initialize app
        self.app = core.TimeTrackerApp(jirahost, login, password)

        # Initialize workers
        self.worker_threads = []
        for i in range(self.number_of_workers):
            worker = workers.NoResultThread(self.tasks_queue)
            self.worker_threads.append(worker)
            worker.start()
            worker.task_started.connect(self.inc_status)
            worker.task_done.connect(self.refresh_ui)
            worker.task_done.connect(self.dec_status)
            worker.exception_raised.connect(self.show_error)
        self.tracking_thread = workers.TrackingWorker()
        self.tracking_thread.start()

        # Signals
        self.ui.FindIssue.clicked.connect(self.get_issue)
        self.ui.lineIssueKey.returnPressed.connect(self.get_issue)
        self.ui.tableIssues.clicked.connect(self.set_issue_selected)
        self.ui.dateDayWorklogEdit.dateChanged.connect(self.print_worklog_table)
        self.ui.actionReresh_issue.triggered.connect(self.refresh_issue)

        # Request assigned issues
        get_assigned_issues_job = partial(self.app.get_user_assigned_issues)
        self.tasks_queue.put(get_assigned_issues_job)

    # Names convention:
    # Underscore for auxiliary methods which aren't called by singals

    # Core stuff
    def closeEvent(self, event):
        for thread in self.worker_threads:
            thread.quit()
        self.tracking_thread.quit()
        event.accept()

    def _extract_issue_from_table(self):
        if self.ui.tableIssues.selectedItems():
            selected_indexes = self.ui.tableIssues.selectedIndexes()
            container_coordinates = selected_indexes[0]
            issue_container = self.ui.tableIssues.item(container_coordinates.row(),
                                                       container_coordinates.column())
            issue = issue_container.issue
            return issue
        else:
            QtWidgets.QMessageBox.warning(self,
                                          'Refresh error',
                                          'Please, select issue first')

    def get_issue(self):
        issue_keys = str(self.ui.lineIssueKey.text())
        for issue_key in issue_keys.split(','):
            issue_key = issue_key.strip().upper()
            if utils.check_jira_issue_key(issue_key):
                get_issue_task = partial(self.app.get_issue, issue_key)
                self.tasks_queue.put(get_issue_task)
        self.ui.lineIssueKey.clear()

    def refresh_issue(self):
        if not self.ui.tableIssues.isHidden():
            issue = self._extract_issue_from_table()
            refresh_job = partial(self.app.refresh_issue, issue)
            self.tasks_queue.put(refresh_job)
        else:
            #TODO: add extraction from worklog table
            pass

    # GUI stuff
    def init_ui(self):
        """Method for UI customization"""
        self.ui.setupUi(self)
        self.ui.dateDayWorklogEdit.setDate(QtCore.QDate.currentDate())

    def refresh_ui(self):
        self.print_issues_table()
        self.print_worklog_table()

    def show_error(self, exception):
        logger.error(str(exception))
        info_msg = 'Error appears:\n'
        info_msg += str(exception)
        QtWidgets.QMessageBox.warning(self, 'Warning', info_msg)

    def inc_status(self):
        self.ui.statusbar.showMessage('Synchronizing...')

    def dec_status(self):
        if self.tasks_queue.empty():
            self.ui.statusbar.clearMessage()

    def print_issues_table(self):
        logger.debug('Refreshing issues table')
        issues = self.app.get_all_issues()
        self.ui.tableIssues.setRowCount(len(issues))
        self.ui.tableIssues.setSortingEnabled(False)
        for row_num, issue in enumerate(issues):
            table_item = QtWidgets.QTableWidgetItem(issue.key)
            table_item.issue = issue
            self.ui.tableIssues.setItem(row_num, 0, table_item)
            self.ui.tableIssues.setItem(row_num, 1, QtWidgets.QTableWidgetItem(issue.summary))
        self.ui.tableIssues.resizeColumnToContents(0)
        self.ui.tableIssues.sortByColumn(0, 0)
        self.ui.tableIssues.setSortingEnabled(True)
        logger.debug('Issues table was refreshed')

    def print_worklog_table(self):
        selected_day = self.ui.dateDayWorklogEdit.date().toPyDate()
        day_worklog = self.app.get_day_worklog(selected_day)
        day_total = timedelta(seconds=0)

        self.ui.tableDayWorklog.setSortingEnabled(False)
        self.ui.tableDayWorklog.setRowCount(len(day_worklog))
        for row_num, worklog_entry in enumerate(day_worklog):
            issue_key_item = QtWidgets.QTableWidgetItem(worklog_entry.issue.key)
            issue_key_item.worklog_entry = worklog_entry
            self.ui.tableDayWorklog.setItem(row_num,
                                            0,
                                            issue_key_item)
            self.ui.tableDayWorklog.setItem(row_num,
                                            1,
                                            QtWidgets.QTableWidgetItem(worklog_entry.issue.summary))
            started_item = QtWidgets.QTableWidgetItem(worklog_entry.started.strftime('%H:%M'))
            started_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.ui.tableDayWorklog.setItem(row_num,
                                            2,
                                            started_item)
            ended_item = QtWidgets.QTableWidgetItem(worklog_entry.ended.strftime('%H:%M'))
            ended_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.ui.tableDayWorklog.setItem(row_num,
                                            3,
                                            ended_item)
            time_spent_item = QtWidgets.QTableWidgetItem(worklog_entry.get_timespent_string())
            time_spent_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.ui.tableDayWorklog.setItem(row_num,
                                            4,
                                            time_spent_item)
            day_total += worklog_entry.get_timespent()

        if day_total.total_seconds() > 0:
            self.ui.labelDaySummary.setText('Total:' + utils.get_time_spent_string(day_total))
        else:
            self.ui.labelDaySummary.clear()
        # restore sorting
        self.ui.tableDayWorklog.sortByColumn(2, QtCore.Qt.AscendingOrder)
        self.ui.tableDayWorklog.setSortingEnabled(True)
        # beautifying
        self.ui.tableDayWorklog.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        for column in (0, 2, 3, 4):
            self.ui.tableDayWorklog.resizeColumnToContents(column)
            self.ui.tableDayWorklog.horizontalHeader().setSectionResizeMode(column,
                                                                            QtWidgets.QHeaderView.Fixed)
            self.ui.tableDayWorklog.horizontalHeader().setSectionResizeMode(column,
                                                                            QtWidgets.QHeaderView.Fixed)

    def set_issue_selected(self):
        if not self.ui.startStopTracking.isChecked():
            if not self.ui.tabIssues.isHidden():
                issue = self._extract_issue_from_table()
                self.ui.labelSelectedIssue.setText(issue.key + ': ' + issue.summary)

