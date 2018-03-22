#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import unittest
import datetime
from urllib import parse
import json

import httpretty

from pyjtt import jira_accessor, base_classes


class SimpleWrapperTests(unittest.TestCase):

    def setUp(self):
        self.jira_url = 'http://example.com'
        self.sample_issue_key = 'TST-123'
        self.sample_issue = base_classes.JiraIssue('123',
                                                   self.sample_issue_key,
                                                   'summary')

    def test_create_accessor(self):
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        self.assertIsNotNone(accessor)

    def test_create_accessor_tricky_password(self):
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'Ilike%!@#$%^&*()_')
        self.assertIsNotNone(accessor)

    @httpretty.activate
    def test_get_issue_by_key(self):
        response = b'{"id": "10806", "fields": ' \
                   b'{' \
                   b'"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b'"summary": "\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82\xd1\x89 and english"' \
                   b'}, ' \
                   b'"expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog", ' \
                   b'"key": "TST-123", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10806"}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue_key,
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        issue, _ = accessor.get_issue_by_key(self.sample_issue_key)
        self.assertEqual(issue.key, self.sample_issue_key)

    @httpretty.activate
    def test_get_assigned_issues(self):
        response = b'{"expand": "schema,names", "total": 5, "startAt": 0, ' \
                   b'"issues": [' \
                   b'{"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test1"}, "key": "TST-101", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10502", "id": "10502"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test2"}, "key": "TST-102", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10500", "id": "10500"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test3"}, "key": "TST-103", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10443", "id": "10443"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test4"}, "key": "TST-104", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10442", "id": "10442"},' \
                   b' {"expand": "editmeta,renderedFields,transitions,changelog,operations", ' \
                   b'"fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},' \
                   b' "summary": "Test5"}, "key": "TST-105", ' \
                   b'"self": "https://example.com/rest/api/2/issue/10441", "id": "10441"}' \
                   b'], "maxResults": 50}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/search',
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        issues = accessor.get_user_assigned_issues()
        self.assertEqual(len(issues), 5)

    @httpretty.activate
    def test_get_more_than_50_issues(self):
        def request_callback(method, uri, headers):
            start = 0
            end = 50
            if 'startAt' in uri:
                parsed_uri = parse.urlparse(uri)
                query = parse.parse_qs(parsed_uri.query)
                start_at = int(query['startAt'][0])
                start += start_at
                end += start_at
            else:
                start_at = 0
            issues = []
            for i in range(start, end):
                issue = {"expand": "editmeta,renderedFields,transitions,changelog,operations",
                         "fields": {"worklog": {"total": 0, "startAt": 0, "worklogs": [], "maxResults": 20},
                                    "summary": "Test%s" % i},
                         "key": "TST-%s" % (100 + i),
                         "self": "https://example.com/rest/api/2/issue/10%s" % (100 + i), "id": "10%s" % (100 + i)}
                issues.append(issue)
            response_dict = {
                'issues': issues,
                'total': 150,
                'startAt': start_at,
                'expand': 'schema,names',
                'maxResults': 50
            }
            response = json.dumps(response_dict).encode('utf-8')
            return 200, headers, response

        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/search',
                               body=request_callback)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        issues = accessor.get_user_assigned_issues()
        self.assertEqual(len(issues), 150)

    @httpretty.activate
    def test_get_worklog(self):
        response = b"""{
            "expand":"renderedFields,names,schema,transitions,operations,editmeta,changelog",
            "id":"10432",
            "self":"http://example.com/rest/api/2/issue/10432",
            "key":"TST-123",
            "fields":{
                "worklog":{
                    "startAt":0,
                    "maxResults":20,
                    "total":1,
                    "worklogs":[
                        {
                            "self":"http://example.com/rest/api/2/issue/10432/worklog/10000",
                            "author":{
                                "self":"http://example.com/rest/api/2/user?username=login",
                                "name":"login",
                                "emailAddress":"login@example.com",
                                "avatarUrls":{
                                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=login&avatarId=10300",
                                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=login&avatarId=10300",
                                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=login&avatarId=10300",
                                    "48x48":"http://example.com/secure/useravatar?ownerId=login&avatarId=10300"
                                },
                                "displayName":"Nikolay Golub",
                                "active":true
                            },
                            "updateAuthor":{
                                "self":"http://example.com/rest/api/2/user?username=login",
                                "name":"login",
                                "emailAddress":"login@example.com",
                                "avatarUrls":{
                                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=login&avatarId=10300",
                                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=login&avatarId=10300",
                                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=login&avatarId=10300",
                                    "48x48":"http://example.com/secure/useravatar?ownerId=login&avatarId=10300"
                                },
                                "displayName":"Nikolay Golub",
                                "active":true
                            },
                            "comment":"",
                            "created":"2014-04-07T22:29:52.413+0400",
                            "updated":"2014-04-07T22:29:52.413+0400",
                            "started":"2014-04-07T21:29:00.000+0400",
                            "timeSpent":"1h",
                            "timeSpentSeconds":3600,
                            "id":"10000"
                        }
                    ]
                }
            }
        }"""
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue_key + '/worklog',
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        worklog = accessor.get_worklog_for_issue(self.sample_issue)
        self.assertEqual(len(worklog), 1)

    @httpretty.activate
    def test_get_empty_worklog(self):
        response = b'{"expand":"renderedFields,names,schema,transitions,' \
                   b'operations,editmeta,changelog","id":"10432",' \
                   b'"self":"http://example.com/rest/api/2/issue/10432",' \
                   b'"key":"TST-123","fields":{' \
                   b'"worklog":{"startAt":0,"maxResults":20,"total":0,' \
                   b'"worklogs":[]}}}'
        httpretty.register_uri(httpretty.GET,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue_key + '/worklog',
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url,
                                                  'login',
                                                  'password')
        worklog = accessor.get_worklog_for_issue(self.sample_issue)
        self.assertEqual(len(worklog), 0)

    @httpretty.activate
    def test_add_worklog(self):
        response = b"""{
            "self":"http://example.com/rest/api/2/issue/10432/worklog/10004",
            "author":{
                "self":"http://example.com/rest/api/2/user?username=golub",
                "name":"golub",
                "emailAddress":"golub@example.com",
                "avatarUrls":{
                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",
                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",
                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",
                    "48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"
                },
                "displayName":"Nikolay Golub",
                "active":true
            },
            "updateAuthor":{
                "self":"http://example.com/rest/api/2/user?username=golub",
                "name":"golub",
                "emailAddress":"golub@example.com",
                "avatarUrls":{
                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",
                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",
                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",
                    "48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"
                },
                "displayName":"Nikolay Golub",
                "active":true
            },
            "comment":"This is from python",
            "created":"2014-04-08T21:47:16.376+0400",
            "updated":"2014-04-08T21:47:16.376+0400",
            "started":"2014-04-08T19:47:15.000+0400",
            "timeSpent":"2h",
            "timeSpentSeconds":7200,
            "id":"10004"
        }"""
        httpretty.register_uri(httpretty.POST,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/',
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url, 'login', 'password')
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp = datetime.datetime.now()
        comment = 'This is from python'
        worklog = base_classes.JiraWorklogEntry(self.sample_issue,
                                                start_timestamp,
                                                end_timestamp,
                                                comment)
        new_worklog = accessor.add_worklog_entry(worklog)
        self.assertIsNotNone(new_worklog)
        self.assertEqual(comment, new_worklog.comment)

    @httpretty.activate
    def test_update_worklog(self):
        response = b"""{
            "self":"http://example.com/rest/api/2/issue/10432/worklog/10004",
            "author":{
                "self":"http://example.com/rest/api/2/user?username=golub",
                "name":"golub",
                "emailAddress":"golub@example.com",
                "avatarUrls":{
                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",
                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",
                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",
                    "48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"
                },
                "displayName":"Nikolay Golub",
                "active":true
            },
            "updateAuthor":{
                "self":"http://example.com/rest/api/2/user?username=golub",
                "name":"golub",
                "emailAddress":"golub@example.com",
                "avatarUrls":{
                    "16x16":"http://example.com/secure/useravatar?size=xsmall&ownerId=golub&avatarId=10300",
                    "24x24":"http://example.com/secure/useravatar?size=small&ownerId=golub&avatarId=10300",
                    "32x32":"http://example.com/secure/useravatar?size=medium&ownerId=golub&avatarId=10300",
                    "48x48":"http://example.com/secure/useravatar?ownerId=golub&avatarId=10300"
                },
                "displayName":"Nikolay Golub",
                "active":true
            },
            "comment":"This is from python",
            "created":"2014-04-08T21:47:16.376+0400",
            "updated":"2014-04-08T21:47:16.376+0400",
            "started":"2014-04-08T19:47:15.000+0400",
            "timeSpent":"2h",
            "timeSpentSeconds":7200,
            "id":"10004"
        }"""
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp = datetime.datetime.now()
        comment = 'This is from python'
        worklog_id = '31337'
        worklog = base_classes.JiraWorklogEntry(self.sample_issue, start_timestamp, end_timestamp,
                                                comment, worklog_id)
        httpretty.register_uri(httpretty.PUT,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/' + worklog_id,
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url, 'login', 'password')
        updated_worklog = accessor.update_worklog_entry(worklog)
        self.assertIsNotNone(updated_worklog)
        self.assertEqual(updated_worklog.comment, comment)

    @httpretty.activate
    def test_remove_worklog(self):
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp = datetime.datetime.now()
        comment = 'This is from python'
        worklog_id = '31337'
        worklog = base_classes.JiraWorklogEntry(self.sample_issue, start_timestamp, end_timestamp,
                                                comment, worklog_id)
        httpretty.register_uri(httpretty.DELETE,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/' + worklog_id)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url, 'login', 'password')
        accessor.remove_worklog_entry(worklog)
        # nothing to check, at first glance

    @httpretty.activate
    def test_from_igor(self):
        response = b"""{
            "total":1,
            "maxResults":1,
            "startAt":0,
            "worklogs":[
                {
                    "id":"585458",
                    "started":"2015-04-02T08:04:00.000-0700",
                    "created":"2015-04-03T08:04:25.000-0700",
                    "timeSpent":"1h",
                    "self":"https://jira.ringcentral.com/rest/api/2/issue/477228/worklog/585458",
                    "timeSpentSeconds":3600,
                    "updated":"2015-04-03T08:04:25.000-0700",
                    "updateAuthor":{
                        "avatarUrls":{
                            "16x16":"https://jira.ringcentral.com/secure/useravatar?size=small&avatarId=10302",
                            "48x48":"https://jira.ringcentral.com/secure/useravatar?avatarId=10302"
                        },
                        "self":"https://jira.ringcentral.com/rest/api/2/user?username=sergey.zaitsev",
                        "name":"sergey.zaitsev",
                        "emailAddress":"sergey.zaitsev@nordigy.ru",
                        "active":true,
                        "displayName":"Sergey Zaitsev"
                    },
                    "author":{
                        "avatarUrls":{
                            "16x16":"https://jira.ringcentral.com/secure/useravatar?size=small&avatarId=10302",
                            "48x48":"https://jira.ringcentral.com/secure/useravatar?avatarId=10302"
                        },
                        "self":"https://jira.ringcentral.com/rest/api/2/user?username=sergey.zaitsev",
                        "name":"sergey.zaitsev",
                        "emailAddress":"sergey.zaitsev@nordigy.ru",
                        "active":true,
                        "displayName":"Sergey Zaitsev"
                    },
                    "comment":"This is from python"
                }
            ]
        }"""
        httpretty.register_uri(httpretty.POST,
                               self.jira_url + '/rest/api/2/issue/' + self.sample_issue.key + '/worklog/',
                               body=response)
        accessor = jira_accessor.JiraRESTAccessor(self.jira_url, 'login', 'password')
        start_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_timestamp = datetime.datetime.now()
        comment = 'This is from python'
        worklog = base_classes.JiraWorklogEntry(self.sample_issue,
                                                start_timestamp,
                                                end_timestamp,
                                                comment)
        new_worklog = accessor.add_worklog_entry(worklog)
        self.assertIsNotNone(new_worklog)
        self.assertEqual(comment, new_worklog.comment)
