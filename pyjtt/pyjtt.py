#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'


import os, sys, logging

from urllib2 import HTTPError
import db, utils
from rest_wrapper import *

#only for console
import getpass

def get_issue_from_jira(creds, issue_key):
    try:
        issue = JIRAIssue(creds[0], creds[1], creds[2], issue_key, new=True)
    except HTTPError:
        logging.error('HTTP Error')
        return
    db.add_issue(creds[3],
        creds[4],
        issue.issue_id,
        issue.issue_key,
        issue.summary)
    db.add_issue_worklog(creds[3], creds[4], issue.worklog, issue.issue_id)
    logging.debug('Info for issue %s is saved' % issue_key)
    return issue


def add_worklog(creds, issue, start_date, end_date, comment=None):
    try:
        added_worklog = issue.add_worklog(start_date, end_date, comment)
    except HTTPError:
        logging.error('HTTP Error')
        return
    db.add_issue_worklog(creds[3], creds[4], added_worklog, issue.issue_id)


def remove_worklog(creds, issue, worklog_id):
    try:
        issue.remove_worklog(worklog_id)
    except HTTPError:
        logging.error('HTTP Error')
        return
    db.remove_issue_worklog(creds[3], creds[4], worklog_id)


def update_worklog(creds, issue, worklog_id, start_date=None, end_date=None, comment=None):
    updated_worklog = issue.update_worklog(worklog_id, start_date, end_date, comment)
    db.update_worklog = (creds[3], creds[4], updated_worklog[0], updated_worklog[1][0], updated_worklog[1][2], updated_worklog[1][2])


def normal_exit(db_conn):
    logging.debug('Closing worklog database')
    db_conn.close()

def main():
    logging.debug('Starting')
    # base constants
    config_filename = 'test.cfg'
    jira_issues = {}

    # STARTING
    if not os.path.isfile(config_filename):
        logging.debug('First start')
        jirahost = raw_input("Enter jira URL: ")
        login = raw_input("Enter login: ")
        password = getpass.getpass("Enter password: ")
        creds = (jirahost, login, password )
        # TODO: add test request of user name for checking correct password
        #
        logging.debug('Creating local database')
        db_conn, cursor = db.create_local_db(utils.get_db_filename(login, jirahost))
    else:
        logging.debug('Read settings')
        jirahost, login, password = utils.get_settings(config_filename)
        db_conn, cursor = db.connect_to_db(utils.get_db_filename(login, jirahost))
        logging.debug('Load issues to memory')
        raw_issues = db.get_all_issues(cursor)
        for issue_entry in raw_issues:
            issue = JIRAIssue(jirahost, login, password, issue_entry[1])
            issue.issue_id = issue_entry[0]
            issue.summary = issue_entry[2]
            issue.worklog = db.get_issue_worklog(cursor, issue.issue_id)
            jira_issues[issue.issue_key] = issue
        logging.debug('Issues have been loaded')

    creds = ( jirahost, login, password, db_conn, cursor )
    while True:
        print '1 - print current username'
        print '2 - get worklog for issue'
        print '3 - add worklog for issue'
        print '4 - remove worklog from issue'
        print '5 - update worklog from issue'
        print '6 - get worklog for a day'
        print '9 - exit'
        action = raw_input("Enter action number: ")
        if action == '9':
            break
        elif action == '1':
            print 'Not supported yet'
        elif action == '2':
            issue_key = raw_input("Enter issue key: ").upper()
            if issue_key not in jira_issues:
                issue = get_issue_from_jira(creds, issue_key)
                jira_issues[issue_key] = issue
            for w, r in jira_issues[issue_key].worklog.iteritems():
                print w, r
        elif action == '3':
            issue_key = raw_input("Enter issue key: ").upper()
            if issue_key in jira_issues:
                issue = jira_issues[issue_key]
            else:
                issue = get_issue_from_jira(creds, issue_key)
                jira_issues[issue_key] = issue
            start_time_str = raw_input("Enter start time[%Y-%m-%dT%H:%M:%S]: ")
            end_time_str = raw_input("Enter end time[%Y-%m-%dT%H:%M:%S]: ")
            comment = raw_input('Comment: ')
            start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S')
            add_worklog(creds, issue, start_time, end_time, comment)
        elif action == '4':
            issue_key = raw_input("Enter issue key: ").upper()
            if issue_key in jira_issues:
                issue = jira_issues[issue_key]
            else:
                logging.error('Add issue first')
                continue
            worklog_id = int(raw_input("Enter worklog_id: "))
            remove_worklog(creds, issue, worklog_id)
        elif action == '5':
            issue_key = raw_input("Enter issue key: ").upper()
            if issue_key in jira_issues:
                issue = jira_issues[issue_key]
            else:
                continue
            worklog_id = int(raw_input("Enter worklog_id: "))
            start_time_str = raw_input("Enter start time[%Y-%m-%dT%H:%M:%S]: ")
            end_time_str = raw_input("Enter end time[%Y-%m-%dT%H:%M:%S]: ")
            comment = raw_input('Comment: ')
            if start_time_str:
                start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S')
            else:
                start_time = None
            if end_time_str:
                end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S')
            else:
                end_time = None
            update_worklog(creds, issue, worklog_id, start_time, end_time, comment)
        elif action == '6':
            selected_day = raw_input("Enter day[%Y-%m-%d]: ")
            day_work = db.get_day_worklog(creds[4], selected_day)
            for entry in day_work:
                print entry

    # NORMAL exit
    utils.save_settings(config_filename, creds)
    normal_exit(db_conn)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    main()