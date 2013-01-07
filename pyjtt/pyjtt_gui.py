#!/usr/bin/env python
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import os, sys, logging, datetime

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

import db, utils, rest_wrapper, pyjtt
import login_screen, main_window, worklog_window
from functools import partial

from PyQt4 import QtCore, QtGui




def datetime_to_qtime(timestamp):
    return QtCore.QTime(timestamp.hour, timestamp.minute)

def get_time_spent_string(timestamp_start, timestamp_end):
    logging.debug('')
    raw_spent = timestamp_end\
                - timestamp_start
    hours, seconds = divmod(raw_spent.seconds, 3600)
    minutes = seconds / 60
    spent = ''
    if hours:
        spent += str(hours) + 'h'
    if minutes:
        spent += ' ' + str(minutes) + 'm'
    spent_str = spent.strip()
    return spent_str


class IOThread(QtCore.QThread):
    def __init__(self, func, parent=None):
        QtCore.QThread.__init__(self, parent)
        logging.debug('Initialize new Thread for IO')
        self.io_func = func

    def run(self):
        self.io_func()

    def __del__(self):
        logging.debug('Thread is terminating')





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
                get_time_spent_string(self.ui.timeStartEdit.dateTime().toPyDateTime(),
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

        self.jira_issues = {}
        self.selected_issue = None
        self.is_tracking_on = False
        self.worklogid_column = 5

        local_db_name = utils.get_db_filename(login, jirahost)
        if not os.path.isfile(local_db_name):
            logging.debug('Local DB does not exist. Creating local database')
            db_conn, cursor = db.create_local_db(utils.get_db_filename(login, jirahost))
        else:
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

        # GUI customization
        self.ui.dateDayWorklogEdit.setDate(QtCore.QDate.currentDate())
        # hide worklogid from user
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, True)
        self._refresh_issues_table()
        self._print_day_worklog()
        # Add status bar preferences
        self.ui.spinnig_img = QtGui.QMovie("spinning-progress.gif")
        self.ui.spinning_label = QtGui.QLabel()
        self.ui.spinning_label.setMovie(self.ui.spinnig_img)
        self.ui.status_msg = QtGui.QLabel()
        self.ui.statusbar.addWidget(self.ui.spinning_label)
        self.ui.statusbar.addWidget(self.ui.status_msg)
        self.ui.status_msg.hide()
        self.ui.spinning_label.hide()
        self.status_msg_queue = 0

        # SIGNALS
        self.ui.FindIssue.clicked.connect(self._get_issue)
        self.ui.dateDayWorklogEdit.dateChanged.connect(self._print_day_worklog)
        self.ui.editWorklog.clicked.connect(self._edit_worklog)
        self.ui.removeWorklog.clicked.connect(self._remove_worklog)
        self.ui.tableIssues.clicked.connect(self._select_issue)
        self.ui.tableIssues.doubleClicked.connect(self._add_worklog)
        self.ui.startStopTracking.clicked.connect(self._tracking)

    def _add_worklog(self):
        title = 'Add worklog'
        issue_key = str(self.ui.tableIssues.selectedItems()[0].text())
        summary = self.jira_issues[issue_key].summary
        selected_date = datetime.datetime.now()
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=1)
        self.add_window = WorklogWindow(title, issue_key, summary,
            selected_date, start_time=start_time, end_time=end_time)
        self.add_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.add_window.show()
        if self.add_window.exec_() == QtGui.QDialog.Accepted:
            start_time = self.add_window.start_time
            end_time = self.add_window.end_time
            comment = self.add_window.comment
            logging.debug('From user: %s, %s, %s' % (str(start_time), str(end_time), comment))
            pyjtt.add_worklog(self.creds, self.jira_issues[issue_key],
                start_time, end_time, comment)
            self._print_day_worklog()

    def _select_issue(self):
        if not self.is_tracking_on:
            issue_key = str(self.ui.tableIssues.selectedItems()[0].text())
            summary = str(self.ui.tableIssues.selectedItems()[1].text())
            self.ui.labelSelectedIssue.setText(issue_key + ': ' + summary)
            self.selected_issue = self.jira_issues[issue_key]
            logging.debug('Now selected issue %s' % self.jira_issues[issue_key].summary)

    def _tracking(self):
        if self.selected_issue:
            if self.ui.startStopTracking.isChecked():
                # TODO: add starting of tracking here
                self.ui.startStopTracking.setText('Stop Tracking')
                self.is_tracking_on = True
            else:
                # TODO: Add stoping of tracking here
                self.ui.startStopTracking.setText('Start Tracking')
                self.is_tracking_on = False
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select issue first')
            self.ui.startStopTracking.setChecked(False)
        # TODO: add event for filtering issues in table, when user enters key

    def _get_issue(self):
        logging.debug('Get issue button has been clicked')
        issue_keys = str(self.ui.lineIssueKey.text())
        for issue_key in issue_keys.split(','):
            issue_key = issue_key.strip()
            if issue_key and issue_key not in self.jira_issues:
                # TODO: add try block here

                issue = pyjtt.get_issue_from_jira(self.creds, issue_key)

                self.jira_issues[issue_key] = issue
                logging.debug('Issue has been added')
                self._refresh_issues_table()
        self._print_day_worklog()
        self.ui.lineIssueKey.clear()

    def _refresh_issues_table(self):
        logging.debug('Refreshing table')
        self.ui.tableIssues.setRowCount(len(self.jira_issues))
        row = 0
        for issue_key in sorted(self.jira_issues.keys()):
            self.ui.tableIssues.setItem(row, 0, QtGui.QTableWidgetItem(issue_key))
            self.ui.tableIssues.setItem(row, 1, QtGui.QTableWidgetItem(self.jira_issues[issue_key].summary))
            self.ui.tableIssues.setItem(row, 2, QtGui.QTableWidgetItem('N/A'))
            row += 1
        self.ui.tableIssues.resizeColumnToContents(0)
        self.ui.tableIssues.resizeColumnToContents(2)
        self.ui.tableIssues.horizontalHeader().setResizeMode(1,QtGui.QHeaderView.Stretch)
        self.ui.tableIssues.horizontalHeader().setResizeMode(0,QtGui.QHeaderView.Fixed)
        logging.debug('Table refresh has been completed')

    def _print_day_worklog(self):
        logging.debug('Request worklog for a day')

        selected_day = self.ui.dateDayWorklogEdit.date().toPyDate()
        day_work = db.get_day_worklog(self.creds[4], selected_day)
        # (u'PERF-303', u'[SS POD2] 5.10 Migration Environment Issues', datetime.datetime(2012, 12, 28, 8, 59), datetime.datetime(2012, 12, 28, 10, 59))
        self.ui.tableDayWorklog.setRowCount(len(day_work))
        for row, entry in enumerate(day_work):
            self.ui.tableDayWorklog.setItem(row, 0, QtGui.QTableWidgetItem(entry[0]))
            self.ui.tableDayWorklog.setItem(row, 1, QtGui.QTableWidgetItem(entry[1]))
            self.ui.tableDayWorklog.setItem(row, 2, QtGui.QTableWidgetItem(entry[2].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 3, QtGui.QTableWidgetItem(entry[3].strftime('%H:%M')))
            self.ui.tableDayWorklog.setItem(row, 4, QtGui.QTableWidgetItem(get_time_spent_string(entry[2],entry[3])))
            # hidden worklogid
            self.ui.tableDayWorklog.setItem(row, self.worklogid_column, QtGui.QTableWidgetItem(str(entry[4])))
        self.ui.tableDayWorklog.resizeColumnToContents(0)
        self.ui.tableDayWorklog.resizeColumnToContents(2)
        self.ui.tableDayWorklog.resizeColumnToContents(3)
        self.ui.tableDayWorklog.resizeColumnToContents(4)
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(1,QtGui.QHeaderView.Stretch)
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(0,QtGui.QHeaderView.Fixed)
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(2,QtGui.QHeaderView.Fixed)
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(3,QtGui.QHeaderView.Fixed)
        self.ui.tableDayWorklog.horizontalHeader().setResizeMode(4,QtGui.QHeaderView.Fixed)
        logging.debug('Worklog table has been updated')

    def _edit_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self._get_selected_worklog()
            title = 'Edit worklog'
            summary = self.jira_issues[issue_key].summary
            start_time = self.jira_issues[issue_key].worklog[worklog_id][0]
            end_time = self.jira_issues[issue_key].worklog[worklog_id][1]
            comment = self.jira_issues[issue_key].worklog[worklog_id][2]
            selected_date = self.jira_issues[issue_key].worklog[worklog_id][0]

            self.edit_window = WorklogWindow(title, issue_key, summary, selected_date, start_time=start_time, end_time=end_time, comment=comment)
            self.edit_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.edit_window.show()
            if self.edit_window.exec_() == QtGui.QDialog.Accepted:
                new_start_time = self.edit_window.start_time
                new_end_time = self.edit_window.end_time
                new_comment = self.edit_window.comment
                logging.debug('From user: %s, %s, %s' % (str(new_start_time), str(new_end_time), new_comment))
                pyjtt.update_worklog(self.creds, self.jira_issues[issue_key],
                    worklog_id, new_start_time, new_end_time, new_comment)
                self._print_day_worklog()
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select worklog first')

    def _remove_worklog(self):
        if self.ui.tableDayWorklog.selectedItems():
            issue_key, worklog_id = self._get_selected_worklog()
            title = 'Remove worklog'
            remove_msg = "Are you sure you want to remove this worklog?"
            reply = QtGui.QMessageBox.question(self, title,
            remove_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                pyjtt.remove_worklog(self.creds, self.jira_issues[issue_key],
                    worklog_id)
                self._print_day_worklog()
        else:
            QtGui.QMessageBox.warning(self, 'Tracking Error', 'Please, select worklog first')

    def _get_selected_worklog(self):
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, False)
        issue_key = str(self.ui.tableDayWorklog.selectedItems()[0].text())
        worklog_id = int(self.ui.tableDayWorklog.selectedItems()[self.worklogid_column].text())
        self.ui.tableDayWorklog.setColumnHidden(self.worklogid_column, True)
        return issue_key, worklog_id

    def set_status_message(self, msg, spin_img=False):
        self.ui.status_msg.setText(msg)
        self.ui.spinning_label.show()
        self.ui.status_msg.show()
        self.ui.spinning_img.start()
        self.status_msg_queue += 1
        logging.debug('Thread queue for a status bar is %d ' % self.status_msg_queue)

        def clear_status_msg(self):
            if self.status_msg_queue == 1:
                self.ui.status_msg.hide()
                self.ui.spinnig_label.hide()
        self.status_msg_queue -= 1
        logging.debug('Thread queue for a status bar is %d ' % self.status_msg_queue)


    def __del__(self):
        # TODO: if creds is not defined yet
        pyjtt.normal_exit(self.creds[3])


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