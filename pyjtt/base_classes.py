#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# This file is part of PyJTT.
#
#    PyJTT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    PyJTT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyJTT.  If not, see <http://www.gnu.org/licenses/>.
#
#    This is module with a small utils functions


__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2014, Nikolay Golub"
__license__ = "GPL"

from urllib.parse import urljoin

import utils


class JiraIssue(object):

    def __init__(self, issue_id, key, summary):
        self.issue_id = issue_id
        self.key = key
        self.summary = summary

    @staticmethod
    def _get_url(jira_url, issue_key):
        return urljoin(urljoin(jira_url, '/rest/api/2/issue/'), issue_key)

    def get_url(self, jira_url):
        return self._get_url(jira_url, self.key)


class JiraWorklogEntry(object):

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
        return self.ended - self.started

    def get_timespent_string(self):
        return utils.get_time_spent_string(self.ended - self.started)