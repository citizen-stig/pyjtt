#!/usr/bin/env python
__author__ = 'Nikolay Golub'

import sys
import os
from datetime import datetime
import unittest
sys.path.insert(0, os.path.abspath(os.path.join('..', 'pyjtt')))

import db_accessor
import base_classes


class DBTest(unittest.TestCase):

    def setUp(self):
        self.filename = 'sample.db'
        self.accessor = db_accessor.DBAccessor(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def test_create_accessor(self):
        db_conn, cursor = self.accessor._connect_to_db()
        self.assertIsNotNone(db_conn)
        self.assertIsNotNone(cursor)
        db_conn.close()

    def test_reopen_db(self):
        raise AssertionError

    def test_add_and_get_issue(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        self.accessor.add_issue(issue)

        from_db_issue = self.accessor.get_issue(issue.key)
        self.assertEqual(issue.key, from_db_issue.key)
        self.assertEqual(issue.issue_id, from_db_issue.issue_id)
        self.assertEqual(issue.summary, from_db_issue.summary)

    def test_add_and_get_issue_worklog(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        worklog = [
            base_classes.JiraWorklogEntry(issue,
                                          datetime(2014, 1, 1, 12),
                                          datetime(2014, 1, 1, 13),
                                          'Комментарий',
                                          '11111'),
            base_classes.JiraWorklogEntry(issue,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '22222'),
        ]
        self.accessor.add_issue(issue)
        self.accessor.add_worklog(worklog)

        worklog_from_db = self.accessor.get_worklog_for_issue(issue)

        self.assertEqual(len(worklog), len(worklog_from_db))

    def test_add_worklog_same_id(self):
        raise AssertionError

    def test_remove_worklog(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        worklog = [
            base_classes.JiraWorklogEntry(issue,
                                          datetime(2014, 1, 1, 12),
                                          datetime(2014, 1, 1, 13),
                                          'Комментарий',
                                          '11111'),
            base_classes.JiraWorklogEntry(issue,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '12345'),
        ]
        self.accessor.add_issue(issue)
        self.accessor.add_worklog(worklog)
        self.accessor.remove_worklog_entry(worklog[0])

        worklog_from_db = self.accessor.get_worklog_for_issue(issue)

        self.assertEqual(len(worklog) - 1, len(worklog_from_db))

    def test_update_worklog(self):
        raise AssertionError

    def test_get_day_worklog(self):
        raise AssertionError

    def test_get_all_issues(self):
        raise AssertionError


if __name__ == '__main__':
    unittest.main()