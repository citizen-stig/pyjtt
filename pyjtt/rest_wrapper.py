#!/usr/bin/env python
#
__author__ = 'Nikolay Golub'


import urllib2, json, logging, datetime

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
            raw_result = opener.open(request)
        else:
            raw_result = urllib2.urlopen(request)
        result = json.loads(raw_result.read()) if req_type != 'DELETE' else raw_result
        logging.debug('Result is %s' % repr(result))
        logging.debug("Request completed")
        return result


class JIRAIssue(JiraRestBase):
    """
    Class for manipulation with Issue worklogs
    """
    def __init__(self, jirahost, login, password, issue_key):
        logging.debug('Initialize JIRA Issue object')
        JiraRestBase.__init__(self, jirahost, login, password)
        self.issue_key = issue_key
        self.issue_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key
        self.add_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key + '/worklog'
        self.jira_timeformat = '%Y-%m-%dT%H:%M:%S'
        self.worklog = {}
        self.get_worklog()
        logging.debug('Initialization completed')

    def get_worklog(self):
        logging.info('Request worklog for issue %s' % self.issue_key)
        strptime = datetime.datetime.strptime
        raw_issue_data = self.rest_req(self.issue_url)
        logging.debug(raw_issue_data)
        logging.debug('Parse worklogs')
        if not raw_issue_data['fields']['worklog']['worklogs']:
            logging.info('Worklog is emtpty for this issue')
        else:
            #logging.debug('1')
            for a in raw_issue_data['fields']['worklog']['worklogs']:
                #logging.debug('2')
                if a['author']['name'] == self.login:
                    #logging.debug('3')
                    self.worklog[a['id']] = self.__parse_worklog(a['started'],
                                                                 a['timeSpentSeconds'],
                                                                 a['comment'])
                    #logging.debug('4')
        logging.debug(self.worklog)

    def add_worklog(self, start_date, end_date, comment=None):
        logging.debug('Adding worklog to issue %s' % self.issue_key)
        json_data = json.dumps(self.__prepare_worklog_data(start_date, end_date, comment))
        logging.debug('1: %s' % json_data)
        new_worklog = self.rest_req(self.add_url,
                                    data=json_data)
        print new_worklog
        self.worklog[new_worklog['id']] = self.__parse_worklog(new_worklog['started'],
                                                               new_worklog['timeSpentSeconds'],
                                                               new_worklog['comment'])
        logging.debug('Worklog has been added')
        return new_worklog

    def remove_worklog(self, worklog_id):
        logging.debug('Removing worklog %s' % worklog_id)
        remove_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key + '/worklog/' + worklog_id
        res = self.rest_req(remove_url, req_type='DELETE')
        if res.code == 204:
            del self.worklog[worklog_id]
        logging.debug('Worklog has been deleted.')

    def update_worklog(self, worklog_id, start_date=None, end_date=None, comment=None):
        logging.debug('Updating worklog %s' % repr(worklog_id))
        upd_url = self.jirahost + '/rest/api/2/issue/' + self.issue_key + '/worklog/' + worklog_id
        if start_date and end_date:
            # TODO: add timezone offset calculation
            data = self.__prepare_worklog_data(start_date, end_date, comment)
        elif comment:
            data = { 'comment' : comment }
        json_data = json.dumps(data)
        updated_worklog = self.rest_req(upd_url, data=json_data, req_type='PUT')
        logging.debug(updated_worklog)
        self.worklog[worklog_id] = self.__parse_worklog(updated_worklog['started'],
                                                        updated_worklog['timeSpentSeconds'],
                                                        updated_worklog['comment'])
        logging.debug('Worklog updated')

    def __parse_worklog(self, started, spent_seconds, comment):
        strptime = datetime.datetime.strptime
        time_spent = datetime.timedelta(seconds=spent_seconds)
        started = strptime(started[:19], self.jira_timeformat)
        return started, started + time_spent, comment

    def __prepare_worklog_data(self, start_date, end_date, comment=None):
        # TODO: add timezone offset calculation
        time_spent = ''
        started = start_date.strftime(self.jira_timeformat) + '.000+0400'
        spent = end_date - start_date
        if spent.days:
            time_spent += str(spent.days) +'d '
        elif spent.seconds:
            time_spent += str(self.__int_round(spent.seconds / 60 )) + 'm'
        # TODO: add handling of empty string
        time_spent = time_spent.strip()
        logging.debug('Time spent: %s' % time_spent)
        data = {
            'started' : started,
            'timeSpent' : time_spent
        }
        if comment:
            data['comment'] = comment
        return data

    def __int_round(self, x, base=5):
        logging.debug('Round %s' % str(x))
        return int(base * round(float(x)/base))