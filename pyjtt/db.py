#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'


import datetime, sqlite3, logging


def convert_to_datetime(datetime_string):
    timeformat = '%Y-%m-%d %H:%M:%S'
    return datetime.datetime.strptime(datetime_string, timeformat)


def create_local_db(db_filename):
    db_conn = sqlite3.connect(db_filename)
    cursor = db_conn.cursor()
    logging.debug('Creating table JIRAIssues')
    cursor.execute("""CREATE TABLE if not exists JIRAIssues
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT,
                        link TEXT)""")
    logging.debug('Creating table worklogs')
    cursor.execute("""CREATE TABLE if not exists Worklogs
                        (worklog_id INTEGER,
                         jira_issue_id INTEGER,
                         comment TEXT,
                         start_date TIMESTAMP,
                         end_date TIMESTAMP)""")
    db_conn.commit()
    logging.debug('Tables created')
    return db_conn, cursor


def connect_to_db(db_filename):
    logging.debug('Connecting to local Database: %s' % db_filename)
    db_conn = sqlite3.connect(db_filename)
    cursor = db_conn.cursor()
    logging.debug('Connection successfull')
    return db_conn, cursor


def add_issue(db_conn, cursor, issue_id, issue_key, issue_summary):
    logging.debug('Save issue to local db')
    cursor.execute('INSERT INTO '
                     'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
                     'VALUES (?,?,?)', (issue_id, issue_key, issue_summary))
    db_conn.commit()

def get_issue(cursor):
    pass

def get_issue_worklog(cursor, issue_id):
    logging.debug('Fetching issue worklogs')
    worklogs = {}
    cursor.execute('SELECT worklog_id, start_date, end_date, comment FROM Worklogs WHERE jira_issue_id = ?', (issue_id,))
    raw_worklogs = cursor.fetchall()
    for worklog_entry in raw_worklogs:
        start_date = convert_to_datetime(worklog_entry[1])
        end_date = convert_to_datetime(worklog_entry[2])
        worklogs[worklog_entry[0]] = (start_date, end_date, worklog_entry[3])

    logging.debug('Worklogs have been fetched')
    return worklogs



def add_issue_worklog(db_conn, cursor, worklog, issue_id):
    logging.debug('Save worklogs')
    rows = [ [x[0]] + [issue_id] + list(x[1]) for x in worklog.items()]
    cursor.executemany("""INSERT INTO Worklogs (worklog_id, jira_issue_id, start_date, end_date, comment)
                                    VALUES (?,?,?,?,?)""", rows)
    db_conn.commit()


def remove_issue_worklog(db_conn,cursor, worklog_id):
    logging.debug('Deleting worklog %s' % str(worklog_id))
    cursor.execute('DELETE from Worklogs WHERE worklog_id = ?', (worklog_id,))
    db_conn.commit()
    logging.debug('Worklog has been deleted')

def update_issue_worklog(db_conn, cursor, worklog_id, start_date, end_date, comment):
    logging.debug('Update worklog %s in local db')
    cursor.execute("""
                    UPDATE  Worklogs
                    SET start_date = ?
                        end_date = ?
                        comment = ?
                    WHERE
                        worklog_id = ?
                    """, (start_date, end_date, comment, worklog_id) )
    db_conn.commit()
    logging.debug('Worklog Updated')

def get_day_worklog(cursor, selected_day):
    logging.debug('Get worklog for %s' % selected_day)
    worklogs = []
    cursor.execute("""
                    SELECT
                        JIRAIssues.jira_issue_key,
                        JIRAIssues.summary,
                        Worklogs.start_date,
                        Worklogs.end_date
                    FROM
                        Worklogs
                    JOIN JIRAIssues on Worklogs.jira_issue_id = JIRAIssues.jira_issue_id
                    WHERE
                        Worklogs.start_date like ?
                        OR Worklogs.end_date  like ?
                    """, (selected_day+'%', selected_day+'%'))
    logging.debug('Worklog Returned')
    raw_worklogs = cursor.fetchall()
    for worklog_entry in raw_worklogs:
        start_date = convert_to_datetime(worklog_entry[2])
        end_date = convert_to_datetime(worklog_entry[3])
        worklogs.append((worklog_entry[0], worklog_entry[1], start_date, end_date))
    return worklogs

def get_all_issues(cursor):
    cursor.execute('SELECT jira_issue_id, jira_issue_key, summary FROM JIRAIssues')
    return cursor.fetchall()
