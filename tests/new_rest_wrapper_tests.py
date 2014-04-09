#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import unittest
import datetime

import httpretty

sys.path.insert(0, os.path.abspath(os.path.join('..', 'pyjtt')))

import rest_wrapper
import base_classes


class SimpleWrapperTests(unittest.TestCase):

    def setUp(self):
        self.jira_url = 'http://example.com'
        self.sample_issue_key = 'TST-123'
        self.sample_issue = base_classes.JiraIssue('123',
                                                   self.sample_issue_key,
                                                   'summary')

    def test_create_accessor(self):
        accessor = rest_wrapper.JiraRESTAccessor(self.jira_url,
                                                 'login',
                                                 'password')
        self.assertIsNotNone(accessor)

    def test_get_issues(self):
        pass

    @httpretty.activate
    def test_get_worklog(self):
        response = b'{"expand":"renderedFields,names,schema,transitions,' \
                   b'operations,editmeta,changelog","id":"10432",' \
                   b'"self":"http://example.com/rest/api/2/issue/10432",' \
                   b'"key":"TST-123","fields":{' \
                   b'"worklog":{"startAt":0,"maxResults":20,"total":1,' \
                   b'"worklogs":[{' \
                   b'"self":"http://example.com/rest/api/2/issue/10432/worklog/10000",' \
                   b'"author":{"self":"http://example.com/rest/api/2/user?username=login",' \
                   b'"name":"login","emailAddress":"login@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=login&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=login&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=login&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=login&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},' \
                   b'"updateAuthor":{' \
                   b'"self":"http://example.com/rest/api/2/user?username=login",' \
                   b'"name":"login","emailAddress":"login@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=login&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=login&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=login&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=login&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},"comment":"",' \
                   b'"created":"2014-04-07T22:29:52.413+0400","updated":"2014-04-07T22:29:52.413+0400",' \
                   b'"started":"2014-04-07T21:29:00.000+0400","timeSpent":"1h",' \
                   b'"timeSpentSeconds":3600,"id":"10000"}]}}}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue_key,
                               body=response)
        accessor = rest_wrapper.JiraRESTAccessor(self.jira_url,
                                                 'login',
                                                 'password')
        worklogs = accessor.get_worklogs_for_issue(self.sample_issue)
        self.assertEqual(len(worklogs), 1)

    def test_get_empty_worklog(self):
        pass

    @httpretty.activate
    def test_add_worklog(self):
        response = b'{"self":"http://example.com/rest/api/2/issue/10432/worklog/10004",' \
                   b'"author":{"self":"http://example.com/rest/api/2/user?username=golub",' \
                   b'"name":"golub","emailAddress":"golub@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},"updateAuthor":{"self":' \
                   b'"http://example.com/rest/api/2/user?username=golub",' \
                   b'"name":"golub","emailAddress":"golub@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},' \
                   b'"comment":"This is from python",' \
                   b'"created":"2014-04-08T21:47:16.376+0400","updated":"2014-04-08T21:47:16.376+0400",' \
                   b'"started":"2014-04-08T19:47:15.000+0400","timeSpent":"2h","timeSpentSeconds":7200,"id":"10004"}'

        httpretty.register_uri(httpretty.POST,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/',
                               body=response)
        accessor = rest_wrapper.JiraRESTAccessor(self.jira_url,
                                                 'login',
                                                 'password')
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp =datetime.datetime.now()
        comment = 'This is from python'
        worklog = base_classes.JiraWorklog(self.sample_issue,
                                           start_timestamp,
                                           end_timestamp,
                                           comment)
        new_worklog = accessor.add_worklog(worklog)
        self.assertIsNotNone(new_worklog)
        self.assertEqual(comment, new_worklog.comment)

    @httpretty.activate
    def test_update_worklog(self):
        response = b'{"self":"http://example.com/rest/api/2/issue/10432/worklog/10004",' \
                   b'"author":{"self":"http://example.com/rest/api/2/user?username=golub",' \
                   b'"name":"golub","emailAddress":"golub@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},"updateAuthor":{"self":' \
                   b'"http://example.com/rest/api/2/user?username=golub",' \
                   b'"name":"golub","emailAddress":"golub@example.com","avatarUrls":{' \
                   b'"16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",' \
                   b'"24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",' \
                   b'"32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",' \
                   b'"48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"},' \
                   b'"displayName":"Nikolay Golub","active":true},' \
                   b'"comment":"This is from python",' \
                   b'"created":"2014-04-08T21:47:16.376+0400","updated":"2014-04-08T21:47:16.376+0400",' \
                   b'"started":"2014-04-08T19:47:15.000+0400","timeSpent":"2h","timeSpentSeconds":7200,"id":"10004"}'
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp =datetime.datetime.now()
        comment = 'This is from python'
        worklog_id = '31337'
        worklog = base_classes.JiraWorklog(self.sample_issue,
                                           start_timestamp,
                                           end_timestamp,
                                           comment,
                                           worklog_id)
        httpretty.register_uri(httpretty.PUT,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/' + worklog_id,
                               body=response)
        accessor = rest_wrapper.JiraRESTAccessor(self.jira_url,
                                                 'login',
                                                 'password')
        updated_worklog = accessor.update_worklog(worklog)
        self.assertIsNotNone(updated_worklog)
        self.assertEqual(updated_worklog.comment, comment)

    @httpretty.activate
    def test_remove_worklog(self):
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp =datetime.datetime.now()
        comment = 'This is from python'
        worklog_id = '31337'
        worklog = base_classes.JiraWorklog(self.sample_issue,
                                           start_timestamp,
                                           end_timestamp,
                                           comment,
                                           worklog_id)
        httpretty.register_uri(httpretty.DELETE,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/' + worklog_id)
        accessor = rest_wrapper.JiraRESTAccessor(self.jira_url,
                                                 'login',
                                                 'password')
        accessor.remove_worklog(worklog)
        # nothing to check, at first glance
