#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'


import urllib2, json, logging, datetime
import utils

class JiraRestBase(object):
    """
    Wrapper class for making JIRA requests
    """
    def __init__(self, jirahost, login, password):
        # TODO: think of jirahost validation
        logging.debug("JiraRestBase object has been called")
        self.jirahost = jirahost
        self.login = login
        self.password = password
        self.auth_string = 'Basic '+ (self.login + \
                                      ":" + \
                                      self.password).encode('base64').rstrip()
        logging.debug("JiraRestBase object initialization is completed")

    def rest_req(self, url, data=None, req_type=None):
        """
        This method allows to make jira request
        url is valid rest-api url. type - string
        data is json data
        req_type is used for DELETE or PUT reuest
        """
        logging.debug("Make a request %s" % url)
        if data:
            request = urllib2.Request(url,
                data,
                {'Content-Type': 'application/json'})
        else:
            request = urllib2.Request(url)
        request.add_header('Authorization', self.auth_string)
        if req_type:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request.get_method = lambda: req_type
            raw_res = opener.open(request)
        else:
            raw_res = urllib2.urlopen(request)
        result = json.loads(raw_res.read()) if req_type != 'DELETE' else raw_res
        #logging.debug('Result is %s' % repr(result))
        logging.debug("Request completed")
        return result


class JIRAIssue(JiraRestBase):
    """
    Class for manipulation with Issue worklogs
    """
    def __init__(self, jirahost, login, password, issue_key, new=False):
        logging.info('Initialize JIRA Issue %s object' % issue_key)
        JiraRestBase.__init__(self, jirahost, login, password)
        self.issue_key = issue_key
        self.issue_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key
        self.add_url = self.jirahost + '/rest/api/2/issue/' +\
                       self.issue_key + '/worklog'
        self.jira_timeformat = '%Y-%m-%dT%H:%M:%S'
        self.worklog = {}
        self.new = new
        if self.new:
            self.get_issue_data()
        logging.debug('Initialization of %s is completed' % self.issue_key)

    def get_issue_data(self):
        logging.info('Request worklog for issue %s' % self.issue_key)
        strptime = datetime.datetime.strptime
        raw_issue_data = self.rest_req(self.issue_url)
        logging.debug('Parse worklogs')
        self.summary = raw_issue_data['fields']['summary']
        self.issue_id = int(raw_issue_data['id'])
        if not raw_issue_data['fields']['worklog']['worklogs']:
            logging.info('Worklog is emtpty for this issue')
        else:
            for a in raw_issue_data['fields']['worklog']['worklogs']:
                if a['author']['name'] == self.login:
                    self.worklog[int(a['id'])] = self.__parse_worklog(
                        a['started'],
                        a['timeSpentSeconds'],
                        a.get('comment', ''))
        logging.debug('Issue info collected')

    def add_worklog(self, start_date, end_date, comment=None):
        logging.debug('Adding worklog to issue %s' % self.issue_key)
        json_data = json.dumps(self.__prepare_worklog_data(start_date,
                                                           end_date,
                                                           comment))
        logging.debug('1: %s' % json_data)
        new_worklog = self.rest_req(self.add_url,
                                    data=json_data)

        self.worklog[int(new_worklog['id'])] = self.__parse_worklog(
            new_worklog['started'],
            new_worklog['timeSpentSeconds'],
            new_worklog.get('comment', ''))
        logging.debug('Worklog has been added')
        return { int(new_worklog['id']) : self.worklog[int(new_worklog['id'])] }

    def remove_worklog(self, worklog_id):
        logging.debug('Removing worklog %s' % worklog_id)
        remove_url = self.jirahost + '/rest/api/2/issue/' +\
                     self.issue_key + '/worklog/' + str(worklog_id)
        res = self.rest_req(remove_url, req_type='DELETE')
        if res.code == 204:
            del self.worklog[worklog_id]
            logging.debug('Worklog has been deleted.')

    def update_worklog(self, worklog_id, start_date=None,
                       end_date=None, comment=None):
        logging.debug('Updating worklog %s' % repr(worklog_id))
        upd_url = self.jirahost + '/rest/api/2/issue/' +\
                  self.issue_key + '/worklog/' + str(worklog_id)
        if start_date and end_date:
            data = self.__prepare_worklog_data(start_date, end_date, comment)
        elif comment:
            data = { 'comment' : comment }
        logging.debug('Update worklog with this data: %s ' % repr(data))
        json_data = json.dumps(data)
        updated_worklog = self.rest_req(upd_url, data=json_data, req_type='PUT')
        logging.debug(updated_worklog)
        self.worklog[worklog_id] = self.__parse_worklog(
            updated_worklog['started'],
            updated_worklog['timeSpentSeconds'],
            updated_worklog.get('comment', ''))
        return int(updated_worklog['id']), self.worklog[int(updated_worklog['id'])]

    def __parse_worklog(self, started, spent_seconds, comment):
        strptime = datetime.datetime.strptime
        time_spent = datetime.timedelta(seconds=spent_seconds)
        remote_started = strptime(started[:19], self.jira_timeformat)
        #logging.debug('Remote timestamp %s' % str(remote_started))
        utc_offset = utils.get_timedelta_from_utc_offset(started[-5:])
        utc_started = remote_started - utc_offset
        #logging.debug('UTC timestamp: %s' % str(utc_started))
        local_started = utc_started + utils.LOCAL_UTC_OFFSET_TIMEDELTA
        #logging.debug('Local timestamp: %s' % str(local_started))

        return local_started, local_started + time_spent, comment

    def __prepare_worklog_data(self, start_date, end_date, comment=None):
        started = start_date.strftime(self.jira_timeformat) + '.000' + utils.LOCAL_UTC_OFFSET
        spent = end_date - start_date
        data = {
            'started' : started,
            'timeSpentSeconds' : int(spent.total_seconds())
        }
        if comment:
            data['comment'] = comment
        return data

    def __int_round(self, x, base=5):
        logging.debug('Round %s' % str(x))
        return int(base * round(float(x)/base))

class JiraUser(JiraRestBase):
    def __init__(self, jirahost, login, password):
        logging.debug('Jira user object has been called')
        JiraRestBase.__init__(self, jirahost, login, password)
        self.user_url = str(self.jirahost) + '/rest/api/2/user?username=' + str(self.login)
        raw_user_data = self.rest_req(self.user_url)
        self.display_name = raw_user_data['displayName']
        self.email = raw_user_data['emailAddress']


    def get_assigned_issues(self):
        assigned_url = '%s/rest/api/2/search?jql=assignee="%s"+and+status!=Resolved+and+status!=Completed&fields=key' %(self.jirahost, self.login)
        self.assigned_issue_keys = []
        logging.debug('Request assigned issues')
        raw_assigned = self.rest_req(assigned_url)
        logging.debug('Parse assigned isses')
        for raw_issue in raw_assigned['issues']:
            self.assigned_issue_keys.append(raw_issue['key'])

