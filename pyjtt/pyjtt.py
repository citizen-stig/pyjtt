#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
from custom_logging import logger
import db
from rest_wrapper import *

def get_issue_from_jira(creds, issue_key):
    logger.info('Fetching issue with key "%s"' % issue_key)
    issue = JIRAIssue(creds[0], creds[1], creds[2], issue_key, new=True)
    db.add_issue(creds[3], issue.issue_id, issue.issue_key, issue.summary)
    db.add_issue_worklog(creds[3], issue.worklog, issue.issue_id)
    logger.info('Issue "%s" has been fetched from JIRA and stored in local db'
                  % str(issue))
    return issue

def add_worklog(creds, issue, start_date, end_date, comment=None):
    logger.info('Adding new worklog for issue "%s"' % str(issue))
    added_worklog = issue.add_worklog(start_date, end_date, comment)
    db.add_issue_worklog(creds[3], added_worklog, issue.issue_id)
    logger.info('Worklog for issues "%s" has been added' % str(issue))

def remove_worklog(creds, issue, worklog_id):
    logger.info('Removing worklog for issue "%s"' % str(issue))
    issue.remove_worklog(worklog_id)
    db.remove_issue_worklog(creds[3], worklog_id)
    logger.info('Worklog for issue "%s" has been removed' % str(issue))

def update_worklog(creds, issue, worklog_id,
                   start_date=None, end_date=None, comment=None):
    logger.info('Updating worklog for issue "%s"' % str(issue))
    updated_worklog = issue.update_worklog(worklog_id, start_date,
        end_date, comment)
    db.update_issue_worklog(creds[3], updated_worklog[0],
        updated_worklog[1][0], updated_worklog[1][1], updated_worklog[1][2])
    logger.info('Worklog for issues "%s" has been updated')