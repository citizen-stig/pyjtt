#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import urllib2, json, unittest, sys, logging, os, datetime, random
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import rest_wrapper, utils
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

WORKLOG_ID = 100
PREVIOUS_W_IDS = [1, 2, 3, 4]

def get_new_worklog_id():
    i = random.randint(10, 10000)
    global PREVIOUS_W_IDS
    while i in PREVIOUS_W_IDS:
        i = random.randint(10, 10000)
    PREVIOUS_W_IDS.append(i)
    return i

class urllib_response():
    def __init__(self, code):
        self.code = code

def parse_url(url):
    """return host, issue and worklogid(if presented)
    """
    host = None
    issue = None
    worklog = None
    url_list = url.split('/')
    for i in range(len(url_list)):
        if url_list[i] == 'issue':
            try:
                issue =  url_list[i+1]
            except IndexError:
                raise urllib2.HTTPError(url, 405, 'Method Not Allowed', None, None)
        if url_list[i] == 'worklog':
            try:
                worklog = url_list[i+1]
            except IndexError:
                worklog = None
    if url_list[0] == 'http:' or url_list[0] == 'https:':
        host = url_list[2]
    else:
        host = url_list[0]
    return host, issue, worklog

def convert_to_timedelta(time_val):
    """
    Given a *time_val* (string) such as '5d', returns a timedelta object
    representing the given value (e.g. timedelta(days=5)).  Accepts the
    following '<num><char>' formats:

    =========   ======= ===================
    Character   Meaning Example
    =========   ======= ===================
    s           Seconds '60s' -> 60 Seconds
    m           Minutes '5m'  -> 5 Minutes
    h           Hours   '24h' -> 24 Hours
    d           Days    '7d'  -> 7 Days
    =========   ======= ===================

    Examples::

    >>> convert_to_timedelta('7d')
    datetime.timedelta(7)
    >>> convert_to_timedelta('24h')
    datetime.timedelta(1)
    >>> convert_to_timedelta('60m')
    datetime.timedelta(0, 3600)
    >>> convert_to_timedelta('120s')
    datetime.timedelta(0, 120)
    """
    timedelta = datetime.timedelta
    num = int(time_val[:-1])
    if time_val.endswith('s'):
        return timedelta(seconds=num)
    elif time_val.endswith('m'):
        return timedelta(minutes=num)
    elif time_val.endswith('h'):
        return timedelta(hours=num)
    elif time_val.endswith('d'):
        return timedelta(days=num)

def get_random_worklog():
    pass

class JIRAIssue(rest_wrapper.JIRAIssue):
    def __init(self, jirahost, login, password, issue_key, new=False):
        rest_wrapper.JIRAIssue(jirahost, login, password, issue_key, new)

    def rest_req(self,url, data=None, req_type=None):
        # TODO: add jira time zone calculation
        known_issues = ('SAMPLE-1', 'SAMPLE-2', 'SAMPLE-3', 'ADDSAMPLE-1', 'EMPTY-1', 'EMPTY-2')
        known_worklog_ids = [1, 2, 3, 4, 100, 101, 102, 103, 104]
        host, issue, worklog_id = parse_url(url)
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
                                'id': 1}
                    issue_data['fields']['worklog']['worklogs'].append(worklog)
                    issue_data['fields']['worklog']['total'] += 1
                if issue == 'SAMPLE-2' or issue == 'SAMPLE-3':
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
                                      'id': 2}
                    issue_data['fields']['worklog']['worklogs'].append(worklog)
                    issue_data['fields']['worklog']['total'] += 1
                if issue == 'SAMPLE-3':
                    worklog = { 'comment': '',
                                'updated': '2013-01-07T03:48:20.000-0800',
                                'created': '2013-01-07T03:48:20.000-0800',
                                'started': '2013-01-07T03:48:00.000-0800',
                                'author':
                                    { 'name' : 'login',
                                      'displayName': u'Test User'
                                    },
                                'timeSpent': '4h 5m',
                                'timeSpentSeconds': 14700,
                                'id': 4}
                    del worklog['comment']
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
                                'id': 3}
                if req_type is None and data is None:
                    return issue_data
                elif req_type is None and data:
                    # add worklog
                    received_data = json.loads(data)
                    global WORKLOG_ID
                    worklog = {
                                'comment': received_data.get('comment', ''),
                                'updated': received_data['started'],
                                'created': received_data['started'],
                                'started': received_data['started'],
                                'author':
                                    { 'name' : self.login,
                                      'displayName': u'Test User'
                                    },
                                'timeSpent': utils.get_time_spent_string(
                                    datetime.timedelta(seconds=received_data['timeSpentSeconds'])),
                                'timeSpentSeconds': received_data['timeSpentSeconds'],
                                'id': WORKLOG_ID}

                    issue_data['fields']['worklog']['worklogs'].append(worklog)
                    issue_data['fields']['worklog']['total'] += 1
                    return worklog
                elif req_type and data:
                    received_data = json.loads(data)
                    if req_type == 'PUT':
                        # update worklog
                        if int(worklog_id) in known_worklog_ids:
                            # TODO: add fields verification
                            received_data['timeSpent'] = utils.get_time_spent_string(
                                datetime.timedelta(seconds=received_data['timeSpentSeconds']))
                            received_data['id'] = int(worklog_id)
                            return received_data
                        else:
                            # TODO: produce error
                            pass
                elif data is None and req_type:
                    if req_type == 'DELETE':
                        if int(worklog_id) in known_worklog_ids:
                            res =  urllib_response(204)
                            return res
                        else:
                            # TODO produce error
                            pass
                    else:
                        # raise exception
                        pass
            else:
                raise urllib2.HTTPError(url, 404, 'Not Found', None, None)
                # produce error about now issue
        else:
            raise urllib2.URLError('No such file or directory')
            return


class pyjttUtilsTest(unittest.TestCase):
    def setUp(self):
        self.jirahost = 'http://jira.example.com'
        self.login = 'login'
        self.password = 'password'

    def test_get_issue_normal(self):
        # Easy sample - 1 worklog entry with comment
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
        # 2 worklogs
        issue_key = 'SAMPLE-2'
        expeceted_worklog[2] = (datetime.datetime(2013,1,7,15,48),
                                datetime.datetime(2013,1,7,19,53), 'Test comment')
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, expeceted_worklog)
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)
        # Empty worklog comment
        issue_key = 'SAMPLE-3'
        expeceted_worklog[4] = (datetime.datetime(2013,1,7,15,48),
                                datetime.datetime(2013,1,7,19,53), '')
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, expeceted_worklog)
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)
        # Empty worklog
        issue_key = 'EMPTY-1'
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, {})
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)
        # No user worklog
        issue_key = 'EMPTY-2'
        issue = JIRAIssue(self.jirahost, self.login, self.password, issue_key, new=True)
        self.assertEqual(issue.issue_key, issue_key)
        self.assertEqual(issue.worklog, {})
        self.assertEqual(issue.issue_id, 123)
        self.assertTrue(issue.summary)

    def test_get_issue_errors(self):
        # Wrong host
        with self.assertRaises(urllib2.URLError) as io_err:
            issue = JIRAIssue('http://nonexists.com', self.login, self.password, 'NONEXISTS-331', new=True)
        # Wrong issue ( not found or denied )
        with self.assertRaises(urllib2.HTTPError) as http_err:
            issue = JIRAIssue(self.jirahost, self.login, self.password, 'NONEXISTS-331', new=True)

    def test_add_worklog_normal(self):
        start_date = datetime.datetime(2013, 1, 9, 17, 30)
        end_date = datetime.datetime(2013, 1, 9, 19)
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
        global WORKLOG_ID
        # add with empty comment
        WORKLOG_ID = get_new_worklog_id()
        expeceted_worklog[WORKLOG_ID] = (start_date, end_date,'')
        issue.add_worklog(start_date, end_date)
        self.assertEqual(issue.worklog, expeceted_worklog)
        # add wth normal comment
        comment = 'Test add comment'
        WORKLOG_ID = get_new_worklog_id()
        expeceted_worklog[WORKLOG_ID] = (start_date, end_date, comment)
        issue.add_worklog(start_date, end_date, comment)
        self.assertEqual(issue.worklog, expeceted_worklog)

    def test_add_worklog_errors(self):
        # TODO: wrong issue

        # TODO: wrong host

        # TODO: wrong data
        pass

    def test_update_worklog_normal(self):
        start_date = datetime.datetime(2013, 1, 9, 17, 30)
        end_date = datetime.datetime(2013, 1, 9, 19)
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
        global WORKLOG_ID
        comment = 'Test add comment'
        WORKLOG_ID = 100
        expeceted_worklog[WORKLOG_ID] = (start_date, end_date, comment)
        issue.add_worklog(start_date, end_date, comment)
        self.assertEqual(issue.worklog, expeceted_worklog)
        delta = datetime.timedelta(hours=3, minutes=30)
        new_comment = 'Updated comment'
        expeceted_worklog[WORKLOG_ID] = (start_date, end_date + delta, new_comment)
        issue.update_worklog(WORKLOG_ID, start_date, end_date + delta, new_comment)

    def test_remove_worklog_normal(self):
        start_date = datetime.datetime(2013, 1, 9, 17, 30)
        end_date = datetime.datetime(2013, 1, 9, 19)
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
        global WORKLOG_ID
        comment = 'Test add comment'
        WORKLOG_ID = 100
        expeceted_worklog[WORKLOG_ID] = (start_date, end_date, comment)
        issue.add_worklog(start_date, end_date, comment)
        self.assertEqual(issue.worklog, expeceted_worklog)
        issue.remove_worklog(WORKLOG_ID)

    def test_remove_worklog_error(self):
        pass

if __name__ == '__main__':
    unittest.main()

