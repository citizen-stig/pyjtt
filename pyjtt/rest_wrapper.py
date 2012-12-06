#!/usr/bin/env python
#
__author__ = 'Nikolay Golub'


import urllib2, json, logging

class JiraRestBase(object):
    """
    Wrapper class for making JIRA requests
    """
    def __init__(self, jirahost, login, password):
        # TODOL: think of jirahost validation
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
        result = json.loads(raw_result.read())
        logging.debug('Result is %s' % repr(result))
        logging.debug("Request completed")
        return result




