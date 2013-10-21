#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#    This is main module of PyJTT. It starts GUI application and manage all
#    other modules.
#

from __future__ import unicode_literals

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2013, Nikolay Golub"
__license__ = "GPL"

import os
import sys
import start
import datetime
import time
from functools import partial
from PyQt4 import QtCore, QtGui
from urllib2 import URLError
import Queue

import custom_logging
logger = custom_logging.get_logger()
import db
import utils
import rest_wrapper
import core
from gui import login_screen, main_window, worklog_window


def datetime_to_qtime(timestamp):
    """Converts Qtime timestamp to Python datetime"""
    return QtCore.QTime(timestamp.hour, timestamp.minute)


class BaseThread(QtCore.QThread):
    """Base class for thread in pyjtt. Not used directly"""
    exception_raised = QtCore.pyqtSignal(Exception)
    status_sent = QtCore.pyqtSignal(str)
    status_cleared = QtCore.pyqtSignal()

    def __init__(self, queue, parent=None):
        """Initializes queue and statuses.

        queue variable is a list of functions, which should be run in thread.
        statuses variable is a list of strings, that should be shown as status.
        indexes of queue and status should correspond to each other.
        Each function should have a status message (at least empty)
        """
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        #self.queue = deque()
        #self.statuses = deque()

    def _run(self, func):
        """Should be implemented in child classees."""
        pass

    def run(self):
        """Prepares execution and handles status messages."""
        while True:
            try:
                f, msg = self.queue.get()
                self.status_sent.emit(msg)
                self._run(f)
            except Queue.Empty:
                pass
            except Exception as exc:
                self.exception_raised.emit(exc)
            finally:
                self.status_cleared.emit()
                self.queue.task_done()
                time.sleep(0.2)


class ResultThread(BaseThread):
    """This thread executed functions, which returns result(JIRAIssue object)"""
    issue_get = QtCore.pyqtSignal(rest_wrapper.JIRAIssue)
    issue_removed = QtCore.pyqtSignal(str)

    def __init__(self, queue, parent=None):
        logger.info('Initialize result thread')
        BaseThread.__init__(self, queue, parent)
        logger.debug('Result thread has been initialized')

    def _run(self, func):
        logger.debug('Start I/O function with result')
        result = func()
        if isinstance(result, core.JIRAIssue):
            self.issue_get.emit(result)
        elif isinstance(result, str):
            self.issue_removed.emit(result)


class IOThread(BaseThread):
    """Simple thread for I/O operations which don't return anything"""
    done = QtCore.pyqtSignal()

    def __init__(self, queue, parent=None):
        logger.info('Initialize simple I/O thread')
        BaseThread.__init__(self, queue, parent)
        logger.debug('I/O thread initialized')

    def _run(self, func):
        logger.debug('Start I/O function')
        func()
        self.done.emit()


class TimeWorker(QtCore.QThread):
    """Thread for tracking timer.

    It is created when time starts and ended when timer stops.
    It wakes up every 500 ms
    """
    timer_updated = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        logger.debug('Initialize timer')
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.delta = 0

    def run(self):
        logger.info('Start tracking timer')
        self.started = datetime.datetime.now()
        while not self.exiting:
            self.current = datetime.datetime.now()
            self.delta = int(round((self.current -
                                    self.started).total_seconds()))
            self.timer_updated.emit(self.delta)
            time.sleep(0.5)

    def __del__(self):
        logger.info("Stop tracking timer")
        self.exiting = True
        self.wait()


class WorklogWindow(QtGui.QDialog):
    """Widget for working with worklog data.

    It allows to set date, time ranges and comment to JIRA worklog
    """
    def __init__(self, title, issue_key, summary, selected_date,
                 start_time=None, end_time=None, comment=None, parent=None):
        logger.debug('Opening worklog window')
        QtGui.QWidget.__init__(self, parent)
        self.ui = worklog_window.Ui_WorklogWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.labelIssue.setText(issue_key + ': ' + summary)
        self.ui.dateEdit.setDate(selected_date)
        if start_time and end_time:
            self.ui.timeStartEdit.setTime(datetime_to_qtime(start_time))
            self.ui.timeEndEdit.setTime(datetime_to_qtime(end_time))
        else:
            current_hour = QtCore.QTime.currentTime().hour()
            self.ui.timeStartEdit.setTime(QtCore.QTime(current_hour - 2, 0) )
            self.ui.timeEndEdit.setTime(QtCore.QTime(current_hour, 0) )
        if comment:
            self.ui.plainTextCommentEdit.setPlainText(comment)

        self._refresh_spent()
        self.ui.timeStartEdit.timeChanged.connect(self._start_time_changed)
        self.ui.timeEndEdit.timeChanged.connect(self._end_time_changed)
        self.ui.buttonBox.accepted.connect(self._save_worklog_data)
        self.ui.buttonBox.rejected.connect(self._user_exit)

    def _start_time_changed(self):
        if self.ui.timeStartEdit.time() >= self.ui.timeEndEdit.time():
            combine = datetime.datetime.combine
            today = datetime.date.today
            start_time = (combine(today(),  self.ui.timeEndEdit.time().toPyTime())
                          - datetime.timedelta(minutes=1)).time()
            self.ui.timeStartEdit.setTime(datetime_to_qtime(start_time))
        self._refresh_spent()

    def _end_time_changed(self):
        if self.ui.timeStartEdit.time() >= self.ui.timeEndEdit.time():
            combine = datetime.datetime.combine
            today = datetime.date.today
            end_time = (combine(today(), self.ui.timeStartEdit.time().toPyTime())
                          + datetime.timedelta(minutes=1)).time()
            self.ui.timeEndEdit.setTime(datetime_to_qtime(end_time))
        self._refresh_spent()

    def _save_worklog_data(self):
        # filter_issues_table
        logger.debug('Saving worklog')
        combine = datetime.datetime.combine
        date = self.ui.dateEdit.date().toPyDate()
        start = self.ui.timeStartEdit.time().toPyTime()
        end = self.ui.timeEndEdit.time().toPyTime()
        self.start_time = combine(date, start)
        self.end_time = combine(date, end)
        self.comment = str(self.ui.plainTextCommentEdit.toPlainText())
        self.accept()
        logger.debug('Worklog saved')

    def _user_exit(self):
        self.reject()

    def _refresh_spent(self):
        logger.debug('Refresh time spent')
        spent = 'Time spent: ' + \
                utils.get_time_spent_string(self.ui.timeEndEdit.dateTime().toPyDateTime() - \
                                            self.ui.timeStartEdit.dateTime().toPyDateTime())
        self.ui.labelSpent.setText(spent)
        logger.debug('Time spent is refreshed')


class LoginForm(QtGui.QDialog):
    def __init__(self, jirahost=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = login_screen.Ui_loginWindow()
        self.save_credentials = False
        self.ui.setupUi(self)
        if jirahost:
            self.ui.lineEditHostAddress.setText(jirahost)
        self.ui.buttonBox.accepted.connect(self.handle_login)
        self.ui.buttonBox.rejected.connect(self.user_exit)

    def handle_login(self):
        # user interaction
        self.jira_host = str(self.ui.lineEditHostAddress.text())
        self.login = str(self.ui.lineEditLogin.text())
        self.password = str(self.ui.lineEditPassword.text())
        if not self.jira_host:
            QtGui.QMessageBox.warning(self, 'Login error',
                                      'Enter JIRA host address')
        elif not self.login:
            QtGui.QMessageBox.warning(self, 'Login error', 'Enter login')
        elif not self.password:
            QtGui.QMessageBox.warning(self, 'Login error', 'Enter password')
        else:
            logger.debug('Starting Login')
            if utils.check_url_host(self.jira_host):
                if self._login(self.login, self.password, self.jira_host):
                    self.accept()
            else:
                QtGui.QMessageBox.warning(self, 'Login error',
                                          'Host is unavailable or'
                                          'internet connection is too bad')
            logger.debug('Ending Login')

    def user_exit(self):
        self.reject()

    def _login(self, login, password, jirahost):
        logger.debug('Trying to get user info')
        try:
            rest_wrapper.JiraUser(str(jirahost), str(login),
                                              str(password))
            logger.debug('Login successful')
            if self.ui.checkBoxSaveCredentials.isChecked():
                self.save_credentials = True
            return True
        except rest_wrapper.urllib2.HTTPError as e:
            if e.code == 401:
                QtGui.QMessageBox.warning(self, 'Login error',
                                          'Wrong login or password')
            elif e.code == 403:
                QtGui.QMessageBox.warning(self, 'Login error',
                                          'Error %s %s. Try to login via Web'
                                          % (str(e.code), e.reason))
            else:
                QtGui.QMessageBox.warning(self, 'Login error',
                                          'Error: %s - %s' % (str(e.code),
                                                              e.reason))
        except rest_wrapper.urllib2.URLError:
            QtGui.QMessageBox.warning(self, 'Login error',
                                      'Wrong jira URL')
        except ValueError as val_err:
            QtGui.QMessageBox.warning(self, 'Login error',
                                      '"%s" \nProbably JIRA doesn\'t respond ' % val_err.message)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, jirahost, login, password, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._init_ui()
        # Main dictionary, contains JIRAIssue objects, key is JIRA issue key
        self.jira_issues = {}
        self.local_db_name = os.path.join(start.get_app_working_dir(),
                                          utils.get_db_filename(login, jirahost)
                                          )
        if not os.path.isfile(self.local_db_name):
            logger.debug('Local DB does not exist. Creating local database')
            db.create_local_db(self.local_db_name)
        else:
            # Need to load issues from db to memory
            raw_issues = db.get_all_issues(self.local_db_name)
            for issue_entry in raw_issues:
                issue = rest_wrapper.JIRAIssue(jirahost, login, password,
                                               issue_entry[1])
                issue.issue_id = issue_entry[0]
                issue.summary = issue_entry[2]
                issue.worklog = db.get_issue_worklog(self.local_db_name,
                                                     issue.issue_id)
                self.jira_issues[issue.issue_key] = issue
        logger.debug('Issues have been loaded')
        # Build tuple with credentials
        self.creds = (str(jirahost), str(login), str(password),
                      self.local_db_name)
        # Get assigned issues keys
        try:
            custom_jql = utils.get_custom_jql()
            self.user = rest_wrapper.JiraUser(self.creds[0],
                                              self.creds[1],
                                              self.creds[2], custom_jql)
            self.user.get_assigned_issues()
        except URLError:
            logger.error('Connection problems')

        self.io_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.status_msg_queue = 0

        # Threads
        num_of_threads = 10
        for i in range(num_of_threads):
            result_thread = ResultThread(self.result_queue, parent=self)
            result_thread.start()
            result_thread.exception_raised.connect(self._print_exception)
            result_thread.status_sent.connect(self._set_status_message)
            result_thread.status_cleared.connect(self._clear_status_msg)
            result_thread.issue_get.connect(self._add_issue_to_local)
            result_thread.issue_removed.connect(self._remove_issue_from_local)

            io_thread = IOThread(self.io_queue, parent=self)
            io_thread.start()
            io_thread.exception_raised.connect(self._print_exception)
            io_thread.status_sent.connect(self._set_status_message)
            io_thread.status_cleared.connect(self._clear_status_msg)
            io_thread.done.connect(self._print_day_worklog)

        # SIGNALS
        self.ui.FindIssue.clicked.connect(self.request_for_issue_data)
        self.ui.lineIssueKey.returnPressed.connect(self.request_for_issue_data)
        self.ui.dateDayWorklogEdit.dateChanged.connect(self._print_day_worklog)
        self.ui.editWorklog.clicked.connect(self.change_worklog)
        self.ui.tableDayWorklog.doubleClicked.connect(self.change_worklog)
        self.ui.removeWorklog.clicked.connect(self.remove_worklog)
        self.ui.tableIssues.clicked.connect(self.make_issue_selected)
        self.ui.tableIssues.doubleClicked.connect(self.add_new_worklog)
        self.ui.startStopTracking.clicked.connect(self.online_tracking)
        self.ui.actionReresh_issue.triggered.connect(self.force_update_selected_issue)
        self.ui.actionFull_refresh.triggered.connect(self.force_update_all_issues)
        self.ui.actionRefresh.triggered.connect(self._refresh_gui)
        self.ui.lineIssueKey.textChanged.connect(self.filter_issues_table)
        self.ui.tray_icon.activated.connect(self.tray_click)
        self.ui.app_exit.triggered.connect(self._app_close)
        self.ui.show_window.triggered.connect(self._restore_from_tray)

        # Request assigned issues
        for assigned_issue in self.user.assigned_issue_keys:
            if assigned_issue not in self.jira_issues:
                get_issue_func = partial(core.get_issue_from_jira,
                                         self.creds, assigned_issue)
                logger.debug('Put func to queue')
                self.result_queue.put((get_issue_func,
                                       'Fetching issue from JIRA...'))
        self._refresh_gui()

    # About naming convention:
    # All methods, that handle user input or works with JIRA (prepare request)
    # start with letter. Internal or GUI representation methods started from
    #  underscore

    def _init_ui(self):
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)
        # Issue which is selected by user. It is used in online tracking
        self.selected_issue = None
        self.is_tracking_on = False
        # number of worklog id column, which is hidden from user
        self.worklog_id_column = 5
        # GUI customization
        self.ui.dateDayWorklogEdit.setDate(QtCore.QDate.currentDate())
        # Hide work log id from user
        self.ui.tableDayWorklog.setColumnHidden(self.worklog_id_column, True)
        # Add status bar preferences
        self.ui.spinning_img = QtGui.QMovie(main_window._fromUtf8(
            ":/res/img/spinning-progress.gif"))
        self.ui.spinning_label = QtGui.QLabel()
        self.ui.spinning_label.setMovie(self.ui.spinning_img)
        self.ui.spinning_label.hide()
        self.ui.status_msg = QtGui.QLabel()
        self.ui.statusbar.addWidget(self.ui.spinning_label)
        self.ui.statusbar.addWidget(self.ui.status_msg)
        self.ui.status_msg.hide()
        self.ui.start_icon = QtGui.QIcon()
        self.ui.start_icon.addPixmap(QtGui.QPixmap(main_window._fromUtf8(
            ":/res/icons/start.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.stop_icon = QtGui.QIcon()
        self.ui.stop_icon.addPixmap(QtGui.QPixmap(main_window._fromUtf8(
            ":/res/icons/stop.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.tray_icon = QtGui.QSystemTrayIcon()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(main_window._fromUtf8(":/res/icons/clock.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.tray_icon.setIcon(icon)
        self.ui.tray_icon.show()
        self.ui.tray_menu = QtGui.QMenu()
        self.ui.show_window = self.ui.tray_menu.addAction("pyJTT")
        self.ui.show_window.setDisabled(True)
        self.ui.tray_menu.addSeparator()
        self.ui.app_exit = self.ui.tray_menu.addAction("Exit")
        self.ui.tray_icon.setContextMenu(self.ui.tray_menu)

    def closeEvent(self, event):
        self._hide_to_tray()
        event.ignore()

    def _restore_from_tray(self):
        self.setWindowFlags(QtCore.Qt.Window)
        self.showNormal()
        self.activateWindow()
        self.ui.show_window.setDisabled(True)

    def _hide_to_tray(self):
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui.show_window.setDisabled(False)

    def tray_click(self, reason):
        if reason != QtGui.QSystemTrayIcon.Context:
            if self.isHidden():
                self._restore_from_tray()
            else:
                self._hide_to_tray()

    def _app_close(self):
        info_msg = "Are you sure to quit?"
        was_hidden = False
        if self.isHidden():
            self.setHidden(False)
            was_hidden = True
        reply = QtGui.QMessageBox.question(self,
                                           'Exit',
                                           info_msg,
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
        if was_hidden:
            self.setHidden(True)

    def filter_issues_table(self):
        current_text = self.ui.lineIssueKey.text()
        filtered_issues = dict((k, v) for (k, v) in self.jira_issues.iteritems()
                               if str(current_text).lower() in k.lower() or
                               str(current_text).lower() in v.summary.lower())
        self.ui.tableIssues.setRowCount(len(filtered_issues))
        self._print_issues_table(filtered_issues)

    @staticmethod
    def _get_issue_link_label(issue):
        issue_link = '<a href="' + issue.issue_link + \
                         '"><span style=" text-decoration: underline; color:#0000ff;">'\
                     + issue.issue_key + \
                     '</span></a>'
        issue_link_label = QtGui.QLabel('<qt><html><head/><body><p>' +
                                        issue_link +
                                        '</body></html></qt>')
        issue_link_label.setOpenExternalLinks(True)
        return issue_link_label

    def _print_issues_table(self, issues_dict):
        for row, issue_key in enumerate(sorted(issues_dict.keys())):
            issue_link_label = self._get_issue_link_label(issues_dict[issue_key])
            self.ui.tableIssues.setCellWidget(row, 0, issue_link_label)
            self.ui.tableIssues.\
                setItem(row, 1,
                        QtGui.QTableWidgetItem(issues_dict[issue_key].summary))
        self.ui.tableIssues.resizeColumnToContents(0)
        self.ui.tableIssues.horizontalHeader().\
            setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.tableIssues.horizontalHeader().\
            setResizeMode(0, QtGui.QHeaderView.Fixed)
        self.ui.tableIssues.sortByColumn(0, 0)

    def _print_exception(self, exception):
        logger.error(str(exception))
        info_msg = 'Error appears:\n'
        info_msg += str(exception)
        QtGui.QMessageBox.warning(self, 'Warning', info_msg)

    def _get_selected_issue_details(self):
        """Returns issue key and summary """
        if not self.ui.tabIssues.isHidden():
            table = self.ui.tableIssues
        else:
        #elif self.ui.tabWorklogs.isHidden():
            table = self.ui.tableDayWorklog
        selected_indexes = table.selectedIndexes()
        key_coordinates = selected_indexes[0]
        summary_coordinates = selected_indexes[1]

        doc = QtGui.QTextDocument()
        doc.setHtml(table.cellWidget(key_coordinates.row(),
                                     key_coordinates.column()).text())
        key = str(doc.toPlainText()).strip()
        summary = str(table.item(summary_coordinates.row(),
                                 summary_coordinates.column()).text())
        return key, summary

    def make_issue_selected(self):
        """Makes issue selected on top menu for online tracking."""
        if not self.is_tracking_on:
            label_new_width = self.width() - \
                              (self.ui.startStopTracking.width() + 30)
            issue_key, summary = self._get_selected_issue_details()
            self.ui.labelSelectedIssue.setText(issue_key + ': ' + summary)
            self.ui.labelSelectedIssue.setMaximumWidth(label_new_width)
            self.selected_issue = self.jira_issues[issue_key]
            logger.debug('Now selected issue %s'
                         % str(self.jira_issues[issue_key]))

    def _refresh_issues_table(self):
        """Refreshes issues table GUI"""
        logger.debug('Refreshing issues table')
        self.ui.tableIssues.setRowCount(len(self.jira_issues))
        self._print_issues_table(self.jira_issues)
        logger.debug('Issues table has been refreshed')

    def _print_day_worklog(self):
        """Print worklog entries for selected day"""
        logger.info('Refreshing day worklog table')
        selected_day = self.ui.dateDayWorklogEdit.date().toPyDate()
        day_work = db.get_day_worklog(self.creds[3], selected_day)
        day_summary = datetime.timedelta(seconds=0)
        # preparations
        self.ui.tableDayWorklog.setSortingEnabled(False)

        # (u'PERF-303', u'[SS POD2] 5.10 Migration Environment Issues', datetime.datetime(2012, 12, 28, 8, 59), datetime.datetime(2012, 12, 28, 10, 59))
        # Filling the table started
        self.ui.tableDayWorklog.setRowCount(len(day_work))
        for row, entry in enumerate(day_work):
            if entry[0] not in self.jira_issues:
                # Multithreading handling
                logger.debug('Issue %s is still being proccessed'
                             % str(entry[0]))
                continue
            spent = entry[3] - entry[2]
            day_summary += spent
            issue = self.jira_issues[entry[0]]
            issue_link = self._get_issue_link_label(issue)
            self.ui.tableDayWorklog.setCellWidget(row, 0, issue_link)
            self.ui.tableDayWorklog.setItem(row, 1,
                                            QtGui.QTableWidgetItem(entry[1]))
            self.ui.tableDayWorklog.setItem(row, 2,
                                            QtGui.QTableWidgetItem(entry[2].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 3,
                                            QtGui.QTableWidgetItem(entry[3].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 4,
                                            QtGui.QTableWidgetItem(utils.get_time_spent_string(entry[3] -
                                                                                               entry[2])))
            self.ui.tableDayWorklog.setItem(row, self.worklog_id_column,
                                            QtGui.QTableWidgetItem(str(entry[4])))

        # Filling the table completed
        # Sorting
        self.ui.tableDayWorklog.setSortingEnabled(True)
        self.ui.tableDayWorklog.sortByColumn(2, QtCore.Qt.AscendingOrder)
        # Handle the width
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(1,
                                                                 QtGui.QHeaderView.Stretch)
        for column in (0, 2, 3, 4):
            self.ui.tableDayWorklog.resizeColumnToContents(column)
            self.ui.tableDayWorklog.horizontalHeader().setResizeMode(column,
                                                                     QtGui.QHeaderView.Fixed)
            self.ui.tableDayWorklog.horizontalHeader().setResizeMode(column,
                                                                     QtGui.QHeaderView.Fixed)
        # Print total day work
        if day_summary.total_seconds() > 0:
            self.ui.labelDaySummary.setText('Total: ' +
                                            utils.get_time_spent_string(day_summary))
        else:
            self.ui.labelDaySummary.clear()
        logger.info('Day worklog table has been refreshed')

    def _refresh_gui(self):
        self._refresh_issues_table()
        self._print_day_worklog()

    def get_selected_worklog(self):
        """Returns issue and worklog, which is selected on worklog tab """
        issue_key = self._get_selected_issue_details()[0]
        self.ui.tableDayWorklog.setColumnHidden(self.worklog_id_column, False)
        worklog_id = int(self.ui.tableDayWorklog.selectedItems()[self.worklog_id_column - 1].text()) # - 1 because of issue key is not item it is widget
        self.ui.tableDayWorklog.setColumnHidden(self.worklog_id_column, True)
        return issue_key, worklog_id

    def _set_status_message(self, msg, spin_img=True):
        """Shows status message and spinning image"""
        self.ui.status_msg.setText(msg)
        self.ui.spinning_label.show()
        self.ui.status_msg.show()
        self.ui.spinning_img.start()
        self.status_msg_queue += 1
        logger.debug('Thread queue for a status bar is %d '
                     % self.status_msg_queue)

    def _clear_status_msg(self):
        if self.status_msg_queue == 1:
            #self.ui.status_msg.hide()
            self.ui.status_msg.setText('Synchronized')
            self.ui.spinning_label.hide()
        self.status_msg_queue -= 1
        logger.debug('Thread queue for a status bar is %d '
                     % self.status_msg_queue)

    @staticmethod
    def _format_seconds(seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        time_string = '%02d:%02d:%02d' % (hours, minutes, seconds)
        return time_string

    def _update_timer_label(self, seconds):
        self.ui.labelTimeSpent.setText(self._format_seconds(seconds))

    def request_for_issue_data(self):
        """ Function parses user input from find issue line edit and
        Adds required issues to the pyjtt
        """
        logger.debug('Get issue button has been clicked')
        issue_keys = str(self.ui.lineIssueKey.text())
        logger.debug('Issue keys has red, text is "%s"' % issue_keys)
        for issue_key in issue_keys.split(','):
            issue_key = issue_key.strip().upper()
            logger.debug('issue key is %s' % issue_key)
            if utils.check_jira_issue_key(issue_key) and issue_key not in self.jira_issues:
                logger.debug('Packing the function')
                get_issue_func = partial(core.get_issue_from_jira,
                                         self.creds, issue_key)
                logger.debug('Putting function to the queue')
                self.result_queue.put((get_issue_func,
                                       'Fetching issues ...'))
        self.ui.lineIssueKey.clear()

    def force_update_selected_issue(self):
        """Force request to update issue info

        Useful, when issue data changed outside this program"""
        if self.ui.tabWorklogs.isHidden():
            # we on issues tab
            if len(self.ui.tableIssues.selectedItems()):
                #issue_key = str(self.ui.tableIssues.selectedItems()[0].text())
                issue_key = str(self._get_selected_issue_details()[0])
                self.update_issue_info_from_jira(issue_key)
            else:
                QtGui.QMessageBox.warning(self, 'Tracking Error',
                                          'Please, select issue first')
        if self.ui.tableIssues.isHidden():
            # we on worklogs tab
            if len(self.ui.tableDayWorklog.selectedItems()):
                issue_key = str(self.ui.tableDayWorklog.selectedItems()[0].text())
                self.update_issue_info_from_jira(issue_key)
            else:
                QtGui.QMessageBox.warning(self, 'Tracking Error',
                                          'Please, select issue first')

    def force_update_all_issues(self):
        for issue_key in self.jira_issues.keys():
            self.update_issue_info_from_jira(issue_key)

    def update_issue_info_from_jira(self, issue_key):
        logger.debug('Refreshing issue %s' % str(issue_key))

        self._remove_issue_from_local(issue_key)
        get_issue_func = partial(core.get_issue_from_jira,
                                 self.creds, issue_key)
        self.result_queue.put((get_issue_func, 'Refreshing issue %s ...'
                                           % str(issue_key)))

    def _add_issue_to_local(self, issue):
        logger.debug('Add issue "%s" to memory' % str(issue))
        self.jira_issues[issue.issue_key] = issue
        logger.debug('Issue "%s" has been added to memory' % str(issue))
        self._refresh_gui()

    def _remove_issue_from_local(self, issue_key):
        logger.debug('Remove issue %s from memory' % issue_key)
        del self.jira_issues[str(issue_key)]
        db.remove_issue(self.creds[3], str(issue_key))
        logger.debug('Issue %s has been removed from memory' % issue_key)
        self._refresh_gui()

    def add_new_worklog(self):
        title = 'Add worklog'
        issue_key, summary = self._get_selected_issue_details()
        selected_date = datetime.datetime.now()
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=1)
        self.add_window = WorklogWindow(title, issue_key, summary,
                                        selected_date, start_time=start_time,
                                        end_time=end_time, parent=self)
        self.add_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if self.add_window.exec_() == QtGui.QDialog.Accepted:
            start_time = self.add_window.start_time
            end_time = self.add_window.end_time
            comment = self.add_window.comment
            logger.debug('From user: %s, %s, %s' % (str(start_time),
                                                    str(end_time), comment))
            stat_message = 'Adding worklog for issue %s' % str(issue_key)
            self._push_task_to_io_threads(core.add_worklog,
                                          stat_message,
                                          self.creds,
                                          self.jira_issues[issue_key],
                                          start_time,
                                          end_time, comment)

    def change_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self.get_selected_worklog()
            title = 'Edit worklog'
            summary = self.jira_issues[issue_key].summary
            start_time = self.jira_issues[issue_key].worklog[worklog_id][0]
            end_time = self.jira_issues[issue_key].worklog[worklog_id][1]
            comment = self.jira_issues[issue_key].worklog[worklog_id][2]
            selected_date = self.jira_issues[issue_key].worklog[worklog_id][0]
            self.edit_window = WorklogWindow(title, issue_key, summary,
                                             selected_date,
                                             start_time=start_time,
                                             end_time=end_time, comment=comment,
                                             parent=self)
            self.edit_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            if self.edit_window.exec_() == QtGui.QDialog.Accepted:
                new_start_time = self.edit_window.start_time
                new_end_time = self.edit_window.end_time
                new_comment = self.edit_window.comment
                logger.debug('From user: %s, %s, %s' % (str(new_start_time),
                                                        str(new_end_time),
                                                        new_comment))
                stat_message = 'Edit worklog in issue %s' % str(issue_key)
                self._push_task_to_io_threads(core.update_worklog, stat_message,
                               self.creds, self.jira_issues[issue_key],
                               worklog_id, new_start_time, new_end_time,
                               new_comment)
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select worklog first')

    def remove_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self.get_selected_worklog()
            title = 'Remove worklog'
            remove_msg = "Are you sure you want to remove this worklog?"
            reply = QtGui.QMessageBox.question(self, title, remove_msg,
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                stat_message = 'Removing worklog in issue %s' % issue_key
                self._push_task_to_io_threads(core.remove_worklog, stat_message, self.creds,
                               self.jira_issues[issue_key], worklog_id)
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error',
                                      'Please, select worklog first')

    def _push_task_to_io_threads(self, func, msg, *args):
        single = False  # TODO: debug, remove it
        logger.debug('Packing function')
        io_func = partial(func, *args)
        # TODO: debug remove it
        if single:
            io_func()
            self._print_day_worklog()
        else:
            logger.debug('Adding function to queue')
            self.io_queue.put((io_func, msg))

    def online_tracking(self):
        if self.selected_issue:
            if self.ui.startStopTracking.isChecked():
                self.ui.startStopTracking.setIcon(self.ui.stop_icon)
                self.ui.startStopTracking.setText('Stop Tracking')
                self.is_tracking_on = True
                self.tracking_thread = TimeWorker()
                self.tracking_thread.timer_updated.connect(self._update_timer_label)
                self.tracking_thread.start()
            else:
                if self.tracking_thread.delta > 300:
                    info_msg = """Do you want to add this worklog:
                    Issue: %s
                    Started: %s
                    Ended: %s
                    Time spent: %s
                    """ % (self.selected_issue.issue_key,
                           str(self.tracking_thread.started),
                           str(self.tracking_thread.current),
                           utils.get_time_spent_string(self.tracking_thread.current -
                                                       self.tracking_thread.started))
                    reply = QtGui.QMessageBox.question(self, 'Add worklog',
                                                       info_msg,
                                                       QtGui.QMessageBox.Yes,
                                                       QtGui.QMessageBox.No,
                                                       QtGui.QMessageBox.Cancel)
                    if reply == QtGui.QMessageBox.Yes:
                        logger.debug('From GUI: %s, %s, %s'
                                     % (self.selected_issue.issue_key,
                                        str(self.tracking_thread.started),
                                        str(self.tracking_thread.current)))
                        stat_message = 'Adding worklog for issue %s' \
                                       % str(self.selected_issue.issue_key)
                        self._push_task_to_io_threads(core.add_worklog,
                                                      stat_message,
                                                      self.creds,
                                                      self.selected_issue,
                                                      self.tracking_thread.started,
                                                      self.tracking_thread.current)
                        self._clear_tracking_timer()
                    elif reply == QtGui.QMessageBox.No:
                        self._clear_tracking_timer()
                    else:
                        self.ui.startStopTracking.setChecked(True)
                else:
                    self._clear_tracking_timer()
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error',
                                      'Please, select issue first')
            self.ui.startStopTracking.setChecked(False)

    def _clear_tracking_timer(self):
        self.tracking_thread.terminate()
        self.ui.startStopTracking.setText('Start Tracking')
        self.ui.startStopTracking.setIcon(self.ui.start_icon)
        self.ui.labelTimeSpent.setText('00:00:00')
        self.is_tracking_on = False


def perform_login(jirahost=None):
    login_window = LoginForm(jirahost=jirahost)
    login_window.show()
    if login_window.exec_() == QtGui.QDialog.Accepted:
        logger.debug('Login successful')
        jirahost = login_window.jira_host
        login = login_window.login
        password = login_window.password
        save_credentials = login_window.save_credentials
    else:
        logger.info('Exit')
        #TODO: add exit code, but without freezing
        sys.exit()
    return jirahost, login, password, save_credentials


def main():
    logger.debug('Local GMT offset is %s' % utils.LOCAL_UTC_OFFSET)
    # base constants
    app = QtGui.QApplication(sys.argv)
    workdir = start.get_app_working_dir()
    if not os.path.isdir(workdir):
        logger.debug('First start')
        os.mkdir(workdir)
    config_filename = os.path.join(workdir, 'pyjtt.cfg')
    utils.CONFIG_FILENAME = config_filename
    save_credentials = False
    if not os.path.isfile(config_filename):
        jirahost, login, password, save_credentials = perform_login()
    elif not all(utils.get_settings(config_filename)):
        jirahost, login, password = utils.get_settings(config_filename)
        jirahost, login, password, save_credentials = perform_login(jirahost)
    else:
        logger.debug('Config file exists, reading settings')
        jirahost, login, password = utils.get_settings(config_filename)
    if save_credentials:
        logger.debug('Saving credentials')
        utils.save_settings(config_filename, (jirahost, login, password))
    else:
        utils.save_jirahost(config_filename, jirahost)
    logger.debug('Starting Main Application')
    pyjtt_main_window = MainWindow(jirahost, login, password)
    pyjtt_main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()