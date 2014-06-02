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
#    This is module with a small utils functions


__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2014, Nikolay Golub"
__license__ = "GPL"

import os
import platform
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)


def get_app_working_dir():
    """Returns path to application operational folder.

    Options and local database are stored in this folder.
    """
    app_name = 'pyjtt'
    current_platform = platform.system()
    if 'Linux' == current_platform:
        return os.path.join(os.environ['HOME'], '.' + app_name)
    elif 'Windows' == current_platform:
        return os.path.join(os.environ['APPDATA'], app_name)
    else:
        return os.path.abspath('.' + app_name)


def get_local_utc_offset(now, utcnow):
    """Calculates local UTC offset. Returns string"""
    logger.debug('Getting local UTC Offset')

    def absolute_offset(bigger_timestamp, smaller_timestamp):
        minutes = bigger_timestamp.minute - smaller_timestamp.minute
        hours_diff = abs(bigger_timestamp.hour - smaller_timestamp.hour)
        if minutes < 0:
            hours_diff -= 1
        if bigger_timestamp.day != smaller_timestamp.day:
            hours_diff = abs(hours_diff - 24)
        offset = '%02d%02d' % (hours_diff, abs(minutes))
        return offset

    if (now - utcnow).total_seconds() > 50400 or (now - utcnow).total_seconds() < -43200:
        raise ValueError('Offset is too large')
    if now >= utcnow:
        sign = '+'
        offset = absolute_offset(now, utcnow)
    else:
        sign = '-'
        offset = absolute_offset(utcnow, now)
    return sign + offset


def get_timedelta_from_utc_offset(time_string):
    """Defines timedelta object from utc offset string"""
    utc_offset = time_string[-5:]
    hours = int(utc_offset[0:3])
    minutes = int(utc_offset[3:5])
    # TODO: add bound values checking
    return timedelta(hours=hours, minutes=minutes)


def get_time_spent_string(t_delta):
    """Converts timedelta object to time spent string."""
    hours, seconds = divmod(t_delta.total_seconds(), 3600)
    minutes = seconds / 60
    spent = ''
    if hours:
        spent += str(int(hours)) + 'h'
    if minutes:
        spent += ' ' + str(int(minutes)) + 'm'
    spent_str = spent.strip()
    return spent_str


def check_jira_issue_key(issue_key):
    """Checks syntax of JIRA issue key"""
    splitted = issue_key.split('-')
    if len(splitted) == 2:
        return splitted[1].isdigit() and splitted[0].isalpha() and splitted[0].isupper()
    else:
        return False


# global variables, that can be used by other modules
LOCAL_UTC_OFFSET = get_local_utc_offset(datetime.now(), datetime.utcnow())
LOCAL_UTC_OFFSET_TIMEDELTA = get_timedelta_from_utc_offset(LOCAL_UTC_OFFSET)

