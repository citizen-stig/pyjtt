from urllib.parse import urljoin

from . import utils

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"


class JiraIssue(object):

    def __init__(self, issue_id, key, summary):
        self.issue_id = issue_id
        self.key = key
        self.summary = summary

    def __str__(self):
        return "{key}: {summary}".format(key=self.key,
                                         summary=self.summary)

    @staticmethod
    def _get_url(jira_url, issue_key):
        return urljoin(urljoin(jira_url, '/rest/api/2/issue/'), issue_key)

    def get_url(self, jira_url):
        return self._get_url(jira_url, self.key)


class JiraWorklogEntry(object):
    time_fmt = '%d-%m-%Y %H:%M:%S'

    def __init__(self, issue, started, ended, comment, worklog_id=''):
        self.worklog_id = worklog_id
        self.started = started
        self.ended = ended
        self.comment = comment
        self.issue = issue

    def get_url(self, jira_url):
        return urljoin(self.issue.get_url(jira_url) + '/worklog/',
                       self.worklog_id)

    def __str__(self):
        return self.worklog_id + '=' + self.started.strftime(self.time_fmt) \
            + ' - ' + self.ended.strftime(self.time_fmt)

    def get_timespent(self):
        return self.ended - self.started

    def get_timespent_string(self):
        return utils.get_time_spent_string(self.ended - self.started)
