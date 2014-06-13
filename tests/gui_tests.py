#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# standard library
import unittest
import sys
import os
import logging
import shutil
import time
import json
sys.path.insert(0, os.path.abspath(os.path.join('..', 'pyjtt')))

# 3rd party
from PyQt5 import QtTest, QtWidgets, QtCore
import httpretty

# Application modules
import gui
import base_classes


class BaseGuiTest(unittest.TestCase):

    @httpretty.activate
    def setUp(self):
        self.jira_url = 'http://example.com'
        LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s - %(message)s'
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)

        # REST API stubs for initialization
        response_dict = {'maxResults': 50, 'startAt': 0, 'expand': 'schema,names', 'total': 0, 'issues': []}
        response = json.dumps(response_dict).encode('utf-8')

        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/search',
                               body=response)

        os.mkdir('.pyjtt')

        self.app = QtWidgets.QApplication([])
        self.form = gui.MainWindow(self.jira_url,
                                   'login',
                                   'password')

    def tearDown(self):
        shutil.rmtree('.pyjtt')


class AccessorGuiTest(BaseGuiTest):

    def test_print_issue_table(self):
        number_of_issues = 5
        for i in range(number_of_issues):
            issue = base_classes.JiraIssue('10024' + str(i), 'TST-' + str(i), 'Test summary number ' + str(i))
            self.form.app.db_accessor.add_issue(issue)
        self.form.refresh_ui()
        number_of_rows = self.form.ui.tableIssues.rowCount()
        self.assertEqual(number_of_issues, number_of_rows)

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

    # def test_print_worklog_table(self):
    #     raise AssertionError
    #
    # def test_set_issue_selected(self):
    #     raise AssertionError

