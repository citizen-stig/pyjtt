#!/usr/bin/env python2

__author__ = 'stig'

import unittest, os, sys, ConfigParser, logging, datetime
from urllib2 import HTTPError

# add folder concat
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

print sys.path

from rest_wrapper import *

class pyjttTestJiraIssue(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG)
        config = ConfigParser.ConfigParser()
        config.read('test.cfg')
        if config:
            try:
                self.jirahost = config.get('jira', 'host')
                self.jirauser = config.get('jira', 'user')
                self.password = config.get('jira', 'password')
                self.display_name = config.get('jira', 'display_name')
                self.empty_issue_key = config.get('jira', 'empty_issue')
                self.nonempty_issue_key = config.get('jira', 'nonempty_issue')
                self.email = config.get('jira', 'email')
            except ConfigParser.NoSectionError as e:
                logging.error('Section %s is missed in configuration file!' % e[0])
                sys.exit(1)
            except ConfigParser.NoOptionError as e:
                logging.error('Option %s is missed in configuration file!' % e[0])
                sys.exit(1)
        else:
            logging.error('Error, no config file, exit')
            sys.exit(1)

    def test_init(self):
        self.assertTrue(JIRAIssue(self.jirahost, self.jirauser, self.password, self.nonempty_issue_key))

    def test_add_worklog(self):
        jissue = JIRAIssue(self.jirahost, self.jirauser, self.password, 'PERF-282')
        for w, r in jissue.worklog.iteritems():
            print w, r
        nw = jissue.add_worklog(datetime.datetime(2012, 12, 01, 14, 00), datetime.datetime(2012, 12, 01, 16, 00), 'Test from python')
        self.assertEqual(nw['comment'], 'Test from python')
        for w in jissue.worklog.iteritems():
            print w, r
        jissue.update_worklog(nw['id'], datetime.datetime(2012, 12, 02, 14, 00), datetime.datetime(2012, 12, 02, 16, 00), 'Updated from python' )
        self.assertEqual(jissue.worklog[nw['id']][2], 'Updated from python')
        for w in jissue.worklog.iteritems():
            print w, r
        jissue.remove_worklog(nw['id'])
        self.assertTrue(nw['id'] not in jissue.worklog)
        for w in jissue.worklog.iteritems():
            print w, r

if __name__ == '__main__':
    unittest.main()