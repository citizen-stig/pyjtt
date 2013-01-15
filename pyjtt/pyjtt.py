#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import os, sys, logging
from urllib2 import HTTPError
import db
from rest_wrapper import *

def get_issue_from_jira(creds, issue_key):
    issue = JIRAIssue(creds[0], creds[1], creds[2], issue_key, new=True)
    db.add_issue(creds[3],
        issue.issue_id,
        issue.issue_key,
        issue.summary)
    logging.debug('Issue %s' % repr(issue))
    logging.debug('Worklog %s' % repr(issue.worklog))
    db.add_issue_worklog(creds[3], issue.worklog, issue.issue_id)
    logging.debug('Info for issue %s is saved' % issue_key)
    return issue

def add_worklog(creds, issue, start_date, end_date, comment=None):
    added_worklog = issue.add_worklog(start_date, end_date, comment)
    db.add_issue_worklog(creds[3], added_worklog, issue.issue_id)

def remove_worklog(creds, issue, worklog_id):
    try:
        issue.remove_worklog(worklog_id)
    except HTTPError:
        logging.error('HTTP Error')
        return
    db.remove_issue_worklog(creds[3], worklog_id)

def update_worklog(creds, issue, worklog_id, start_date=None, end_date=None, comment=None):
    updated_worklog = issue.update_worklog(worklog_id, start_date, end_date, comment)
    logging.debug('Worklog updated in JIRA')
    logging.debug(updated_worklog)
    db.update_issue_worklog(creds[3], updated_worklog[0], updated_worklog[1][0], updated_worklog[1][1], updated_worklog[1][2])
