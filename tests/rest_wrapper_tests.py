#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import urllib2, json, unittest, sys, logging, os, datetime
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import rest_wrapper
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

def parse_url(url):
    """return host, issue and worklogid(if presented)
    """
    host = None
    issue = None
    worklog = None
    url_list = url.split('/')
    for i in range(len(url_list)):
        if url_list[i] == 'issue':
            issue =  url_list[i+1]
        if url_list[i] == 'worklog':
            worklog = url_list[i+1]
    if url_list[0] == 'http:' or url_list[0] == 'https:':
        host = url_list[2]
    else:
        host = url_list[0]
    return host, issue, worklog


def get_random_worklog():
    pass

class JIRAIssue(rest_wrapper.JIRAIssue):
    def __init(self, jirahost, login, password, issue_key, new=False):
        rest_wrapper.JIRAIssue(jirahost, login, password, issue_key, new)

    def rest_req(self,url, data=None, req_type=None):
        known_issues = ('SAMPLE-1', 'SAMPLE-2', 'EMPTY-1', 'EMPTY-2')
        worklog_ids = ['1', '2', '3']
        host, issue, worklog = parse_url(url)
        if self.login != 'login' and self.password != 'secret':
            pass
            # TODO: produce deny error
        if host == 'jira.example.com':
            if issue in known_issues:
                issue_data = {'key': issue,
                              'id' : '123',
                              'fields':
                                        {'summary': 'Sample issue summary',
                                         'worklog' :
                                            {'worklogs' : [], 'total' : 0 }
                                        }
                             }
                if issue[:6] == 'SAMPLE':
                    worklog = { 'comment': 'Test comment',
                                'updated': '2013-01-09T02:48:20.000-0800',
                                'created': '2013-01-09T02:48:20.000-0800',
                                'started': '2013-01-16T02:47:00.000-0800',
                                'author':
                                    { 'name' : 'login',
                                      'displayName': u'Test User'
                                    },
                                'timeSpent': '3h',
                                'timeSpentSeconds': 10800,
                                'id': '1'}
                    issue_data['fields']['worklog']['worklogs'].append(worklog)
                    issue_data['fields']['worklog']['total'] += 1
                if issue == 'SAMPLE-2':
                    worklog = { 'comment': 'Test comment',
                                      'updated': '2013-01-07T03:48:20.000-0800',
                                      'created': '2013-01-07T03:48:20.000-0800',
                                      'started': '2013-01-07T03:48:00.000-0800',
                                      'author':
                                          { 'name' : 'login',
                                            'displayName': u'Test User'
                                          },
                                      'timeSpent': '4h 5m',
                                      'timeSpentSeconds': 14700,
                                      'id': '2'}
                    issue_data['fields']['worklog']['worklogs'].append(worklog)
                    issue_data['fields']['worklog']['total'] += 1
                if issue == 'EMPTY-2':
                    worklog = { 'comment': 'Test comment',
                                'updated': '2013-01-07T03:48:20.000-0800',
                                'created': '2013-01-07T03:48:20.000-0800',
                                'started': '2013-01-07T03:48:00.000-0800',
                                'author':
                                    { 'name' : 'some_user',
                                      'displayName': u'Some Test User'
                                    },
                                'timeSpent': '4h 5m',
                                'timeSpentSeconds': 14700,
                                'id': '3'}
                if req_type is None and data is None:
                    return issue_data
            else:
                raise urllib2.HTTPError(url, 404, 'Not Found', None, None)
                # produce error about now issue
        else:
            # produce error about no host
            return


class pyjttUtilsTest(unittest.TestCase):
    def setUp(self):
        self.jirahost = 'http://jira.example.com'
        self.login = 'login'
        self.password = 'password'

    def test_get_issue_normal(self):
        # easy sample - 1 worklog entry with comment
        issue_key = 'SAMPLE-1'
        expeceted_worklog = {1: (datetime.datetime(2013,1,16,14,47),
                                 datetime.datetime(2013,1,16,17,47),
                                 'Test comment')
                            }
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, expeceted_worklog)
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)

        # TODO: 2 worklogs
        issue_key = 'SAMPLE-2'
        expeceted_worklog[2] = (datetime.datetime(2013,1,7,15,48),
                                datetime.datetime(2013,1,7,19,53), 'Test comment')
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, expeceted_worklog)
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)
        # TODO: empty worklog comment


        # TODO: empty worklog
        issue_key = 'EMPTY-1'
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, {})
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)

        # TODO: no user worklog
        issue_key = 'EMPTY-2'
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, {})
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)

    def test_get_issue_errors(self):
        # TODO: wrong host

        # wrong issue ( not found or denied )
        with self.assertRaises(urllib2.HTTPError) as http_err:
            issue = JIRAIssue(self.jirahost, self.login, self.password, 'NONEXISTS-331', new=True)




if __name__ == '__main__':
    unittest.main()

