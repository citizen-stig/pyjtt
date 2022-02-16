from datetime import datetime
import sqlite3
import logging

from pyjtt.base_classes import JiraIssue, JiraWorklogEntry

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"

logger = logging.getLogger(__name__)


class DBAccessor(object):
    TIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    ISSUES_TABLE_NAME = 'JIRAIssues'
    WORKLOG_TABLE_NAME = 'Worklogs'
    CREATE_ISSUES_TABLE_SQL = """CREATE TABLE IF NOT EXISTS {issues_table_name}
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT)""".format(
        issues_table_name=ISSUES_TABLE_NAME)
    CREATE_WORKLOGS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS {worklog}
                        (worklog_id INTEGER PRIMARY KEY,
                         jira_issue_id INTEGER,
                         comment TEXT,
                         start_date TIMESTAMP,
                         end_date TIMESTAMP)""".format(
        worklog=WORKLOG_TABLE_NAME)

    def __init__(self, db_filename):
        self.db_filename = db_filename
        db_conn, cursor = self._connect_to_db()
        tables = cursor.execute('SELECT name FROM sqlite_master '
                                'WHERE type="table" '
                                'AND name="{issues_table}";'.format(
            issues_table=self.ISSUES_TABLE_NAME))
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
        logger.debug('Connecting to local DB: %s', self.db_filename)
        db_conn = sqlite3.connect(self.db_filename, timeout=10,
                                  check_same_thread=False)
        cursor = db_conn.cursor()
        logger.debug('Connection has been successful')
        return db_conn, cursor

    def _convert_to_datetime(self, datetime_string):
        return datetime.strptime(datetime_string, self.TIMEFORMAT)

    @staticmethod
    def _parse_raw_issue(row):
        return JiraIssue(str(row[0]), row[1], row[2])

    def _parse_raw_worklog_entry(self, issue, row):
        started = self._convert_to_datetime(row[1])
        ended = self._convert_to_datetime(row[2])
        return JiraWorklogEntry(issue, started, ended, row[3], str(row[0]))

    def add_issue(self, issue):
        logger.debug('Saving issue "{0}" in local DB. '
                     'Id: {1}'.format(issue.key, issue.issue_id))
        db_conn, cursor = self._connect_to_db()
        cursor.execute(
            'INSERT OR REPLACE INTO '
            '{issues_table} (jira_issue_id, jira_issue_key, summary) '
            'VALUES (?,?,?);'.format(issues_table=self.ISSUES_TABLE_NAME),
            (issue.issue_id, issue.key, issue.summary))
        db_conn.commit()
        db_conn.close()
        logger.debug(
            'Issue "{0}" has been saved in local DB'.format(issue.key))

    def remove_issue(self, issue):
        logger.debug('Removing issue %s from local DB', issue.key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('DELETE FROM Worklogs '
                       'WHERE jira_issue_id = '
                       '(SELECT jira_issue_id FROM JIRAIssues '
                       'WHERE jira_issue_key = ?)', (issue.key,))
        cursor.execute('DELETE FROM JIRAIssues '
                       'WHERE jira_issue_key = ?', (issue.key,))
        db_conn.commit()
        db_conn.close()
        logger.debug('Issue %s has been remove from local DB', issue.key)

    def get_issue(self, issue_key):
        logger.debug('Getting issue %s from local DB', issue_key)
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT jira_issue_id, jira_issue_key, summary '
                       'FROM JIRAIssues WHERE jira_issue_key = ?',
                       (issue_key,))
        raw_issue = cursor.fetchone()
        db_conn.close()
        try:
            issue = self._parse_raw_issue(raw_issue)
            logger.debug('Issue %s has been extracted from local DB')
            return issue
        except TypeError:
            logger.debug('Issue is not found in local DB')

    def get_worklog_for_issue(self, issue):
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT worklog_id, start_date, end_date, comment '
                       'FROM {worklog} WHERE jira_issue_id = ?'.format(
            worklog=self.WORKLOG_TABLE_NAME),
                       (issue.issue_id,))
        for raw_worklog_entry in cursor.fetchall():
            yield self._parse_raw_worklog_entry(issue, raw_worklog_entry)

    def add_worklog(self, worklog):

        rows = [(x.worklog_id, x.issue.issue_id, x.started, x.ended, x.comment)
                for x in worklog]
        if rows:
            logger.debug('Save worklog in local db.'
                         ' First issue in bulk set is {0}'.format(
                worklog[0].issue.key))
            db_conn, cursor = self._connect_to_db()
            cursor.executemany('INSERT OR REPLACE INTO {worklog}'
                               ' (worklog_id, jira_issue_id,'
                               ' start_date, end_date, comment)'
                               'VALUES (?,?,?,?,?)'.format(
                worklog=self.WORKLOG_TABLE_NAME), rows)
            db_conn.commit()
            db_conn.close()
            logger.debug('Bulk worklog saving is completed')

    def add_worklog_entry(self, worklog_entry):
        logger.debug('Saving worklog entry '
                     'for issue {0}'.format(worklog_entry.issue))
        db_conn, cursor = self._connect_to_db()
        cursor.execute(
            'INSERT INTO {worklog} (worklog_id, jira_issue_id, start_date, end_date, comment)'
            'VALUES (?,?,?,?,?)'.format(worklog=self.WORKLOG_TABLE_NAME),
            (worklog_entry.worklog_id,
             worklog_entry.issue.issue_id,
             worklog_entry.started,
             worklog_entry.ended,
             worklog_entry.comment))
        db_conn.commit()
        db_conn.close()

    def remove_worklog_entry(self, worklog_entry):
        db_conn, cursor = self._connect_to_db()
        cursor.execute('DELETE FROM {worklog} WHERE worklog_id = ?'.format(
            worklog=self.WORKLOG_TABLE_NAME),
                       (worklog_entry.worklog_id,))
        db_conn.commit()
        db_conn.close()

    def update_worklog_entry(self, worklog_entry):
        logger.debug('Updating worklog entry '
                     'for issue {0}'.format(worklog_entry.issue))
        db_conn, cursor = self._connect_to_db()
        cursor.execute('UPDATE {worklog} '
                       'SET '
                       'start_date = ?, '
                       'end_date = ?, '
                       'comment = ? '
                       'WHERE '
                       'worklog_id = ?'.format(
            worklog=self.WORKLOG_TABLE_NAME),
                       (worklog_entry.started, worklog_entry.ended,
                        worklog_entry.comment, worklog_entry.worklog_id))
        db_conn.commit()
        db_conn.close()

    def get_day_worklog(self, day):
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT '
                       '{issues}.jira_issue_id,'
                       '{issues}.jira_issue_key, '
                       '{issues}.summary, '
                       '{worklog}.worklog_id, '
                       '{worklog}.start_date, '
                       '{worklog}.end_date, '
                       '{worklog}.comment '
                       'FROM '
                       '{worklog} '
                       'INNER JOIN {issues} ON {issues}.jira_issue_id = {worklog}.jira_issue_id '
                       'WHERE '
                       '{worklog}.start_date LIKE (?) '.format(
            issues=self.ISSUES_TABLE_NAME,
            worklog=self.WORKLOG_TABLE_NAME),
                       (day.strftime('%Y-%m-%d') + '%',))
        for raw_entry in cursor.fetchall():
            issue = self._parse_raw_issue(raw_entry[:3])
            yield self._parse_raw_worklog_entry(issue, raw_entry[3:])

    def get_all_issues(self):
        db_conn, cursor = self._connect_to_db()
        cursor.execute('SELECT jira_issue_id, jira_issue_key, summary '
                       'FROM {issues}'.format(issues=self.ISSUES_TABLE_NAME))
        for raw_issue_data in cursor.fetchall():
            yield self._parse_raw_issue(raw_issue_data)
