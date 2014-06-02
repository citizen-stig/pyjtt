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

from os import path
import logging
logger = logging.getLogger(__name__)

import db_accessor
import jira_accessor
import utils


class TimeTrackerApp(object):

    def __init__(self, hostname, login, password):
        self.jira_accessor = jira_accessor.JiraRESTAccessor(hostname, login, password)
        self.db_accessor = db_accessor.DBAccessor(self._get_db_filename(hostname, login))

    def get_user_info(self):
        return self.jira_accessor.get_user_info()

    @staticmethod
    def _get_db_filename(hostname, login):
        db_name = login + '_' \
            + hostname.replace('http://', '').replace('https://', '').replace('/', '').replace(':', '') \
            + '.db'
        return path.join(utils.get_app_working_dir(), db_name)

    def get_issue(self, issue_key):
        logger.info('Fetching issue with key "%s"' % issue_key)
        cached_issue = self.db_accessor.get_issue(issue_key)
        if not cached_issue:
            issue, worklog = self.jira_accessor.get_issue_by_key(issue_key)
            self.db_accessor.add_issue(issue)
            self.db_accessor.add_worklog(worklog)
            logger.info('Issue "%s" has been fetched from JIRA and stored in local db'
                        % str(issue_key))
            return issue
        else:
            return cached_issue

    def add_worklog_entry(self, worklog_entry):
        logger.info('Adding worklog entry to the issue: %s' % worklog_entry.issue)
        worklog_entry = self.jira_accessor.add_worklog_entry(worklog_entry)
        self.db_accessor.add_worklog_entry(worklog_entry)
        logger.info('Worklog entry for issue %s has been successfully added' % worklog_entry.issue)

    def remove_worklog_entry(self, worklog_entry):
        logger.info('Removing worklog entry to the issue: %s' % worklog_entry.issue)
        self.jira_accessor.remove_worklog_entry(worklog_entry)
        self.db_accessor.remove_worklog_entry(worklog_entry)
        logger.info('Worklog entry for issue %s has been successfully removed' % worklog_entry.issue)

    def update_worklog_entry(self, worklog_entry):
        logger.info('Updating worklog entry to the issue: %s' % worklog_entry.issue)
        self.jira_accessor.update_worklog_entry(worklog_entry)
        self.db_accessor.update_worklog_entry(worklog_entry)
        logger.info('Worklog entry for issue %s has been successfully updated' % worklog_entry.issue)

    def get_day_worklog(self, day):
        return self.db_accessor.get_day_worklog(day)

    def get_all_issues(self):
        return self.db_accessor.get_all_issues()

    def refresh_issue(self, issue):
        self.db_accessor.remove_issue(issue)
        return self.get_issue(issue.key)

    def remove_issue(self, issue):
        self.db_accessor.remove_issue(issue)

    def get_user_assigned_issues(self):
        issues_w_worklog = self.jira_accessor.get_user_assigned_issues()
        issues = []
        for issue, worklog in issues_w_worklog:
            self.db_accessor.add_issue(issue)
            self.db_accessor.add_worklog(worklog)
            issues.append(issues)
        return issues