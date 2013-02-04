#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta
import ConfigParser
from custom_logging import logger
import urllib2
import sys
import os

__author__ = 'Nikolay Golub'

def get_settings(config_filename):
    logger.debug('Getting base options')
    #config = ConfigParser.ConfigParser()
    config = ConfigParser.SafeConfigParser({'host': '',
                                            'login': '',
                                            'password': ''})
    config.read(config_filename)
    try:
        jirahost = config.get('jira', 'host', '')
        login = config.get('jira', 'login', '')
        password = config.get('jira', 'password', '')
    except ConfigParser.NoSectionError as e:
        logger.warning('Section %s is missed in configuration file %s' % (e[0], config_filename))
        logger.warning('Return default values')
        defaults = config.defaults()
        return defaults['host'], defaults['login'], defaults['password'],
    logger.info('Options have been red')
    return jirahost, login, password

def save_settings(config_filename, creds):
    logger.debug('Saving configuration')
    if len(creds) != 3:
        raise ValueError('Credentials tuple is incomplete')
    config = ConfigParser.ConfigParser()
    config.add_section('jira')
    config.set('jira', 'host', creds[0])
    config.set('jira', 'login', creds[1])
    config.set('jira', 'password', creds[2])
    with open(config_filename, 'wb') as configfile:
        config.write(configfile)
    logger.debug('Options have been saved')

def get_db_filename(login, jirahost):
    # TODO: add absolute path handling
    return login + '_'\
           + jirahost.replace('http://', '').replace('https://', '').replace('/','').replace(':', '') \
           + '.db'

def get_local_utc_offset(now, utcnow):
    logger.debug('Getting local UTC Offset')
    def absolute_offset(bigger_timestamp, smaller_timestamp):
        offset = bigger_timestamp.hour - smaller_timestamp.hour
        minutes = bigger_timestamp.minute - smaller_timestamp.minute
        hours_diff = abs(bigger_timestamp.hour - smaller_timestamp.hour)
        if minutes < 0:
            hours_diff -= 1
        if bigger_timestamp.day != smaller_timestamp.day:
            hours_diff = abs(hours_diff - 24)
        offset = '%02d%02d' % ( hours_diff, abs(minutes))
        return offset
    if (now-utcnow).total_seconds() > 50400 or (now-utcnow).total_seconds() < -43200:
        raise ValueError('Offset is too large')
    if now >= utcnow:
        sign = '+'
        offset = absolute_offset(now, utcnow)
    else:
        sign ='-'
        offset = absolute_offset(utcnow, now)
    return sign + offset

def get_timedelta_from_utc_offset(time_string):
    utc_offset = time_string[-5:]
    hours = int(utc_offset[0:3])
    minutes = int(utc_offset[3:5])
    # TODO: add bound values checking
    return timedelta(hours=hours, minutes=minutes)


def get_time_spent_string(t_delta):
    #raw_spent = timestamp_end\
    #            - timestamp_start
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
    splitted = issue_key.split('-')
    if len(splitted) == 2:
        return splitted[1].isdigit() and splitted[0].isalpha() and splitted[0].isupper()
    else:
        return False

def check_url_host(url):
    try:
        urllib2.urlopen(url,timeout=3)
        logger.info('Host %s is ok and accessible' % str(url))
        return True
    except urllib2.URLError as urlerr:
        logger.warning('Problem to access URL: "%s": %s' % (str(url), urlerr))
    except ValueError as valerr:
        logger.error('URL: "%s" is not an valid url' % url)
    return False

def get_app_working_dir():
    app_name = 'pyjtt'
    if 'linux' in sys.platform:
        return os.path.join(os.environ['HOME'], '.' + app_name)
    elif 'win' in sys.platform:
        return os.path.join(os.environ['APPDATA'], app_name)
    else:
        return os.path.abspath('.' + app_name)


LOCAL_UTC_OFFSET = get_local_utc_offset(datetime.now(), datetime.utcnow())
LOCAL_UTC_OFFSET_TIMEDELTA = get_timedelta_from_utc_offset(LOCAL_UTC_OFFSET)