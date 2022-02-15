import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urljoin
import json
from datetime import datetime, timedelta
import base64

import logging

import base_classes
import utils

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"

logger = logging.getLogger(__name__)


class JiraRESTAccessor(object):
    encoding = 'utf-8'
    jira_timeformat = '%Y-%m-%dT%H:%M:%S'
    jql_assigned = 'project=PERF+AND+resolution=Unresolved+AND+(assignee+in+(currentUser())+OR+issuetype+in+("Routine%20Activity"))'

    def __init__(self, jirahost, login, password):
        self.jirahost = jirahost
        self.login = login
        self.password = password
        credentials = base64.b64encode(
            (login + ':' + password).encode(self.encoding))
        self.auth_string = 'Basic '.encode(self.encoding) + credentials

    def _make_request(self, url, data=None, req_type=None):
        logger.info("Make a request to {url}".format(url=url))
        if data:
            request = urllib.request.Request(
                url,
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
        result = json.loads(raw_res.read().decode(
            self.encoding)) if req_type != 'DELETE' else raw_res
        logger.info("Request to %s is completed" % url)
        return result

    def _parse_worklog_entry(self, issue, raw_worklog_entry):
        """Parses worklog entry data to interal representation"""
        logger.debug('Parsing worklog data')
        time_spent = timedelta(seconds=raw_worklog_entry['timeSpentSeconds'])
        remote_started = datetime.strptime(raw_worklog_entry['started'][:19],
                                           self.jira_timeformat)
        utc_offset = utils.get_timedelta_from_utc_offset(
            raw_worklog_entry['started'][-5:])
        utc_started = remote_started - utc_offset
        local_started = utc_started + utils.LOCAL_UTC_OFFSET_TIMEDELTA
        logger.debug('Worklog data has been parsed')
        return base_classes.JiraWorklogEntry(issue,
                                             local_started,
                                             local_started + time_spent,
                                             raw_worklog_entry.get('comment',
                                                                   ''),
                                             raw_worklog_entry['id'], )

    def _parse_worklog(self, issue, raw_data):
        worklog = []
        try:
            if raw_data['fields']['worklog']['total'] > \
                raw_data['fields']['worklog']['maxResults']:
                return self.get_worklog_for_issue(issue)
            raw_worklog = raw_data['fields']['worklog']['worklogs']
        except KeyError:
            raw_worklog = raw_data['worklogs']
        for raw_worklog_entry in raw_worklog:
            if raw_worklog_entry['author']['name'] == self.login:
                worklog_entry = self._parse_worklog_entry(issue,
                                                          raw_worklog_entry)
                worklog.append(worklog_entry)
        return worklog

    @staticmethod
    def _parse_issue(raw_issue_data):
        issue = base_classes.JiraIssue(raw_issue_data['id'],
                                       raw_issue_data['key'],
                                       raw_issue_data['fields']['summary'])
        return issue

    def _serialize_worklog(self, worklog):
        """Prepares worklog entry data for JIRA representation"""
        started = worklog.started.strftime(
            self.jira_timeformat) + '.000' + utils.LOCAL_UTC_OFFSET
        spent = worklog.ended - worklog.started
        data = {'started': started,
                'timeSpentSeconds': int(spent.total_seconds()),
                'comment': worklog.comment}
        return data

    def get_issue_by_key(self, issue_key):
        issue_url = base_classes.JiraIssue._get_url(self.jirahost,
                                                    issue_key) + '?fields=summary,worklog'
        raw_issue_data = self._make_request(issue_url)
        issue = self._parse_issue(raw_issue_data)
        return issue, self._parse_worklog(issue, raw_issue_data)

    def get_worklog_for_issue(self, issue):
        issue_url = issue.get_url(self.jirahost) + '/worklog'
        raw_data = self._make_request(issue_url)
        logger.debug(
            'Requesting worklog for issue {key}'.format(key=issue.key))
        return self._parse_worklog(issue, raw_data)

    def add_worklog_entry(self, worklog):
        json_data = json.dumps(self._serialize_worklog(worklog)).encode(
            self.encoding)
        # append '/' to the base url to avoid replacement
        add_url = worklog.get_url(self.jirahost)
        new_worklog_data = self._make_request(add_url,
                                              data=json_data)
        if 'worklogs' not in new_worklog_data:
            return self._parse_worklog_entry(worklog.issue, new_worklog_data)
        else:
            # We add only one worklog at time
            return self._parse_worklog_entry(worklog.issue,
                                             new_worklog_data['worklogs'][0])

    def update_worklog_entry(self, worklog_entry):
        update_url = worklog_entry.get_url(self.jirahost)
        json_data = json.dumps(self._serialize_worklog(worklog_entry)).encode(
            self.encoding)
        updated_worklog_data = self._make_request(update_url,
                                                  data=json_data,
                                                  req_type='PUT')
        if 'worklogs' not in updated_worklog_data:
            return self._parse_worklog_entry(worklog_entry.issue,
                                             updated_worklog_data)
        else:
            # We update only one worklog at time
            return self._parse_worklog_entry(worklog_entry.issue,
                                             updated_worklog_data['worklogs'][
                                                 0])

    def remove_worklog_entry(self, worklog_entry):
        remove_url = worklog_entry.get_url(self.jirahost)
        self._make_request(remove_url, req_type='DELETE')
        logger.debug('Worklog has been deleted')

    def get_user_assigned_issues(self):
        return self.get_issues_by_custom_filter(self.jql_assigned)

    def get_issues_by_custom_filter(self, jql_expression):
        issues_w_worklog = []
        jql_url = urljoin(self.jirahost,
                          '/rest/api/2/search') + '?jql=' + jql_expression + '&fields=summary,worklog'
        raw_data = self._make_request(jql_url)
        for raw_issue_data in raw_data['issues']:
            issue = self._parse_issue(raw_issue_data)
            worklog = self._parse_worklog(issue, raw_issue_data)
            issues_w_worklog.append((issue, worklog))
        if raw_data['total'] > raw_data['maxResults']:
            current = raw_data['maxResults']
            while current < raw_data['total']:
                additional_url = urljoin(self.jirahost,
                                         '/rest/api/2/search') + '?jql=' \
                                 + jql_expression + '&fields=summary,worklog' + '&startAt=' + str(
                    current)
                raw_data = self._make_request(additional_url)
                for raw_issue_data in raw_data['issues']:
                    issue = self._parse_issue(raw_issue_data)
                    worklog = self._parse_worklog(issue, raw_issue_data)
                    issues_w_worklog.append((issue, worklog))
                current += raw_data['maxResults']
        return issues_w_worklog

    def get_user_info(self):
        user_url = urljoin(self.jirahost,
                           '/rest/api/2/user') + '?username=' + self.login + '&fields=displayName'
        raw_data = self._make_request(user_url)
        return raw_data
