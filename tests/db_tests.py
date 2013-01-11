#!/usr/bin/env python
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import sys, unittest, os, sqlite3, datetime
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import db

class pyjttUtilsTest(unittest.TestCase):
    def setUp(self):
        self.filename = 'sample.db'
        self.db_conn, self.cursor = db.create_local_db(self.filename)
        self.db_conn.close()


    def tearDown(self):
        os.remove(self.filename)


    def test_create_db(self):
        filename = 'create_sample.db'
        db.create_local_db(filename)
        os.remove(filename)
        with self.assertRaises(sqlite3.OperationalError):
            db.create_local_db(os.path.join('no', 'such', 'file'))

    def test_conect_to_db(self):
        db_conn, cursor = db.connect_to_db(self.filename)
        self.assertEqual(type(db_conn), type(self.db_conn))
        self.assertEqual(type(cursor), type(self.cursor))

    def test_add_issue_normal(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        db_conn, cursor = db.connect_to_db(self.filename)
        cursor.execute('SELECT * FROM JIRAIssues')
        entry = cursor.fetchall()
        self.assertEqual(entry, [(issue_id, issue_key, issue_summary)])
        db.add_issue(self.filename, issue_id+1, issue_key, issue_summary )
        cursor.execute('SELECT * FROM JIRAIssues')
        entry = cursor.fetchall()
        self.assertEqual(len(entry), 2)


    def test_add_issue_errors(self):
        print 'TDB'
        # PRIMARY KEY ERROR

        # WRONG TYPES

        # WRONG FILEPATH

    def test_get_issue(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        issue = db.get_issue(self.filename, issue_key)
        self.assertEqual(issue, (issue_id, issue_key, issue_summary))
        self.assertEqual(None, db.get_issue(self.filename, 'NOSUCH-123'))

    def test_get_issue_errors(self):
        print 'TDB'
        #Wrong filename

    def test_add_issue_worklog(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        # worglog = { id : ( start_date, end_date, comment) }
        worklog = { 12345 : ( datetime.datetime(2013, 01, 03, 15), datetime.datetime(2013, 01, 03, 17) , 'Sample comment'),
                    12346 : ( datetime.datetime(2013, 01, 04, 15), datetime.datetime(2013, 01, 04, 17) , 'Sample comment'), }
        db.add_issue_worklog(self.filename, worklog, issue_id)

    def test_add_issue_worklog_errors(self):
        print 'TDB'

    def test_get_issue_worklog(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        # worglog = { id : ( start_date, end_date, comment) }
        worklog = { 12345 : ( datetime.datetime(2013, 01, 03, 15), datetime.datetime(2013, 01, 03, 17) , 'Sample comment'),
                    12346 : ( datetime.datetime(2013, 01, 04, 15), datetime.datetime(2013, 01, 04, 17) , 'Sample comment'), }
        db.add_issue_worklog(self.filename, worklog, issue_id)
        r_worklog = db.get_issue_worklog(self.filename, issue_id)
        self.assertEqual(worklog, r_worklog)

    def test_get_issue_worklog_error(self):
        print 'TDB'

    def test_remove_issue_worklog(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        # worglog = { id : ( start_date, end_date, comment) }
        worklog = { 12345 : ( datetime.datetime(2013, 01, 03, 15), datetime.datetime(2013, 01, 03, 17) , 'Sample comment'),
                    12346 : ( datetime.datetime(2013, 01, 04, 15), datetime.datetime(2013, 01, 04, 17) , 'Sample comment'), }
        db.add_issue_worklog(self.filename, worklog, issue_id)
        deleted_id = 12346
        db.remove_issue_worklog(self.filename,deleted_id)
        del worklog[deleted_id]
        r_worklog = db.get_issue_worklog(self.filename, issue_id)
        self.assertEqual(worklog, r_worklog)

    def test_remove_issue_worklog_errors(self):
        print 'TDB'

    def test_update_issue_worklog(self):
        issue_id = 12345
        issue_key = 'SAMPLE-123'
        issue_summary = 'Summary'
        db.add_issue(self.filename, issue_id, issue_key, issue_summary )
        # worglog = { id : ( start_date, end_date, comment) }
        worklog = { 12345 : ( datetime.datetime(2013, 01, 03, 15), datetime.datetime(2013, 01, 03, 17) , 'Sample comment'),
                    12346 : ( datetime.datetime(2013, 01, 04, 15), datetime.datetime(2013, 01, 04, 17) , 'Sample comment'), }
        db.add_issue_worklog(self.filename, worklog, issue_id)
        upd_id = 12346
        upd_start = datetime.datetime(2012, 12, 21, 15, 30)
        upd_end = datetime.datetime(2012, 12, 21, 16, 05)
        upd_comment = 'End of the world'
        worklog[upd_id] = (upd_start, upd_end, upd_comment)
        db.update_issue_worklog(self.filename, upd_id, upd_start, upd_end, upd_comment)
        r_worklog = db.get_issue_worklog(self.filename, issue_id)
        self.assertEqual(worklog, r_worklog)

    def test_upd_issue_worklog_errors(self):
        print 'TDB'

    def test_get_day_worklog(self):
        issue_id_1 = 12345
        issue_key_1 = 'SAMPLE-123'
        issue_summary_1 = 'Summary'
        db.add_issue(self.filename, issue_id_1, issue_key_1, issue_summary_1 )
        issue_id_2 = 12346
        issue_key_2 = 'SAMPLE-126'
        issue_summary_2 = 'Summary 2'
        db.add_issue(self.filename, issue_id_2, issue_key_2, issue_summary_2 )
        worklog_1 = { 12345 : ( datetime.datetime(2013, 01, 03, 15), datetime.datetime(2013, 01, 03, 17) , 'Sample comment'),
                    12346 : ( datetime.datetime(2013, 01, 04, 15), datetime.datetime(2013, 01, 04, 17) , 'Sample comment'), }
        worklog_2 = { 12347 : ( datetime.datetime(2013, 01, 03, 19), datetime.datetime(2013, 01, 03, 21) , 'Sample comment'),
                      12348 : ( datetime.datetime(2013, 01, 04, 19), datetime.datetime(2013, 01, 04, 21) , 'Sample comment'), }
        db.add_issue_worklog(self.filename, worklog_1, issue_id_1)
        db.add_issue_worklog(self.filename, worklog_2, issue_id_2)
        expected = [(issue_key_1, issue_summary_1, worklog_1[12346][0], worklog_1[12346][1], 12346 ),
                    (issue_key_2, issue_summary_2, worklog_2[12348][0], worklog_2[12348][1], 12348 )]
        day_work = db.get_day_worklog(self.filename, datetime.datetime(2013, 01, 04))
        self.assertEqual(day_work, expected)

    def test_get_all_issues(self):
        issue_id_1 = 12345
        issue_key_1 = 'SAMPLE-123'
        issue_summary_1 = 'Summary'
        db.add_issue(self.filename, issue_id_1, issue_key_1, issue_summary_1 )
        issue_id_2 = 12346
        issue_key_2 = 'SAMPLE-126'
        issue_summary_2 = 'Summary 2'
        db.add_issue(self.filename, issue_id_2, issue_key_2, issue_summary_2 )
        expected = [(issue_id_1, issue_key_1, issue_summary_1),
            (issue_id_2,issue_key_2, issue_summary_2)]
        all_issues = db.get_all_issues(self.filename)
        self.assertEqual(all_issues, expected)

    def test_get_all_issues_err(self):
        print 'TDB'

if __name__ == '__main__':
    unittest.main()