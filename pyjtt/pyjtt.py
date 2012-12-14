#!/usr/bin/env python
#
__author__ = 'Nikolay Golub'

import os, sys, ConfigParser, logging, datetime, sqlite3
from urllib2 import HTTPError
from rest_wrapper import *

def get_settings(config_filename):
    logging.debug('Getting base options')
    config = ConfigParser.ConfigParser()
    logging.debug('Config file exists, read options')
    config.read(config_filename)
    try:
        jirahost = config.get('jira', 'host')
        login = config.get('jira', 'login')
        password = config.get('jira', 'password')
    except ConfigParser.NoSectionError as e:
        logging.error('Section %s is missed in configuration file!' % e[0])
        sys.exit(1)
    except ConfigParser.NoOptionError as e:
        logging.error('Option %s is missed in configuration file!' % e[0])
        sys.exit(1)
    logging.debug('Options have been red')
        #config.add_section('jira')
        #config.set('jira', 'host', jirahost)
        #config.set('jira', 'login', login)
        #config.set('jira', 'password', password)
        #with open(config_filename, 'wb') as configfile:
            #config.write(configfile)
    return jirahost, login, password

def save_settings(config_filename, creds):
    logging.debug('Saving configuration')
    config = ConfigParser.ConfigParser()
    config.add_section('jira')
    config.set('jira', 'host', creds[0])
    config.set('jira', 'login', creds[1])
    config.set('jira', 'password', creds[2])
    with open(config_filename, 'wb') as configfile:
        config.write(configfile)
    logging.debug('Options have been saved')

def get_db_filename(login, jirahost):
    # TODO: add absolute path handling
    return login + '_' + jirahost.replace('http://', '').replace('/','').replace(':', '')\
           + '.db'

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


def get_action(creds, issue_key):
    try:
        issue = JIRAIssue(creds[0], creds[1], creds[2], issue_key, new=True)
    except HTTPError:
        logging.error('HTTP Error')
        return
    logging.debug('Save issue to local db')
    logging.debug('Save issue info')
    creds[4].execute('INSERT INTO '
                     'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
                     'VALUES (?,?,?)', (issue.issue_id, issue.issue_key, issue.summary))
    logging.debug('Save worklogs')
    for w, r in issue.worklog.iteritems():
        #print w, r[0], r[1], r[2]
        creds[4].execute("""INSERT INTO Worklogs (worklog_id, jira_issue_id, comment, start_date, end_date)
                                    VALUES (?,?,?,?,?)""", (w, issue.issue_id, r[2], r[0], r[1]))
    creds[3].commit()
    return issue



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
        password = raw_input("Enter password: ")
        creds = (jirahost, login, password )
        # TODO: add test request of user name for checking correct password
        #
        logging.debug('Creating local database')
        db_conn, cursor = create_local_db(get_db_filename(login, jirahost))
    else:
        logging.debug('Read settings')
        jirahost, login, password = get_settings(config_filename)
        logging.debug('Connect to local database')
        db_conn = sqlite3.connect(get_db_filename(login, jirahost))
        cursor = db_conn.cursor()
        logging.debug('Load Issue to memory')
        # TODO: add loading jira issues to memory

    creds = ( jirahost, login, password, db_conn, cursor )
    while True:
        print '1 - print current username'
        print '2 - get worklog for issue'
        print '9 - exit'
        action = raw_input("Enter action number: ")
        if action == '9':
            break
        elif action == '1':
            print 'Not supported yet'
        elif action == '2':
            issue_key = raw_input("Enter issue key: ")
            if issue_key not in jira_issues:
                issue = get_action(creds, issue_key)
                jira_issues[issue_key] = issue
            for w, r in jira_issues[issue_key].worklog.iteritems():
                print w, r



    # NORMAL exit
    save_settings(config_filename, creds)
    normal_exit(db_conn)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    main()