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
#    This module handles access to sqlite database in cache role.

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2014, Nikolay Golub"
__license__ = "GPL"

from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

from base_classes import JiraIssue, JiraWorklogEntry


class DBAccessor(object):
    TIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    ISSUES_TABLE_NAME = 'JIRAIssues'
    WORKLOG_TABLE_NAME = 'Worklogs'
    CREATE_ISSUES_TABLE_SQL = """CREATE TABLE IF NOT EXISTS {issues_table_name}
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT)""".format(issues_table_name=ISSUES_TABLE_NAME)
    CREATE_WORKLOGS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS {worklogs_table_name}
                        (worklog_id INTEGER PRIMARY KEY,
                         jira_issue_id INTEGER,
                         comment TEXT,
                         start_date TIMESTAMP,
                         end_date TIMESTAMP)""".format(worklogs_table_name=WORKLOG_TABLE_NAME)

    def __init__(self, db_filename):
        self.db_filename = db_filename
        db_conn, cursor = self._connect_to_db()
        tables = cursor.execute('SELECT name FROM sqlite_master '
                                'WHERE type="table" '
                                'AND name="{issues_table}";'.format(issues_table=self.ISSUES_TABLE_NAME))
        if len(tables.fetchall()) != 2:
            self._create_local_db()
        db_conn.close()

    def _create_local_db(self):
        """Creates local db and tables"""
        logger.debug('Creating db %s' % self.db_filename)
        db_conn = sqlite3.connect(str(self.db_filename))
        cursor = db_conn.cursor()
        logger.debug('Creating table JIRAIssues')
        cursor.execute(self.CREATE_ISSUES_TABLE_SQL)
        logger.debug('Creating table worklogs')
        cursor.execute(self.CREATE_WORKLOGS_TABLE_SQL)
        db_conn.commit()
        logger.debug('Tables created')

    def _connect_to_db(self):
        logger.debug('Connecting to local DB: %s' % self.db_filename)
        db_conn = sqlite3.connect(self.db_filename, timeout=30)
        cursor = db_conn.cursor()
        logger.debug('Connection has been successful')
        return db_conn, cursor

    def _convert_to_datetime(self, datetime_string):
        return datetime.strptime(datetime_string, self.TIMEFORMAT)

    def add_issue(self, issue):
        logger.debug('Saving issue %s in local DB' % issue.key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('INSERT INTO '
                       '{issues_table} (jira_issue_id, jira_issue_key, summary) '
                       'VALUES (?,?,?);'.format(issues_table=self.ISSUES_TABLE_NAME),
                       (issue.issue_id, issue.key, issue.summary))
        db_conn.commit()
        db_conn.close()
        logger.debug('Issue %s has been saved in local DB')

    def remove_issue(self, issue):
        logger.debug('Removing issue %s from local DB' % issue.key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('DELETE FROM Worklogs'
                       'WHERE jira_issue_id = '
                       '(SELECT jira_issue_id FROM JIRAIssues '
                       'WHERE jira_issue_key = ?)', (issue.key,))
        cursor.execute('DELETE FROM JIRAIssues '
                       'WHERE jira_issue_key = ?', (issue.key,))
        db_conn.commit()
        db_conn.close()
        logger.debug('Issue %s has been remove from local DB' % issue_key)

    def get_issue(self, issue_key):
        logger.debug('Getting issue %s from local DB' % issue_key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT * FROM JIRAIssues where jira_issue_key = ?', (issue_key,))
        raw_issue = cursor.fetchone()
        db_conn.close()
        try:
            issue = JiraIssue(str(raw_issue[0]), raw_issue[1], raw_issue[2])
            logger.debug('Issue %s has been extracted from local DB')
            return issue
        except sqlite3.DatabaseError:
            # TODO: move to the normal exception
            pass

    def get_worklog_for_issue(self, issue):
        worklog = []
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT worklog_id, start_date, end_date, comment '
                       'FROM Worklogs WHERE jira_issue_id = ?', (issue.issue_id,))
        for raw_worklog_entry in cursor.fetchall():
            started = self._convert_to_datetime(raw_worklog_entry[1])
            ended = self._convert_to_datetime(raw_worklog_entry[2])
            worklog_entry = JiraWorklogEntry(issue, started, ended, raw_worklog_entry[3], raw_worklog_entry[0])
            worklog.append(worklog_entry)
        return worklog

    def add_worklog(self, worklog):
        rows = [(x.worklog_id, x.issue.issue_id, x.started, x.ended, x.comment) for x in worklog]
        db_conn, cursor = self._connect_to_db()
        cursor.executemany('INSERT INTO {worklogs} (worklog_id, jira_issue_id, start_date, end_date, comment)'
                           'VALUES (?,?,?,?,?)'.format(worklogs=self.WORKLOG_TABLE_NAME), rows)
        db_conn.commit()
        db_conn.close()

    def add_worklog_entry(self, issue, worklog_entry):
        db_conn, cursor = self._connect_to_db()
        cursor.executemany('INSERT INTO {worklogs} (worklog_id, jira_issue_id, start_date, end_date, comment)'
                           'VALUES (?,?,?,?,?)'.format(worklogs=self.WORKLOG_TABLE_NAME), rows)
        db_conn.commit()
        #cursor.execute()
        db_conn.close()

    def remove_worklog_entry(self, worklog_entry):
        db_conn, cursor = self._connect_to_db()
        cursor.execute('DELETE from {worklogs} WHERE worklog_id = ?'.format(worklogs=self.WORKLOG_TABLE_NAME),
                       (worklog_entry.worklog_id,))
        db_conn.commit()
        db_conn.close()

    def update_worklog_entry(self, worklog):
        pass

    def get_day_worklog(self, day):
        pass

    def get_all_issues(self):
        pass
