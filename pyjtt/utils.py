#!/usr/bin/env python
#
from __future__ import unicode_literals
from datetime import datetime, timedelta
import ConfigParser, logging, sys, os

__author__ = 'Nikolay Golub'

def get_settings(config_filename):
    logging.debug('Getting base options')
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
        logging.warning('Section %s is missed in configuration file %s' % (e[0], config_filename))
        logging.warning('Return default values')
        defaults = config.defaults()
        return defaults['host'], defaults['login'], defaults['password'],
    logging.info('Options have been red')
    return jirahost, login, password

def save_settings(config_filename, creds):
    logging.debug('Saving configuration')
    if len(creds) != 3:
        raise ValueError('Credentials tuple is incomplete')
    config = ConfigParser.ConfigParser()
    config.add_section('jira')
    config.set('jira', 'host', creds[0])
    config.set('jira', 'login', creds[1])
    config.set('jira', 'password', creds[2])
    with open(config_filename, 'wb') as configfile:
        config.write(configfile)
    logging.debug('Options have been saved')

def get_db_filename(login, jirahost):
    # TODO: add absolute path handling
    return login + '_'\
           + jirahost.replace('http://', '').replace('https://', '').replace('/','').replace(':', '') \
           + '.db'

def get_local_utc_offset(now, utcnow):
    logging.debug('Getting local UTC Offset')
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
    #logging.debug('Getting timedelta from UTC offset')
    utc_offset = time_string[-5:]
    hours = int(utc_offset[0:3])
    minutes = int(utc_offset[3:5])
    # TODO: add bound values checking
    return timedelta(hours=hours, minutes=minutes)


def get_time_spent_string(timestamp_start, timestamp_end):
    logging.debug('Convert time bounds to time spent string')
    raw_spent = timestamp_end\
                - timestamp_start
    hours, seconds = divmod(raw_spent.seconds, 3600)
    minutes = seconds / 60
    spent = ''
    if hours:
        spent += str(hours) + 'h'
    if minutes:
        spent += ' ' + str(minutes) + 'm'
    spent_str = spent.strip()
    logging.debug('Convertion of time bounds to time stpent string is completed')
    return spent_str

LOCAL_UTC_OFFSET = get_local_utc_offset(datetime.now(), datetime.utcnow())
LOCAL_UTC_OFFSET_TIMEDELTA = get_timedelta_from_utc_offset(LOCAL_UTC_OFFSET)