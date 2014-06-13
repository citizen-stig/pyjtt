#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# standard library
import unittest
import sys
import os
import logging
import shutil
import time
sys.path.insert(0, os.path.abspath(os.path.join('..', 'pyjtt')))

# 3rd party
from PyQt5 import QtTest, QtWidgets, QtCore
import httpretty

# Application modules
import gui


class BaseGuiTest(unittest.TestCase):

    @httpretty.activate
    def setUp(self):
        self.jira_url = 'http://example.com'
        LOGGING_FORMAT = '%(asctime)s %(levelname)s - %(name)s - %(message)s'
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)

        # Test stubs
        response = b'{"expand": "schema,names", "total": 5, "startAt": 0, ' \
                   b'"issues": [' \
                   b'{"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test1"}, "key": "TST-101", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10502", "id": "10502"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test2"}, "key": "TST-102", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10500", "id": "10500"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test3"}, "key": "TST-103", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10443", "id": "10443"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test4"}, "key": "TST-104", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10442", "id": "10442"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test5"}, "key": "TST-105", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10441", "id": "10441"}' \
                   b'], "maxResults": 50}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/search',
                               body=response)

        os.mkdir('.pyjtt')

        self.app = QtWidgets.QApplication([])
        self.form = gui.MainWindow(self.jira_url,
                                   'login',
                                   'password')
        # TODO: replace sleep and get smart signal working
        time.sleep(0.1)
        self.form.print_issues_table(self.form.app.get_all_issues())

    def tearDown(self):
        shutil.rmtree('.pyjtt')


class AccessorGuiTest(BaseGuiTest):

    def test_initial(self):
        self.assertEqual(self.form.ui.tableIssues.rowCount(), 5)

    @httpretty.activate
    def test_add_issue(self):
        sample_issue_key = 'TST-1000'
        response = b'{"id": "10806", "fields": ' \
                   b'{' \
                   b'"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b'"summary": "\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82\xd1\x89 and english"' \
                   b'}, ' \
                   b'"expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog", ' \
                   b'"key": "TST-1000", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10806"}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/issue/' + sample_issue_key,
                               body=response)


        initial_count = self.form.ui.tableIssues.rowCount()
        QtTest.QTest.keyClicks(self.form.ui.lineIssueKey, sample_issue_key)
        QtTest.QTest.mouseClick(self.form.ui.FindIssue, QtCore.Qt.LeftButton)
        # FIXME: replace sleep with smarter implementation
        time.sleep(0.1)
        self.form.print_issues_table(self.form.app.get_all_issues())
        self.assertEqual(self.form.ui.tableIssues.rowCount(), initial_count + 1)
