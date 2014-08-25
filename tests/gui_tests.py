#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# standard library
import unittest
import sys
import os
import logging
import shutil
import time
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join('..', 'pyjtt')))

# 3rd party
from PyQt5 import QtTest, QtWidgets, QtCore

# Application modules
import gui
import base_classes


class TestableApp(gui.MainWindow):

    def init_workers(self):
        pass


class BaseGuiTest(unittest.TestCase):

    def setUp(self):
        LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s@%(thread)d - %(message)s'
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.ERROR)

        os.mkdir('.pyjtt')
        self.jira_url = 'http://example.com'
        self.app = QtWidgets.QApplication([])
        gui.MainWindow.number_of_workers = 1

        self.form = TestableApp(self.jira_url,
                                'login',
                                'password')

    def tearDown(self):
        shutil.rmtree('.pyjtt')


class AccessorGuiTest(BaseGuiTest):

    def setUp(self):
        super(AccessorGuiTest, self).setUp()

    def test_print_issue_table(self):
        number_of_issues = 5
        for i in range(number_of_issues):
            issue = base_classes.JiraIssue('10024' + str(i), 'TST-' + str(i), 'Test summary number ' + str(i))
            self.form.app.db_accessor.add_issue(issue)
        self.form.refresh_ui()
        number_of_rows = self.form.ui.tableIssues.rowCount()
        self.assertEqual(number_of_issues, number_of_rows)
        time.sleep(5)

    def test_filter_issues_table(self):
        issue1 = base_classes.JiraIssue('100241', 'TST-1', 'Target summary')
        self.form.app.db_accessor.add_issue(issue1)
        issue2 = base_classes.JiraIssue('100242', 'TST-2', 'Just summary')
        self.form.app.db_accessor.add_issue(issue2)
        QtTest.QTest.keyClicks(self.form.ui.lineIssueKey, 'Target')
        self.form.refresh_ui()
        number_of_rows = self.form.ui.tableIssues.rowCount()
        self.assertEqual(1, number_of_rows)
        target_key = self.form.ui.tableIssues.item(0, 0)
        self.assertEqual(target_key.text(), 'TST-1')
        time.sleep(5)

    def test_print_worklog_table_simple(self):
        issue = base_classes.JiraIssue('100241', 'TST-1', 'Target summary')
        self.form.app.db_accessor.add_issue(issue)
        worklog_entry = base_classes.JiraWorklogEntry(issue,
                                                      datetime(2014, 1, 1, 13),
                                                      datetime(2014, 1, 1, 14),
                                                      'Sample',
                                                      12345)
        self.form.app.db_accessor.add_worklog_entry(worklog_entry)
        self.form.ui.dateDayWorklogEdit.setDate(QtCore.QDate(2014, 1, 1))
        self.form.refresh_ui()
        worklog_rows = self.form.ui.tableDayWorklog.rowCount()
        self.assertEqual(worklog_rows, 1)

    # def test_print_worklog_table(self):
    #     raise AssertionError
    #
    # def test_set_issue_selected(self):
    #     raise AssertionError

    def test_filter_with_case_sensitive(self):
        """
        Filter of issues should be case insensetive
        """
        issue1 = base_classes.JiraIssue('100241', 'TST-1', 'Bug in pyjtt')
        issue2 = base_classes.JiraIssue('100242', 'TST-2', 'Cant reproduce bug')
        issue3 = base_classes.JiraIssue('100243', 'TST-3', 'Some test')

        for issue in (issue1, issue2, issue3):
            self.form.app.db_accessor.add_issue(issue)

        self.form.refresh_ui()
        self.assertEqual(self.form.ui.tableIssues.rowCount(), 3)
        self.form.ui.lineIssueKey.setText('bug')
        self.form.refresh_ui()
        self.assertEqual(self.form.ui.tableIssues.rowCount(), 2)