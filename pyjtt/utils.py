import os
import pathlib
import sys
import configparser
import logging
import platform
from datetime import datetime, timedelta

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"

logger = logging.getLogger(__name__)

CONFIG_FILENAME = 'pyjtt.cfg'

try:
    BASE_PATH = sys._MEIPASS
except AttributeError:
    BASE_PATH = os.path.normpath(os.path.join(
        pathlib.Path(__file__).parent, '..')
    )


def get_resource_path(relative_path):
    return os.path.join(BASE_PATH, relative_path)


def get_app_working_dir():
    """Returns path to application operational folder.

    Options and local database are stored in this folder.
    """
    app_name = 'pyjtt'
    current_platform = platform.system()
    if current_platform in ('Linux', 'Darwin'):
        return os.path.join(os.environ['HOME'], '.' + app_name)
    elif 'Windows' == current_platform:
        return os.path.join(os.environ['APPDATA'], app_name)
    else:
        return os.path.abspath('.' + app_name)


def init_config(workdir=None):
    """
    Prepares config class for usage
    """
    if workdir is None:
        workdir = get_app_working_dir()
    defaults = {'log_level': 'INFO'}
    for item in ('jirahost', 'login', 'password', 'save_password'):
        defaults[item] = ''

    config_filename = os.path.join(workdir, CONFIG_FILENAME)
    config = configparser.RawConfigParser(defaults=defaults)
    config.read(config_filename)

    if not config.has_section('main'):
        config.add_section('main')
    return config


def write_config(config):
    workdir = get_app_working_dir()
    with open(os.path.join(workdir, CONFIG_FILENAME), 'w') as configfile:
        config.write(configfile)


def get_local_utc_offset(now, utcnow):
    """Calculates local UTC offset. Returns string"""
    logger.debug('Getting local UTC Offset')

    def absolute_offset(bigger_timestamp, smaller_timestamp):
        minutes = bigger_timestamp.minute - smaller_timestamp.minute
        # Case when, minutes can be differ on one minute because
        # of time gap between now and utcnow. This difference cannot
        # be more than one minute
        if minutes == 1:
            minutes = 0
        hours_diff = abs(bigger_timestamp.hour - smaller_timestamp.hour)
        if minutes < 0:
            hours_diff -= 1
        if bigger_timestamp.day != smaller_timestamp.day:
            hours_diff = abs(hours_diff - 24)
        offset = '%02d%02d' % (hours_diff, abs(minutes))
        return offset

    if (now - utcnow).total_seconds() > 50400 \
        or (now - utcnow).total_seconds() < -43200:
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
        return splitted[1].isdigit() and splitted[0].isalpha() \
               and splitted[0].isupper()
    else:
        return False


# global variables, that can be used by other modules
LOCAL_UTC_OFFSET = get_local_utc_offset(datetime.now(), datetime.utcnow())
LOCAL_UTC_OFFSET_TIMEDELTA = get_timedelta_from_utc_offset(LOCAL_UTC_OFFSET)
