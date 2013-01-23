#!/usr/bin/env python
from __future__ import unicode_literals
import os
import sys
import logging
import datetime
import time
from functools import partial
from collections import deque
from PyQt4 import QtCore, QtGui
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
import db, utils, rest_wrapper, pyjtt
from gui import login_screen, main_window, worklog_window


def datetime_to_qtime(timestamp):
    return QtCore.QTime(timestamp.hour, timestamp.minute)


class BaseThread(QtCore.QThread):
    exception_raised = QtCore.pyqtSignal(Exception)
    status_sent = QtCore.pyqtSignal(str)
    status_cleared = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = deque()
        self.statuses = deque()

    def _run(self, func):
        pass

    def run(self):
        while True:
            if len(self.queue):
                logging.info('Here is a job in queue')
                try:
                    f = self.queue.popleft()
                    msg = self.statuses.popleft()
                    self.status_sent.emit(msg)
                    self._run(f)
                except Exception as exc:
                    self.exception_raised.emit(exc)
                finally:
                    self.status_cleared.emit()
            else:
                time.sleep(0.2)


class ResultThread(BaseThread):
    issue_done = QtCore.pyqtSignal(rest_wrapper.JIRAIssue)

    def __init__(self, parent=None):
        logging.info('Initialize result thread')
        BaseThread.__init__(self, parent)
        logging.debug('Result thread has been initialized')

    def _run(self, func):
        logging.debug('Start I/O function with result')
        result = func()
        self.issue_done.emit(result)


class IOThread(BaseThread):
    done = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        logging.info('Initialize simple I/O thread')
        BaseThread.__init__(self, parent)
        logging.debug('I/O thread initialized')

    def _run(self, func):
        logging.debug('Start I/O function')
        func()
        self.done.emit()


class TimeWorker(QtCore.QThread):
    timer_updated = QtCore.pyqtSignal(int)
    def __init__(self, parent = None):
        logging.debug('Initialize timer')
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def run(self):
        logging.info('Start tracking timer')
        self.start = datetime.datetime.now()
        while not self.exiting:
            self.current = datetime.datetime.now()
            self.delta = int(round((self.current - self.start).total_seconds()))
            self.timer_updated.emit(self.delta)
            time.sleep(0.5)

    def __del__(self):
        logging.info("Stop tracking timer")
        self.exiting = True
        self.wait()


class WorklogWindow(QtGui.QDialog):
    def __init__(self, title, issue_key, summary, selected_date, start_time=None, end_time=None, comment=None, parent=None):
        logging.debug('Opening worklog window')
        QtGui.QWidget.__init__(self, parent)
        self.ui = worklog_window.Ui_WorklogWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.labelIssue.setText(issue_key + ': ' + summary)
        self.ui.dateEdit.setDate(selected_date)
        if  start_time and end_time:
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
            start_time = (combine(datetime.date.today(), self.ui.timeEndEdit.time().toPyTime())
                          - datetime.timedelta(minutes=1)).time()
            self.ui.timeStartEdit.setTime(datetime_to_qtime(start_time))
        self._refresh_spent()

    def _end_time_changed(self):
        if self.ui.timeStartEdit.time() >= self.ui.timeEndEdit.time():
            combine = datetime.datetime.combine
            end_time = (combine(datetime.date.today(), self.ui.timeStartEdit.time().toPyTime())
                          + datetime.timedelta(minutes=1)).time()
            self.ui.timeEndEdit.setTime(datetime_to_qtime(end_time))
        self._refresh_spent()

    def _save_worklog_data(self):
        # test
        logging.debug('Saving worklog')
        combine = datetime.datetime.combine
        date = self.ui.dateEdit.date().toPyDate()
        start = self.ui.timeStartEdit.time().toPyTime()
        end = self.ui.timeEndEdit.time().toPyTime()
        self.start_time = combine(date, start)
        self.end_time = combine(date, end)
        self.comment = str(self.ui.plainTextCommentEdit.toPlainText())
        self.accept()
        logging.debug('Worklog saved')

    def _user_exit(self):
        self.reject()

    def _refresh_spent(self):
        logging.debug('Refresh time spent')
        spent = 'Time spent: ' +\
                utils.get_time_spent_string(self.ui.timeStartEdit.dateTime().toPyDateTime(),
                    self.ui.timeEndEdit.dateTime().toPyDateTime())
        self.ui.labelSpent.setText(spent)
        logging.debug('Time spent is refreshed')


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
            if self._login(self.login, self.password, self.jira_host):
                self.accept()

    def user_exit(self):
        self.reject()

    def _login(self, login, password, jirahost):
        logging.debug('Trying to get user info')
        try:
            user_info = rest_wrapper.JiraUser(str(jirahost), str(login), str(password))
            logging.debug('Login successful')
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

        # Main dictionary, contains JIRAIssue objects, key is JIRA issue key
        self.jira_issues = {}
        # Issue which is selected by user. It isud in online tracking
        self.selected_issue = None
        self.is_tracking_on = False
        # number of worklogid column, which is hidden from user
        self.worklogid_column = 5
        self.local_db_name = utils.get_db_filename(login, jirahost)

        if not os.path.isfile(self.local_db_name):
            logging.debug('Local DB does not exist. Creating local database')
            db.create_local_db(self.local_db_name)
        else:
            # Need to load issueds from db to memory
            raw_issues = db.get_all_issues(self.local_db_name)
            for issue_entry in raw_issues:
                issue = rest_wrapper.JIRAIssue(jirahost, login, password, issue_entry[1])
                issue.issue_id = issue_entry[0]
                issue.summary = issue_entry[2]
                issue.worklog = db.get_issue_worklog(self.local_db_name, issue.issue_id)
                self.jira_issues[issue.issue_key] = issue
        logging.debug('Issues have been loaded')
        # Build tuple with credentials
        self.creds = ( str(jirahost), str(login), str(password), self.local_db_name )

        # Get assigned issues keys
        self.user = rest_wrapper.JiraUser(self.creds[0], self.creds[1], self.creds[2])
        self.user.get_assigned_issues()

        # GUI customization
        self.ui.dateDayWorklogEdit.setDate(QtCore.QDate.currentDate())
        #self.ui.tableDayWorklog.sortByColumn(2,0)
        # Hide worklogid from user
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, True)
        # Add status bar preferences
        self.ui.spinning_img = QtGui.QMovie('spinning-progress.gif')
        self.ui.spinning_label = QtGui.QLabel()
        self.ui.spinning_label.setMovie(self.ui.spinning_img)
        self.ui.status_msg = QtGui.QLabel()
        self.ui.statusbar.addWidget(self.ui.spinning_label)
        self.ui.statusbar.addWidget(self.ui.status_msg)
        self.ui.status_msg.hide()
        self.ui.spinning_label.hide()
        self.status_msg_queue = 0

        # Threads
        self.result_thread = ResultThread(self)
        self.result_thread.start()
        self.io_thread = IOThread(self)
        self.io_thread.start()

        # SIGNALS
        self.ui.FindIssue.clicked.connect(self._get_issue)
        self.ui.lineIssueKey.returnPressed.connect(self._get_issue)
        self.ui.dateDayWorklogEdit.dateChanged.connect(self.print_day_worklog)
        self.ui.editWorklog.clicked.connect(self._edit_worklog)
        self.ui.tableDayWorklog.doubleClicked.connect(self._edit_worklog)
        self.ui.removeWorklog.clicked.connect(self.remove_worklog)
        self.ui.tableIssues.clicked.connect(self.select_issue)
        self.ui.tableIssues.doubleClicked.connect(self.add_worklog)
        self.ui.startStopTracking.clicked.connect(self._tracking)
        self.io_thread.exception_raised.connect(self.print_exception)
        self.io_thread.status_sent.connect(self.set_status_message)
        self.io_thread.status_cleared.connect(self.clear_status_msg)
        self.io_thread.done.connect(self.print_day_worklog)
        self.result_thread.exception_raised.connect(self.print_exception)
        self.result_thread.status_sent.connect(self.set_status_message)
        self.result_thread.status_cleared.connect(self.clear_status_msg)
        self.result_thread.issue_done.connect(self._add_issue)
        self.ui.actionReresh_issue.triggered.connect(self.refresh_issue_action)
        self.ui.actionFull_refresh.triggered.connect(self.full_refresh_action)
        self.ui.actionRefresh.triggered.connect(self._refresh_gui)

        # Reqeust assigned issues
        for assigned_issue in self.user.assigned_issue_keys:
            if assigned_issue not in self.jira_issues:
                get_issue_func = partial(pyjtt.get_issue_from_jira,
                    self.creds, assigned_issue)
                logging.debug('Put func to queue')
                self.result_thread.queue.append(get_issue_func)
                self.result_thread.statuses.append('Getting issue %s ...' % str(assigned_issue))
        self._refresh_gui()

    def print_exception(self, exception):
        info_msg = 'Error appears:\n'
        info_msg += str(exception)
        QtGui.QMessageBox.warning(self, 'Warning', info_msg)

# GUI Methods
    def select_issue(self):
        if not self.is_tracking_on:
            label_new_width = self.width() - ( self.ui.startStopTracking.width() + 30 )
            issue_key = str(self.ui.tableIssues.selectedItems()[0].text()).upper()
            summary = str(self.ui.tableIssues.selectedItems()[1].text())
            self.ui.labelSelectedIssue.setText(issue_key + ': ' + summary)
            self.ui.labelSelectedIssue.setMaximumWidth(label_new_width)
            self.selected_issue = self.jira_issues[issue_key]
            logging.debug('Now selected issue %s' % str(self.jira_issues[issue_key]))

    def refresh_issues_table(self):
        logging.debug('Refreshing issues table')
        self.ui.tableIssues.setRowCount(len(self.jira_issues))
        for row, issue_key in enumerate(sorted(self.jira_issues.keys())):
            self.ui.tableIssues.setItem(row, 0,
                QtGui.QTableWidgetItem(issue_key))
            self.ui.tableIssues.setItem(row, 1,
                QtGui.QTableWidgetItem(self.jira_issues[issue_key].summary))
        self.ui.tableIssues.resizeColumnToContents(0)
        self.ui.tableIssues.horizontalHeader().setResizeMode(1,
            QtGui.QHeaderView.Stretch)
        self.ui.tableIssues.horizontalHeader().setResizeMode(0,
            QtGui.QHeaderView.Fixed)
        self.ui.tableIssues.sortByColumn(0,0)
        logging.debug('Issues table has been refreshed')

    def print_day_worklog(self):
        logging.info('RefReshing day worklog table')
        selected_day = self.ui.dateDayWorklogEdit.date().toPyDate()
        day_work = db.get_day_worklog(self.creds[3], selected_day)
        logging.debug(day_work)
        # preparations
        self.ui.tableDayWorklog.setSortingEnabled(False)

        # (u'PERF-303', u'[SS POD2] 5.10 Migration Environment Issues', datetime.datetime(2012, 12, 28, 8, 59), datetime.datetime(2012, 12, 28, 10, 59))
        # Filling the table started
        self.ui.tableDayWorklog.setRowCount(len(day_work))
        for row, entry in enumerate(day_work):
            self.ui.tableDayWorklog.setItem(row, 0,
                QtGui.QTableWidgetItem(entry[0]))
            self.ui.tableDayWorklog.setItem(row, 1,
                QtGui.QTableWidgetItem(entry[1]))
            self.ui.tableDayWorklog.setItem(row, 2,
                QtGui.QTableWidgetItem(entry[2].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 3,
                QtGui.QTableWidgetItem(entry[3].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 4,
                QtGui.QTableWidgetItem(utils.get_time_spent_string(entry[2],
                                                                   entry[3])))
            self.ui.tableDayWorklog.setItem(row, self.worklogid_column,
                QtGui.QTableWidgetItem(str(entry[4])))
        # Filling the table completed
        # Sorting
        self.ui.tableDayWorklog.setSortingEnabled(True)
        self.ui.tableDayWorklog.sortByColumn(2,QtCore.Qt.AscendingOrder)
        # Handle the width
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(1,
            QtGui.QHeaderView.Stretch)
        for column in (0,2,3,4):
            self.ui.tableDayWorklog.resizeColumnToContents(column)
            self.ui.tableDayWorklog.horizontalHeader().setResizeMode(column,
                QtGui.QHeaderView.Fixed)
            self.ui.tableDayWorklog.horizontalHeader().setResizeMode(column,
                QtGui.QHeaderView.Fixed)
        logging.info('Day worklog table has been refreshed')

    def _refresh_gui(self):
        self.refresh_issues_table()
        self.print_day_worklog()

    def _get_selected_worklog(self):
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, False)
        issue_key = str(self.ui.tableDayWorklog.selectedItems()[0].text())
        worklog_id = int(self.ui.tableDayWorklog.selectedItems()[self.worklogid_column].text())
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, True)
        return issue_key, worklog_id

    def set_status_message(self, msg, spin_img=True):
        self.ui.status_msg.setText(msg)
        self.ui.spinning_label.show()
        self.ui.status_msg.show()
        self.ui.spinning_img.start()
        self.status_msg_queue += 1
        logging.debug('Thread queue for a statusbar is %d ' % self.status_msg_queue)

    def clear_status_msg(self):
        if self.status_msg_queue == 1:
            self.ui.status_msg.hide()
            self.ui.spinning_label.hide()
        self.status_msg_queue -= 1
        logging.debug('Thread queue for a statusbar is %d ' % self.status_msg_queue)

    def _format_seconds_timer(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        time_string = '%02d:%02d:%02d' % (hours, minutes, seconds)
        return time_string

    def _update_timer_label(self, seconds):
        self.ui.labelTimeSpent.setText(self._format_seconds_timer(seconds))

    def _get_issue(self):
        """ Function parses user input from find issue line edit and
        Adds required issues to the pyjtt
        """
        logging.debug('Get issue button has been clicked')
        issue_keys = str(self.ui.lineIssueKey.text())
        logging.debug('Issue keys has red, text is "%s"' % issue_keys)
        for issue_key in issue_keys.split(','):
            issue_key = issue_key.strip().upper()
            logging.debug('issue key is %s' % issue_key)
            if issue_key and issue_key not in self.jira_issues:
                logging.debug('Packing the function')
                get_issue_func = partial(pyjtt.get_issue_from_jira,
                    self.creds, issue_key)
                logging.debug('Puting funcion to the queue')
                self.result_thread.queue.append(get_issue_func)
                self.result_thread.statuses.append('Getting issue %s ...' % str(issue_key))
        self.ui.lineIssueKey.clear()

    def refresh_issue_action(self):
        if self.ui.tabWorklogs.isHidden():
            # we on issues tab
            if len(self.ui.tableIssues.selectedItems()):
                issue_key = str(self.ui.tableIssues.selectedItems()[0].text())
                self._refresh_issue(issue_key)
            else:
                QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select issue first')
        if self.ui.tableIssues.isHidden():
            # we on worklogs tab
            if len(self.ui.tableDayWorklog.selectedItems()):
               issue_key = str(self.ui.tableDayWorklog.selectedItems()[0].text())
               self._refresh_issue(issue_key)
            else:
                QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select issue first')

    def full_refresh_action(self):
        for issue_key in self.jira_issues.keys():
            self._refresh_issue(issue_key)

    def _refresh_issue(self, issue_key):
        logging.debug('Refreshing issue %s' % str(issue_key))
        del self.jira_issues[issue_key]
        db.remove_issue(self.creds[3], issue_key)
        self._refresh_gui()
        get_issue_func = partial(pyjtt.get_issue_from_jira,
            self.creds, issue_key)
        self.result_thread.queue.append(get_issue_func)
        self.result_thread.statuses.append('Refreshing issue %s ...' % str(issue_key))


    def _add_issue(self, issue):
        logging.debug('Add issue "%s" to the memory' % str(issue))
        self.jira_issues[issue.issue_key] = issue
        logging.debug('Issue "%s" has been added' % str(issue))
        self._refresh_gui()

    def add_worklog(self):
        title = 'Add worklog'
        issue_key = str(self.ui.tableIssues.selectedItems()[0].text())
        summary = self.jira_issues[issue_key].summary
        selected_date = datetime.datetime.now()
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=1)
        self.add_window = WorklogWindow(title, issue_key, summary,
            selected_date, start_time=start_time, end_time=end_time, parent=self)
        self.add_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.add_window.show()
        if self.add_window.exec_() == QtGui.QDialog.Accepted:
            start_time = self.add_window.start_time
            end_time = self.add_window.end_time
            comment = self.add_window.comment
            logging.debug('From user: %s, %s, %s' % (str(start_time),
                                                     str(end_time), comment))
            stat_message = 'Adding worklog for issue %s' % str(issue_key)
            self._start_io(pyjtt.add_worklog, stat_message, self.creds,
                self.jira_issues[issue_key],  start_time,
                end_time, comment )

    def _edit_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self._get_selected_worklog()
            title = 'Edit worklog'
            summary = self.jira_issues[issue_key].summary
            start_time = self.jira_issues[issue_key].worklog[worklog_id][0]
            end_time = self.jira_issues[issue_key].worklog[worklog_id][1]
            comment = self.jira_issues[issue_key].worklog[worklog_id][2]
            selected_date = self.jira_issues[issue_key].worklog[worklog_id][0]
            self.edit_window = WorklogWindow(title, issue_key, summary,
                selected_date, start_time=start_time, end_time=end_time,
                comment=comment, parent=self)
            self.edit_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.edit_window.show()
            if self.edit_window.exec_() == QtGui.QDialog.Accepted:
                new_start_time = self.edit_window.start_time
                new_end_time = self.edit_window.end_time
                new_comment = self.edit_window.comment
                logging.debug('From user: %s, %s, %s' % (str(new_start_time), str(new_end_time), new_comment))
                stat_message = 'Edit worklog in issue %s' % str(issue_key)
                self._start_io(pyjtt.update_worklog, stat_message, self.creds,
                    self.jira_issues[issue_key], worklog_id, new_start_time,
                    new_end_time, new_comment)
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select worklog first')

    def remove_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self._get_selected_worklog()
            title = 'Remove worklog'
            remove_msg = "Are you sure you want to remove this worklog?"
            reply = QtGui.QMessageBox.question(self, title,
            remove_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                stat_message = 'Removing worklog in issue %s' % issue_key
                self._start_io(pyjtt.remove_worklog, stat_message, self.creds,
                    self.jira_issues[issue_key], worklog_id)
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select worklog first')

    def _start_io(self, func, msg, *args):
        single = False
        logging.debug('Packing function')
        io_func = partial(func, *args)
        if single:
            io_func()
            self.print_day_worklog()
        else:
            logging.debug('Adding finction to queue')
            self.io_thread.queue.append(io_func)
            self.io_thread.statuses.append(msg)

    def _tracking(self):
        if self.selected_issue:
            if self.ui.startStopTracking.isChecked():
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
                           str(self.tracking_thread.start),
                           str(self.tracking_thread.current),
                           utils.get_time_spent_string(self.tracking_thread.start,
                               self.tracking_thread.current)
                          )
                    reply = QtGui.QMessageBox.question(self, 'Add worklog',
                    info_msg    , QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)
                    if reply == QtGui.QMessageBox.Yes:
                        logging.debug('From GUI: %s, %s, %s' % (self.selected_issue.issue_key,
                                                                str(self.tracking_thread.start),
                                                                str(self.tracking_thread.current)
                                                                )
                                    )
                        stat_message = 'Adding worklog for issue %s' % str(self.selected_issue.issue_key)
                        self._start_io(pyjtt.add_worklog, stat_message,
                            self.creds, self.selected_issue,
                            self.tracking_thread.start, self.tracking_thread.current)
                        self._clear_tracking_timer()
                    elif reply == QtGui.QMessageBox.No:
                        self._clear_tracking_timer()
                    else:
                        self.ui.startStopTracking.setChecked(True)
                else:
                    self._clear_tracking_timer()
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select issue first')
            self.ui.startStopTracking.setChecked(False)

    def _clear_tracking_timer(self):
        self.tracking_thread.terminate()
        self.ui.startStopTracking.setText('Start Tracking')
        self.ui.startStopTracking.setText('Start Tracking')
        self.ui.labelTimeSpent.setText('00:00:00')
        self.is_tracking_on = False


def main():
    logging.debug('Local GMT offset is %s' % utils.LOCAL_UTC_OFFSET)
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