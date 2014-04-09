#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from urllib.parse import urljoin

class JiraIssue(object):

    def __init__(self, issue_id, key, summary):
        self.issue_id = issue_id
        self.key = key
        self.summary = summary

    def get_url(self, jira_url):
        return urljoin(urljoin(jira_url, '/rest/api/2/issue/'), self.key)

class JiraWorklog(object):

    def __init__(self, issue, started, ended, comment, worklog_id=''):
        self.worklog_id = worklog_id
        self.started = started
        self.ended = ended
        self.comment = comment
        self.issue = issue

    def get_url(self, jira_url):
        return urljoin(self.issue.get_url(jira_url) + '/worklog/', self.worklog_id)

    def __str__(self):
        return self.worklog_id + '=' + self.started.strftime('%d-%m-%Y %H:%M:%S') + ' - ' \
            + self.ended.strftime('%d-%m-%Y %H:%M:%S')

    def get_timespent(self):
        pass