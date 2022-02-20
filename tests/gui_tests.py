#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# standard library
import unittest
import os
import logging
import shutil
import time
from datetime import datetime

# 3rd party
from PyQt6 import QtTest, QtWidgets, QtCore

# Application modules
from pyjtt import gui, base_classes


class TestableApp(gui.MainWindow):

    def init_workers(self):
        pass


class BaseGuiTest(unittest.TestCase):

    def setUp(self):
        LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s@%(thread)d - %(message)s'
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.ERROR)
        try:
            shutil.rmtree('.pyjtt')
        except FileNotFoundError:
            pass
        os.mkdir('.pyjtt')
        self.jira_url = 'http://example.com'
        self.app = QtWidgets.QApplication([])

        self.main_window = TestableApp(self.jira_url,
                                       'login',
                                       'password')

    def tearDown(self):
        shutil.rmtree('.pyjtt')

# Disabled after migration to Qt6
# class AccessorGuiTest(BaseGuiTest):
#
#     def setUp(self):
#         super(AccessorGuiTest, self).setUp()
#         self.main_window.app.db_accessor.truncate_db()
#
#     def test_print_issue_table(self):
#         number_of_issues = 5
#         for i in range(number_of_issues):
#             issue = base_classes.JiraIssue('10024' + str(i), 'TST-' + str(i),
#                                            'Test summary number ' + str(i))
#             self.main_window.app.db_accessor.add_issue(issue)
#         self.main_window.refresh_ui()
#         number_of_rows = self.main_window.ui.tableIssues.rowCount()
#         self.assertEqual(number_of_issues, number_of_rows)
#
#     def test_filter_issues_table(self):
#         issue1 = base_classes.JiraIssue('100241', 'TST-1', 'Target summary')
#         self.main_window.app.db_accessor.add_issue(issue1)
#         issue2 = base_classes.JiraIssue('100242', 'TST-2', 'Just summary')
#         self.main_window.app.db_accessor.add_issue(issue2)
#         QtTest.QTest.keyClicks(self.main_window.ui.lineIssueKey, 'Target')
#         # self.main_window.refresh_ui()
#         # number_of_rows = self.main_window.ui.tableIssues.rowCount()
#         # self.assertEqual(1, number_of_rows)
#         # target_key = self.main_window.ui.tableIssues.item(0, 0)
#         # self.assertEqual(target_key.text(), 'TST-1')
#
#     # def test_print_worklog_table_simple(self):
#     #     issue = base_classes.JiraIssue('100241', 'TST-1', 'Target summary')
#     #     self.main_window.app.db_accessor.add_issue(issue)
#     #     worklog_entry = base_classes.JiraWorklogEntry(issue,
#     #                                                   datetime(2014, 1, 1, 13),
#     #                                                   datetime(2014, 1, 1, 14),
#     #                                                   'Sample',
#     #                                                   12345)
#     #     self.main_window.app.db_accessor.add_worklog_entry(worklog_entry)
#     #     self.main_window.ui.dateDayWorklogEdit.setDate(
#     #         QtCore.QDate(2014, 1, 1))
#     #     self.main_window.refresh_ui()
#     #     worklog_rows = self.main_window.ui.tableDayWorklog.rowCount()
#     #     self.assertEqual(worklog_rows, 1)
# #
# #     # def test_print_worklog_table(self):
# #     #     raise AssertionError
# #     #
# #     # def test_set_issue_selected(self):
# #     #     raise AssertionError
# # #
# #     def test_filter_with_case_sensitive(self):
# #         """
# #         Filter of issues should be case insensitive
# #         """
# #         issue1 = base_classes.JiraIssue('100242', 'TST-1', 'Bug in pyjtt')
# #         issue2 = base_classes.JiraIssue('100243', 'TST-2',
# #                                         'Cant reproduce bug')
# #         issue3 = base_classes.JiraIssue('100244', 'TST-3', 'Some test')
# #
# #         for issue in (issue1, issue2, issue3):
# #             self.main_window.app.db_accessor.add_issue(issue)
#
#         # self.main_window.refresh_ui()
#         # self.assertEqual(self.main_window.ui.tableIssues.rowCount(), 3)
#         # self.main_window.ui.lineIssueKey.setText('bug')
#         # self.main_window.refresh_ui()
#         # self.assertEqual(self.main_window.ui.tableIssues.rowCount(), 2)
