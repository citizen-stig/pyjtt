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
__copyright__ = "Copyright 2012 - 2013, Nikolay Golub"
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
        return base_classes.JiraWorklog(issue,
                                        local_started,
                                        local_started + time_spent,
                                        raw_worklog.get('comment', ''),
                                        raw_worklog['id'],)

    def _serialize_worklog(self, worklog):
        """Prepares worklog entry data for JIRA representation"""
        started = worklog.started.strftime(self.jira_timeformat) + '.000' + '+0400' #'' + utils.LOCAL_UTC_OFFSET_TIMEDELTA
        spent = worklog.ended - worklog.started
        data = {'started': started,
                'timeSpentSeconds': int(spent.total_seconds()),
                'comment': worklog.comment}
        return data

    def get_issue_by_key(self, issue_key):
        pass

    def get_worklogs_for_issue(self, issue):
        worklogs = []
        issue_url = issue.get_url(self.jirahost) + '?fields=worklog'
        raw_data = self._make_request(issue_url)
        logger.debug('Requesting worklog for issue {key}'.format(key=issue.key))
        raw_worklogs = raw_data['fields']['worklog']['worklogs']
        try:
            for worklog_entry in raw_worklogs:
                if worklog_entry['author']['name'] == self.login:
                    worklog = self._parse_worklog(issue, worklog_entry)
                    worklogs.append(worklog)
        except KeyError:
            logger.info('Worklog is empty for issue {key}'.format(key=issue.key))
        return worklogs

    def add_worklog(self, worklog):
        json_data = json.dumps(self._serialize_worklog(worklog)).encode(self.encoding)
        # append '/' to the base url to avoid replacement
        add_url = worklog.get_url(self.jirahost)
        new_worklog_data = self._make_request(add_url,
                                              data=json_data)
        return self._parse_worklog(worklog.issue, new_worklog_data)

    def update_worklog(self, worklog):
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

    def remove_worklog(self, worklog):
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


# class JiraRestBase(object):
#     """Wrapper class for making JIRA requests.
#
#     It builds correct request to the JIRA rest api from given URL and data.
#     """
#     def __init__(self, jirahost, login, password):
#         logger.debug("JiraRestBase object has been called")
#         self.jirahost = jirahost
#         self.login = login
#         self.password = password
#         self.auth_string = 'Basic ' + (self.login +
#                                        ":" +
#                                        self.password).encode('base64').rstrip()
#         logger.debug("JiraRestBase object initialization is completed")
#
#     def rest_req(self, url, data=None, req_type=None):
#         """Makes a request to JIRA REST API
#
#         URL is a valid rest-api url.
#         data is json data in POST request
#         req_type is string(PUT or DELETE)
#         """
#         logger.info("Make a request to %s" % url)
#         if data:
#             request = urllib.request.Request(url,
#                                       data, {'Content-Type': 'application/json'})
#         else:
#             request = urllib.request.Request(url)
#         request.add_header('Authorization', self.auth_string)
#         if req_type:
#             opener = urllib.request.build_opener(urllib.request.HTTPHandler)
#             request.get_method = lambda: req_type
#             raw_res = opener.open(request)
#         else:
#             raw_res = urllib.request.urlopen(request)
#         result = json.loads(raw_res.read()) if req_type != 'DELETE' else raw_res
#         logger.info("Request to %s is completed" % url)
#         return result
#
#
# class JIRAIssue(JiraRestBase):
#     """Class for manipulation with JIRA issue worklogs."""
#     def __init__(self, jirahost, login, password, issue_key, new=False):
#         logger.info('Initialize JIRA Issue %s object' % issue_key)
#         JiraRestBase.__init__(self, jirahost, login, password)
#         self.issue_key = issue_key
#         self.jira_timeformat = '%Y-%m-%dT%H:%M:%S'
#         self.issue_link = self.jirahost + '/browse/' + self.issue_key
#         self.worklog = {}
#
#         self.issue_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key
#         self.add_url = self.jirahost + '/rest/api/2/issue/' + \
#                        self.issue_key + '/worklog'
#         # If new parameter is set to False, issue will build offline
#         if new:
#             self.get_issue_data()
#         logger.debug('Initialization of %s is completed' % self.issue_key)
#
#     def get_issue_data(self):
#         """Gets issue data: Summary, ID and work logs."""
#         logger.debug('Requesting worklog for issue %s' % self.issue_key)
#         raw_issue_data = self.rest_req(self.issue_url)
#         logger.debug('Parsing issue %s' % self.issue_key)
#         self.summary = raw_issue_data['fields']['summary']
#         self.issue_id = int(raw_issue_data['id'])
#         if not raw_issue_data['fields']['worklog']['worklogs']:
#             logger.info('Worklog is empty for this issue')
#         else:
#             for a in raw_issue_data['fields']['worklog']['worklogs']:
#                 if a['author']['name'] == self.login:
#                     self.worklog[int(a['id'])] = self.__parse_worklog(
#                         a['started'],
#                         a['timeSpentSeconds'],
#                         a.get('comment', ''))
#         logger.debug('Issue info has been collected')
#
#     def add_worklog(self, start_date, end_date, comment=None):
#         """Adds new worklog to the issue.
#
#         All parameters checks should be done before call this method.
#         """
#         logger.debug('Adding worklog to issue %s' % self.issue_key)
#         json_data = json.dumps(
#             self.__prepare_worklog_data(start_date, end_date, comment))
#         new_worklog = self.rest_req(self.add_url, data=json_data)
#         self.worklog[int(new_worklog['id'])] = self.__parse_worklog(
#             new_worklog['started'],
#             new_worklog['timeSpentSeconds'],
#             new_worklog.get('comment', ''))
#         logger.debug('Worklog has been added')
#         return {int(new_worklog['id']): self.worklog[int(new_worklog['id'])]}
#
#     def remove_worklog(self, worklog_id):
#         """Removes worklog from the issue.
#
#         All parameters checks should be done before call this method.
#         """
#         logger.debug('Removing worklog %s' % worklog_id)
#         remove_url = self.jirahost + '/rest/api/2/issue/' + \
#             self.issue_key + '/worklog/' + str(worklog_id)
#         res = self.rest_req(remove_url, req_type='DELETE')
#         if res.code == 204:
#             del self.worklog[worklog_id]
#             logger.debug('Worklog has been deleted.')
#         else:
#             logger.error("Something goes wrong, return code is %d" % res.code)
#
#     def update_worklog(self, worklog_id, start_date=None,
#                        end_date=None, comment=None):
#         """Updates worklog in the issue.
#
#         All parameters checks should be done before call this method.
#         """
#         logger.debug('Updating worklog %s' % repr(worklog_id))
#         upd_url = self.jirahost + '/rest/api/2/issue/' + \
#             self.issue_key + '/worklog/' + str(worklog_id)
#         if start_date and end_date:
#             data = self.__prepare_worklog_data(start_date, end_date, comment)
#         elif comment:
#             data = {'comment': comment}
#         logger.debug('Update worklog with this data: %s ' % repr(data))
#         json_data = json.dumps(data)
#         updated_worklog = self.rest_req(upd_url, data=json_data, req_type='PUT')
#         logger.debug(updated_worklog)
#         self.worklog[worklog_id] = self.__parse_worklog(
#             updated_worklog['started'],
#             updated_worklog['timeSpentSeconds'],
#             updated_worklog.get('comment', ''))
#         return int(updated_worklog['id']), self.worklog[int(updated_worklog['id'])]
#
#     def __parse_worklog(self, started, spent_seconds, comment):
#         """Parses worklog entry data to interal representation"""
#         logger.debug('Parsing worklog data')
#         strptime = datetime.datetime.strptime
#         time_spent = datetime.timedelta(seconds=spent_seconds)
#         remote_started = strptime(started[:19], self.jira_timeformat)
#         utc_offset = utils.get_timedelta_from_utc_offset(started[-5:])
#         utc_started = remote_started - utc_offset
#         local_started = utc_started + utils.LOCAL_UTC_OFFSET_TIMEDELTA
#         logger.debug('Worklog data has been parsed')
#         return local_started, local_started + time_spent, comment
#
#     def __prepare_worklog_data(self, start_date, end_date, comment=None):
#         """Prepares worklog entry data for JIRA representation"""
#         logger.debug('Preparing worklog for sending')
#         started = start_date.strftime(self.jira_timeformat) + \
#             '.000' + utils.LOCAL_UTC_OFFSET
#         spent = end_date - start_date
#         data = {'started': started,
#                 'timeSpentSeconds': int(spent.total_seconds())}
#         if comment:
#             data['comment'] = comment
#         logger.debug('Worklog has been prepared')
#         return data
#
#     def __int_round(self, x, base=5):
#         logger.debug('Round %s' % str(x))
#         return int(base * round(float(x)/base))
#
#     def __str__(self):
#         return '[%s]: %s' % (self.issue_key, self.summary)
#
#
# class JiraUser(JiraRestBase):
#     """Class for accessing to user data"""
#     def __init__(self, jirahost, login, password, custom_jql=None):
#         logger.debug('Jira user object has been called')
#         JiraRestBase.__init__(self, jirahost, login, password)
#         self.custom_jql = custom_jql
#         self.user_url = str(self.jirahost) + '/rest/api/2/user?username=' + str(self.login)
#         raw_user_data = self.rest_req(self.user_url)
#         self.display_name = raw_user_data['displayName']
#         self.email = raw_user_data['emailAddress']
#
#     def get_assigned_issues(self):
#         """Fills list of assigned issues.
#
#         Currently gets only 50 issues
#         """
#         # TODO: add sorting in JQL
#         if self.custom_jql:
#             cleaned_jql = utils.clean_jql_url(self.custom_jql)
#             to_retrieve_url = self.jirahost + '/rest/api/2/search?jql=' + cleaned_jql
#         else:
#             to_retrieve_url = '%s/rest/api/2/search?jql=assignee="%s"+and+status!=Resolved+and+status!=Completed+and+status!=Closed+and+status!=Aborted&fields=key' % (self.jirahost, self.login)
#         self.assigned_issue_keys = []
#         logger.debug('Request assigned issues')
#         raw_assigned = self.rest_req(to_retrieve_url)
#         logger.debug('Parse assigned isses')
#         for raw_issue in raw_assigned['issues']:
#             self.assigned_issue_keys.append(raw_issue['key'])