#!/usr/bin/env python2
__author__ = 'Nikolay Golub'

import unittest, os, sys, ConfigParser, logging, datetime
from urllib2 import HTTPError

# add folder concat
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

print sys.path

from rest_wrapper import *

class pyjttTestJiraRestBase(unittest.TestCase):
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

    def test_simple_init(self):
        self.assertTrue(
            JiraRestBase(self.jirahost, self.jirauser, self.password))

    def test_get_issue(self):
        issue_url = self.jirahost + '/rest/api/2/issue/' + self.nonempty_issue_key
        empty_issue_url = self.jirahost + '/rest/api/2/issue/' + self.empty_issue_key
        url_404 = self.jirahost + '/rest/api/2/issue/' + 'NONEXIST-387654'
        wrapper = JiraRestBase(self.jirahost, self.jirauser, self.password)
        self.assertTrue(wrapper.rest_req(issue_url))
        self.assertTrue(wrapper.rest_req(empty_issue_url))
        with self.assertRaises(HTTPError) as cm:
            wrapper.rest_req(url_404)
        err = cm.exception
        self.assertEqual(err.code, 404)





if __name__ == '__main__':
    unittest.main()