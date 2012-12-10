#!/usr/bin/env python
#
__author__ = 'Nikolay Golub'

import os, sys, ConfigParser, logging, datetime
from urllib2 import HTTPError
from rest_wrapper import *

def get_settings():
    logging.debug('Getting base options')
    config = ConfigParser.ConfigParser()
    config_filename = 'test.cfg'
    if os.path.isfile(config_filename):
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
        logging.debug('Options have been read')
    else:
        jirahost = raw_input("Enter jira URL: ")
        login = raw_input("Enter login: ")
        password = raw_input("Enter password: ")
        config.add_section('jira')
        config.set('jira', 'host', jirahost)
        config.set('jira', 'login', login)
        config.set('jira', 'password', password)
        with open(config_filename, 'wb') as configfile:
            config.write(configfile)
    return jirahost, login, password


def get_action(creds, issue_key):
    try:
        issue = JIRAIssue(creds[0], creds[1], creds[2], issue_key, new=True)
    except HTTPError:
        logging.error('HTTP Error')
        return
    for w, r in issue.worklog.iteritems():
        print w, r



def main():
    creds = get_settings()
    while True:
        print '1 - print current username'
        print '2 - get worklog for issue'
        print '9 - exit'
        action = raw_input("Enter action number: ")
        if action == '9':
            sys.exit()
        elif action == '1':
            print 'Not supported yet'
        elif action == '2':
            issue_key = raw_input("Enter issue key: ")
            get_action(creds, issue_key)




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    main()