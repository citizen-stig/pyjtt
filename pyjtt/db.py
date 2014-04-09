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
__copyright__ = "Copyright 2012 - 2013, Nikolay Golub"
__license__ = "GPL"

import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

from .base_classes import JiraIssue


class DBAccessor(object):
    TIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    CREATE_ISSUES_TABLE_SQL = """CREATE TABLE IF NOT EXISTS JIRAIssues
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT)"""
    CREATE_WORKLOGS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS Worklogs
                        (worklog_id INTEGER,
                         jira_issue_id INTEGER,
                         comment TEXT,
                         start_date TIMESTAMP,
                         end_date TIMESTAMP)"""

    def __init__(self, db_filename):
        self.db_filename = db_filename

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

    def add_issue(self, issue):
        logger.debug('Saving issue %s in local DB' % issue.key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('INSERT INTO '
                       'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
                       'VALUES (?,?,?)', (issue.issue_id, issue.key, issue.summary))
        db_conn.commit()
        db_conn.close()
        logger.debug('Issue %s has been saved in local DB')

    def remove_issue(self, issue):
        logger.debug('Removing issue %s from local DB' % issue.key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('DELETE FROM Worklogs '
                   'WHERE jira_issue_id = (SELECT jira_issue_id '
                                          'FROM JIRAIssues '
                                          'WHERE jira_issue_key = ?)', (issue.key,))
        cursor.execute('DELETE FROM JIRAIssues '
                    'WHERE jira_issue_key = ?', (issue.key,))
        db_conn.commit()
        db_conn.close()
        logger.debug('Issue %s has been remove from local DB' % issue_key)

    def get_issue(self, issue_key):
        logger.debug('Getting issue %s from local DB' % issue_key)
        db_conn, cursor = connect_to_db(db_filename)
        cursor.execute('SELECT * FROM JIRAIssues where jira_issue_key = ?', (issue_key,))
        issue = cursor.fetchone()
        db_conn.close()
        try:
            issue = JiraIssue(issue)
            logger.debug('Issue %s has been extracted from local DB')
            return issue
        except sqlite3.DatabaseError:
            # TODO: move to the normal exception
            pass

    def get_worklogs_for_issue(self, issue_key):
        pass

    def add_worklog(self, issue_key, worklog):
        pass

    def remove_worklog(self, worklog_id):
        pass

    def update_worklog(self, worklog_id):
        pass

    def get_day_worklogs(self, day):
        pass

    def get_all_issues(self):
        pass
# All that is below is old
# ======
#
# def convert_to_datetime(datetime_string):
#     timeformat = '%Y-%m-%d %H:%M:%S'
#     return datetime.datetime.strptime(datetime_string, timeformat)
#
#
# def create_local_db(db_filename):
#     logger.debug('Creating db %s' % db_filename)
#     db_conn = sqlite3.connect(str(db_filename))
#     cursor = db_conn.cursor()
#     logger.debug('Creating table JIRAIssues')
#     cursor.execute("""CREATE TABLE if not exists JIRAIssues
#                         (jira_issue_id INTEGER PRIMARY KEY,
#                         jira_issue_key TEXT,
#                         summary TEXT)""")
#     logger.debug('Creating table worklogs')
#     cursor.execute("""CREATE TABLE if not exists Worklogs
#                         (worklog_id INTEGER,
#                          jira_issue_id INTEGER,
#                          comment TEXT,
#                          start_date TIMESTAMP,
#                          end_date TIMESTAMP)""")
#     db_conn.commit()
#     logger.debug('Tables created')
#     return db_conn, cursor
#
#
# def connect_to_db(db_filename):
#     logger.debug('Connecting to local DB: %s' % db_filename)
#     db_conn = sqlite3.connect(db_filename,  timeout=30)
#     cursor = db_conn.cursor()
#     logger.debug('Connection has been successfull')
#     return db_conn, cursor
#
#
# def add_issue(db_filename, issue_id, issue_key, issue_summary):
#     logger.debug('Saving issue %s in local DB' % issue_key)
#     db_conn, cursor = connect_to_db(db_filename)
#     cursor.execute('INSERT INTO '
#                      'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
#                      'VALUES (?,?,?)', (issue_id, issue_key, issue_summary))
#     db_conn.commit()
#     db_conn.close()
#     logger.debug('Issue %s has been saved in local DB')
#
#
# def remove_issue(db_filename, issue_key):
#     logger.debug('Removing issue %s from local DB' % issue_key)
#     db_conn, cursor = connect_to_db(db_filename)
#     cursor.execute('DELETE FROM Worklogs '
#                    'WHERE jira_issue_id = (SELECT jira_issue_id '
#                                           'FROM JIRAIssues '
#                                           'WHERE jira_issue_key = ?)', (issue_key,))
#     cursor.execute('DELETE FROM JIRAIssues '
#                    'WHERE jira_issue_key = ?', (issue_key,))
#     db_conn.commit()
#     db_conn.close()
#     logger.debug('Issue %s has been remove from local DB' % issue_key)
#
#
# def get_issue(db_filename, issue_key):
#     logger.debug('Getting issue %s from local DB' % issue_key)
#     db_conn, cursor = connect_to_db(db_filename)
#     cursor.execute('SELECT * FROM JIRAIssues where jira_issue_key = ?', (issue_key,))
#     issue = cursor.fetchone()
#     db_conn.close()
#     if issue:
#         logger.debug('Issue %s has been extracted from local DB')
#         return issue
#
#
# def get_issue_worklog(db_filename, issue_id):
#     logger.debug('Fetching worklogs for issue with id %s from local DB' % str(issue_id))
#     db_conn, cursor = connect_to_db(db_filename)
#     worklog = {}
#     cursor.execute('SELECT worklog_id, start_date, end_date, comment FROM Worklogs WHERE jira_issue_id = ?', (issue_id,))
#     raw_worklog = cursor.fetchall()
#     db_conn.close()
#     for worklog_entry in raw_worklog:
#         start_date = convert_to_datetime(worklog_entry[1])
#         end_date = convert_to_datetime(worklog_entry[2])
#         worklog[worklog_entry[0]] = (start_date, end_date, worklog_entry[3])
#     logger.debug('Worklogs have been fetched from local DB for issue with id %s' % str(issue_id))
#     return worklog
#
#
# def add_issue_worklog(db_filename, worklog, issue_id):
#     logger.debug('Add new worklog to local DB for issue with id %s' % str(issue_id))
#     if worklog:
#         db_conn, cursor = connect_to_db(db_filename)
#         rows = [ [x[0]] + [issue_id] + list(x[1]) for x in worklog.items()]
#         cursor.executemany("""INSERT INTO Worklogs (worklog_id, jira_issue_id, start_date, end_date, comment)
#                                         VALUES (?,?,?,?,?)""", rows)
#         db_conn.commit()
#         logger.debug('Worklog %s has been saved in local DB' % str(rows[0][0]))
#         db_conn.close()
#     else:
#         logger.debug('Worklog is empty, nothing to save')
#
#
# def remove_issue_worklog(db_filename, worklog_id):
#     logger.debug('Deleting worklog %s from local DB' % str(worklog_id))
#     db_conn, cursor = connect_to_db(db_filename)
#     cursor.execute('DELETE from Worklogs WHERE worklog_id = ?', (worklog_id,))
#     db_conn.commit()
#     db_conn.close()
#     logger.debug('Worklog has been deleted from local DB')
#
#
# def update_issue_worklog(db_filename, worklog_id, start_date, end_date, comment):
#     logger.debug('Updating worklog %s in local db' % str(worklog_id))
#     db_conn, cursor = connect_to_db(db_filename)
#     logger.debug('New data is: %s, %s, %s' % (str(start_date), str(end_date), comment) )
#     cursor.execute("""
#                     UPDATE  Worklogs
#                     SET start_date = ?,
#                         end_date = ?,
#                         comment = ?
#                     WHERE
#                         worklog_id = ?
#                     """, (start_date, end_date, comment, worklog_id) )
#     db_conn.commit()
#     db_conn.close()
#     logger.debug('Worklog %s has been updated in local DB' % str(worklog_id))
#
#
# def get_day_worklog(db_filename, selected_day):
#     logger.debug('Getting worklog for %s from local DB' % selected_day)
#     db_conn, cursor = connect_to_db(db_filename)
#     worklog = []
#     cursor.execute("""
#                     SELECT
#                         JIRAIssues.jira_issue_key,
#                         JIRAIssues.summary,
#                         Worklogs.start_date,
#                         Worklogs.end_date,
#                         Worklogs.worklog_id
#                     FROM
#                         Worklogs
#                     JOIN JIRAIssues on Worklogs.jira_issue_id = JIRAIssues.jira_issue_id
#                     WHERE
#                         Worklogs.start_date like (?)
#                     """, (selected_day.strftime('%Y-%m-%d') + '%',))
#     raw_worklog = cursor.fetchall()
#     db_conn.close()
#     for worklog_entry in raw_worklog:
#         start_date = convert_to_datetime(worklog_entry[2])
#         end_date = convert_to_datetime(worklog_entry[3])
#         worklog.append((worklog_entry[0], worklog_entry[1], start_date, end_date, worklog_entry[4]))
#     logger.debug('Day worklog has been returned for %s' % selected_day)
#     # TODO: return tuple
#     return worklog
#
#
# def get_all_issues(db_filename):
#     logger.debug('Getting all issues from local DB')
#     db_conn, cursor = connect_to_db(db_filename)
#     cursor.execute('SELECT jira_issue_id, jira_issue_key, summary FROM JIRAIssues')
#     all_issues = cursor.fetchall()
#     db_conn.close()
#     logger.debug('All issues have been extracted from local DB')
#     return all_issues
