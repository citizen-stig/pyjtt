#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#    This module allows to interact with a few JIRA API functions on
#    Python level


__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2014, Nikolay Golub"
__license__ = "GPL"

import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urljoin
import json
from datetime import datetime, timedelta
import base64

import logging
logger = logging.getLogger(__name__)

import base_classes
import utils


class JiraRESTAccessor(object):
    encoding = 'utf-8'
    jira_timeformat = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, jirahost, login, password):
        self.jirahost = jirahost
        self.login = login
        credentials = base64.b64encode((login + ':' + password).encode(self.encoding))
        self.auth_string = 'Basic '.encode(self.encoding) + credentials

    def _make_request(self, url, data=None, req_type=None):
        logger.info("Make a request to {url}".format(url=url))
        if data:
            request = urllib.request.Request(url,
                                             data,
                                             {'Content-Type': 'application/json'})
        else:
            request = urllib.request.Request(url)
        request.add_header('Authorization', self.auth_string)
        if req_type:
            opener = urllib.request.build_opener(urllib.request.HTTPHandler)
            request.get_method = lambda: req_type
            raw_res = opener.open(request)
        else:
            raw_res = urllib.request.urlopen(request)
        result = json.loads(raw_res.read().decode(self.encoding)) if req_type != 'DELETE' else raw_res
        logger.info("Request to %s is completed" % url)
        return result

    def _get_issue_link(self, issue_key):
        return urljoin(urljoin(self.jirahost, '/rest/api/2/issue/'), issue_key)

    def _parse_worklog(self, issue, raw_worklog):
        """Parses worklog entry data to interal representation"""
        logger.debug('Parsing worklog data')
        time_spent = timedelta(seconds=raw_worklog['timeSpentSeconds'])
        remote_started = datetime.strptime(raw_worklog['started'][:19],
                                           self.jira_timeformat)
        utc_offset = utils.get_timedelta_from_utc_offset(raw_worklog['started'][-5:])
        utc_started = remote_started - utc_offset
        local_started = utc_started + utils.LOCAL_UTC_OFFSET_TIMEDELTA
        logger.debug('Worklog data has been parsed')
        return base_classes.JiraWorklogEntry(issue,
                                             local_started,
                                             local_started + time_spent,
                                             raw_worklog.get('comment', ''),
                                             raw_worklog['id'], )

    def _serialize_worklog(self, worklog):
        """Prepares worklog entry data for JIRA representation"""
        started = worklog.started.strftime(self.jira_timeformat) + '.000' + utils.LOCAL_UTC_OFFSET
        spent = worklog.ended - worklog.started
        data = {'started': started,
                'timeSpentSeconds': int(spent.total_seconds()),
                'comment': worklog.comment}
        return data

    def get_issue_by_key(self, issue_key):
        pass

    def get_worklog_for_issue(self, issue):
        worklog = []
        issue_url = issue.get_url(self.jirahost) + '?fields=worklog'
        raw_data = self._make_request(issue_url)
        logger.debug('Requesting worklog for issue {key}'.format(key=issue.key))
        raw_worklog = raw_data['fields']['worklog']['worklogs']
        try:
            for raw_worklog_entry in raw_worklog:
                if raw_worklog_entry['author']['name'] == self.login:
                    worklog_entry = self._parse_worklog(issue, raw_worklog_entry)
                    worklog.append(worklog_entry)
        except KeyError:
            logger.info('Worklog is empty for issue {key}'.format(key=issue.key))
        return worklog

    def add_worklog(self, worklog):
        json_data = json.dumps(self._serialize_worklog(worklog)).encode(self.encoding)
        # append '/' to the base url to avoid replacement
        add_url = worklog.get_url(self.jirahost)
        new_worklog_data = self._make_request(add_url,
                                              data=json_data)
        return self._parse_worklog(worklog.issue, new_worklog_data)

    def update_worklog_entry(self, worklog):
        if worklog.worklog_id is not None:
            update_url = worklog.get_url(self.jirahost)
            json_data = json.dumps(self._serialize_worklog(worklog)).encode(self.encoding)
            updated_worklog_data = self._make_request(update_url,
                                                      data=json_data,
                                                      req_type='PUT')
            return self._parse_worklog(worklog.issue, updated_worklog_data)
        else:
            # TODO: add custom exception
            logger.error('Cannot update worklog without id in JIRA')

    def remove_worklog_entry(self, worklog):
        if worklog.worklog_id is not None:
            remove_url = worklog.get_url(self.jirahost)
            self._make_request(remove_url, req_type='DELETE')
            logger.debug('Worklog has been deleted')
        else:
            # TODO: add custom exception
            logger.error('Cannot remove worklog without id in JIRA')

    def get_user_assigned_issue(self, username):
        pass

    def get_issues_by_custom_filter(self, jql_expression):
        pass
