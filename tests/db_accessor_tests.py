#!/usr/bin/env python
__author__ = 'Nikolai Golub'

import os
from datetime import datetime
import unittest

from pyjtt import db_accessor, base_classes


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
        issue1 = base_classes.JiraIssue('1111', 'TST-111', 'Юникод')
        self.accessor.add_issue(issue1)
        del self.accessor
        new_accessor = db_accessor.DBAccessor(self.filename)
        new_from_db = new_accessor.get_all_issues()
        self.assertEqual(len(list(new_from_db)), 1)

    def test_get_nonexisted_issue(self):
        none = self.accessor.get_issue('TST-969')
        self.assertIsNone(none)

    def test_add_and_get_issue(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        self.accessor.add_issue(issue)

        from_db_issue = self.accessor.get_issue(issue.key)
        self.assertEqual(issue.key, from_db_issue.key)
        self.assertEqual(issue.issue_id, from_db_issue.issue_id)
        self.assertEqual(issue.summary, from_db_issue.summary)

    def test_update_issue(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        self.accessor.add_issue(issue)
        issue.summary = 'Еще Юникод'
        self.accessor.add_issue(issue)

        from_db_issue = self.accessor.get_issue(issue.key)
        self.assertEqual(issue.key, from_db_issue.key)
        self.assertEqual(issue.issue_id, from_db_issue.issue_id)
        self.assertEqual(issue.summary, 'Еще Юникод')

    def test_remove_issue(self):
        issue1 = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        self.accessor.add_issue(issue1)

        issue2 = base_classes.JiraIssue('22222', 'TST-222', 'Юникод')
        self.accessor.add_issue(issue2)

        self.accessor.remove_issue(issue2)

        rest_issues = self.accessor.get_all_issues()
        self.assertEqual(len(list(rest_issues)), 1)

    def test_add_and_get_worklog_one(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        worklog = [
            base_classes.JiraWorklogEntry(issue,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '22222')
        ]
        self.accessor.add_issue(issue)
        self.accessor.add_worklog(worklog)

        worklog_from_db = list(self.accessor.get_worklog_for_issue(issue))

        self.assertEqual(len(worklog), len(worklog_from_db))
        self.assertEqual(worklog_from_db[0].started, worklog[0].started)
        self.assertEqual(worklog_from_db[0].ended, worklog[0].ended),
        self.assertEqual(worklog_from_db[0].worklog_id, worklog[0].worklog_id)
        self.assertEqual(worklog_from_db[0].comment, worklog[0].comment)
        self.assertEqual(worklog_from_db[0].issue.key, worklog[0].issue.key)

    def test_add_and_get_worklog_many(self):
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

        worklog_from_db = list(self.accessor.get_worklog_for_issue(issue))

        self.assertEqual(len(worklog), len(worklog_from_db))
        self.assertTrue(worklog_from_db[0].comment in ('Комментарий',
                                                          'Комментарий два'))

    def test_add_and_get_worklog_entry(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        worklog_entry = base_classes.JiraWorklogEntry(issue,
                                                      datetime(2014, 1, 1, 12),
                                                      datetime(2014, 1, 1, 13),
                                                      'Комментарий',
                                                      '11111')
        self.accessor.add_issue(issue)
        self.accessor.add_worklog_entry(worklog_entry)

        worklog_entry_from_db = next(self.accessor.get_worklog_for_issue(issue))
        self.assertEqual(worklog_entry_from_db.started, worklog_entry.started)
        self.assertEqual(worklog_entry_from_db.ended, worklog_entry.ended)
        self.assertEqual(worklog_entry_from_db.comment, worklog_entry.comment)
        self.assertEqual(worklog_entry_from_db.worklog_id,
                         worklog_entry.worklog_id)
        self.assertEqual(worklog_entry_from_db.issue.key,
                         worklog_entry.issue.key)

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

        self.assertEqual(len(list(worklog)) - 1, len(list(worklog_from_db)))

    def test_update_worklog_entry(self):
        issue = base_classes.JiraIssue('12345', 'TST-123', 'Юникод')
        worklog_entry = base_classes.JiraWorklogEntry(issue,
                                                      datetime(2014, 1, 1, 12),
                                                      datetime(2014, 1, 1, 13),
                                                      'Комментарий',
                                                      '11111')
        self.accessor.add_issue(issue)
        self.accessor.add_worklog_entry(worklog_entry)
        worklog_entry.started = datetime(2013, 12, 12, 12)
        self.accessor.update_worklog_entry(worklog_entry)
        worklog_entry_from_db = next(self.accessor.get_worklog_for_issue(issue))
        self.assertEqual(worklog_entry_from_db.started.year, 2013)

    def test_update_worklog_many(self):
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

        worklog_from_db = list(self.accessor.get_worklog_for_issue(issue))

        self.assertEqual(len(worklog), len(worklog_from_db))
        self.assertTrue(worklog_from_db[0].comment in ('Комментарий',
                                                       'Комментарий два'))

        worklog[0].ended = datetime(2014, 1, 1, 15)
        worklog[0].comment = 'Обновленный комментарий'
        self.accessor.add_worklog(worklog)

        updated_worklog_from_db = self.accessor.get_worklog_for_issue(issue)
        updated_entry_list = [x for x in updated_worklog_from_db
                              if x.worklog_id == '11111']
        self.assertEqual(len(updated_entry_list), 1)
        self.assertEqual(updated_entry_list[0].ended.hour, 15)

    def test_get_day_worklog(self):
        issue1 = base_classes.JiraIssue('1111', 'TST-111', 'Юникод')
        issue2 = base_classes.JiraIssue('2222', 'TST-222', 'Юникод')

        worklog = [
            base_classes.JiraWorklogEntry(issue1,
                                          datetime(2014, 1, 1, 12),
                                          datetime(2014, 1, 1, 13),
                                          'Комментарий',
                                          '11111'),
            base_classes.JiraWorklogEntry(issue1,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий',
                                          '01010'),
            base_classes.JiraWorklogEntry(issue2,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '22222'),
            base_classes.JiraWorklogEntry(issue2,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '33333'),
            base_classes.JiraWorklogEntry(issue1,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '44444'),
            base_classes.JiraWorklogEntry(issue2,
                                          datetime(2014, 1, 2, 12),
                                          datetime(2014, 1, 2, 13),
                                          'Комментарий два',
                                          '55555'),
            base_classes.JiraWorklogEntry(issue1,
                                          datetime(2014, 1, 3, 12),
                                          datetime(2014, 1, 3, 13),
                                          'Комментарий два',
                                          '66666'),
            base_classes.JiraWorklogEntry(issue2,
                                          datetime(2014, 1, 3, 12),
                                          datetime(2014, 1, 3, 13),
                                          'Комментарий два',
                                          '77777'),
        ]

        self.accessor.add_issue(issue1)
        self.accessor.add_issue(issue2)
        self.accessor.add_worklog(worklog)
        day1_worklog = self.accessor.get_day_worklog(datetime(2014, 1, 2))
        self.assertEqual(len(list(day1_worklog)), 5)
        day2_worklog = self.accessor.get_day_worklog(datetime(2014, 1, 3))
        self.assertEqual(len(list(day2_worklog)), 2)

    def test_get_all_issues(self):
        n = 5
        for i in range(n):
            issue = base_classes.JiraIssue('1234%s' % i, 'TST-%s' % i, 'Юникод')
            self.accessor.add_issue(issue)
        issues_from_db = self.accessor.get_all_issues()
        self.assertEqual(len(list(issues_from_db)), n)


if __name__ == '__main__':
    unittest.main()
