#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from . import db_accessor
from . import jira_accessor


class TimeTrackerApp(object):

    def __init__(self):
        self.jira_accessor = jira_accessor.JiraRESTAccessor('test', 'test', 'test')
        self.db_accessor = db_accessor.DBAccessor('test')

    def get_issue_from_jira(self, issue_key):
        logger.info('Fetching issue with key "%s"' % issue_key)
        issue = self.jira_accessor.get_issue_by_key(issue_key)
        self.db_accessor.add_issue(issue)
        worklog = self.jira_accessor.get_worklog_for_issue(issue)
        self.db_accessor.add_worklog(issue.key, worklog)
        logger.info('Issue "%s" has been fetched from JIRA and stored in local db'
                    % str(issue_key))
        return issue


    def add_worklog(self, issue, worklog_entry):
        pass

    def remove_worklog(self, issue, worklog_entry):
        pass

    def update_worklog(self, issue, old_worklog_entry, new_worklog_entry):
        pass

    def get_day_worklog(self, day):
        pass
