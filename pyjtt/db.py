#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import datetime, sqlite3, logging

def convert_to_datetime(datetime_string):
    timeformat = '%Y-%m-%d %H:%M:%S'
    return datetime.datetime.strptime(datetime_string, timeformat)

def create_local_db(db_filename):
    logging.debug('Creating db %s' % db_filename)
    db_conn = sqlite3.connect(str(db_filename))
    cursor = db_conn.cursor()
    logging.debug('Creating table JIRAIssues')
    cursor.execute("""CREATE TABLE if not exists JIRAIssues
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT)""")
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

def add_issue(db_filename, issue_id, issue_key, issue_summary):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Save issue to local db')
    cursor.execute('INSERT INTO '
                     'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
                     'VALUES (?,?,?)', (issue_id, issue_key, issue_summary))
    db_conn.commit()
    db_conn.close()

def remove_issue(db_filename, issue_key):
    db_conn, cursor = connect_to_db(db_filename)
    print db_filename
    logging.debug('Removing worklogs for issue %s' % str(issue_key))
    cursor.execute('DELETE FROM Worklogs '
                   'WHERE jira_issue_id = (SELECT jira_issue_id '
                                          'FROM JIRAIssues '
                                          'WHERE jira_issue_key = ?)', (issue_key,))
    cursor.execute('DELETE FROM JIRAIssues '
                   'WHERE jira_issue_key = ?', (issue_key,))
    db_conn.commit()
    db_conn.close()

def get_issue(db_filename, issue_key):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Getting issue %s' % issue_key)
    cursor.execute('SELECT * FROM JIRAIssues where jira_issue_key = ?', (issue_key,))
    issue = cursor.fetchone()
    if issue:
        return issue
    db_conn.close()


def get_issue_worklog(db_filename, issue_id):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Fetching issue worklogs')
    worklog = {}
    cursor.execute('SELECT worklog_id, start_date, end_date, comment FROM Worklogs WHERE jira_issue_id = ?', (issue_id,))
    raw_worklog = cursor.fetchall()
    for worklog_entry in raw_worklog:
        start_date = convert_to_datetime(worklog_entry[1])
        end_date = convert_to_datetime(worklog_entry[2])
        worklog[worklog_entry[0]] = (start_date, end_date, worklog_entry[3])

    logging.debug('Worklogs have been fetched')
    db_conn.close()
    return worklog

def add_issue_worklog(db_filename, worklog, issue_id):
    if worklog:
        db_conn, cursor = connect_to_db(db_filename)
        logging.debug('Add new worklog to local DB')
        rows = [ [x[0]] + [issue_id] + list(x[1]) for x in worklog.items()]
        cursor.executemany("""INSERT INTO Worklogs (worklog_id, jira_issue_id, start_date, end_date, comment)
                                        VALUES (?,?,?,?,?)""", rows)
        db_conn.commit()
        logging.debug('Worklog %s has been saved in local DB' % str(rows[0][0]))
        db_conn.close()
    else:
        logging.debug('Worklog is empty, nothing to save')

def remove_issue_worklog(db_filename, worklog_id):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Deleting worklog %s' % str(worklog_id))
    cursor.execute('DELETE from Worklogs WHERE worklog_id = ?', (worklog_id,))
    db_conn.commit()
    logging.debug('Worklog has been deleted')
    db_conn.close()

def update_issue_worklog(db_filename, worklog_id, start_date, end_date, comment):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Updating worklog %s in local db' % str(worklog_id))
    logging.debug('New data is: %s, %s, %s' % (str(start_date), str(end_date), comment) )
    cursor.execute("""
                    UPDATE  Worklogs
                    SET start_date = ?,
                        end_date = ?,
                        comment = ?
                    WHERE
                        worklog_id = ?
                    """, (start_date, end_date, comment, worklog_id) )
    db_conn.commit()
    logging.debug('Worklog %s Updated in local database' % str(worklog_id))
    db_conn.close()

def get_day_worklog(db_filename, selected_day):
    db_conn, cursor = connect_to_db(db_filename)
    logging.debug('Get worklog for %s' % selected_day)
    worklog = []
    cursor.execute("""
                    SELECT
                        JIRAIssues.jira_issue_key,
                        JIRAIssues.summary,
                        Worklogs.start_date,
                        Worklogs.end_date,
                        Worklogs.worklog_id
                    FROM
                        Worklogs
                    JOIN JIRAIssues on Worklogs.jira_issue_id = JIRAIssues.jira_issue_id
                    WHERE
                        Worklogs.start_date like (?)
                    """, (selected_day.strftime('%Y-%m-%d') + '%',))
    logging.debug('Worklog Returned')
    raw_worklog = cursor.fetchall()
    for worklog_entry in raw_worklog:
        start_date = convert_to_datetime(worklog_entry[2])
        end_date = convert_to_datetime(worklog_entry[3])
        worklog.append((worklog_entry[0], worklog_entry[1], start_date, end_date, worklog_entry[4]))
    db_conn.close()
    # TODO: add sorting by start_time
    return worklog

def get_all_issues(db_filename):
    db_conn, cursor = connect_to_db(db_filename)
    cursor.execute('SELECT jira_issue_id, jira_issue_key, summary FROM JIRAIssues')
    all_issues = cursor.fetchall()
    db_conn.close()
    return all_issues
