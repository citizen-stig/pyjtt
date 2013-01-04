#!/usr/bin/env python
#
from __future__ import unicode_literals
from datetime import datetime, timedelta
import ConfigParser, logging

__author__ = 'Nikolay Golub'

def get_settings(config_filename):
    logging.debug('Getting base options')
    config = ConfigParser.ConfigParser()
    logging.debug('Config file exists, read options')
    config.read(config_filename)
    try:
        jirahost = config.get('jira', 'host')
        login = config.get('jira', 'login')
        password = config.get('jira', 'password')
    except ConfigParser.NoSectionError as e:
        logging.error('Section %s is missed in configuration file!' % e[0])
        sys.exit(1)
    except ConfigParser.NoOptionError as e:
        logging.error('Option %s is missed in configuration file!' % e[0])
        sys.exit(1)
    logging.debug('Options have been red')
    return jirahost, login, password

def save_settings(config_filename, creds):
    logging.debug('Saving configuration')
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
    return login + '_' + jirahost.replace('http://', '').replace('https://', '').replace('/','').replace(':', '') \
           + '.db'



def get_local_utc_offset():
    now, utcnow = (datetime.now(), datetime.utcnow())
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
    if now > utcnow:
        sign = '+'
        offset = absolute_offset(now, utcnow)
    else:
        sign ='-'
        offset = absolute_offset(utcnow, now)
    return sign + offset


def get_timedelta_from_utc_offset(utc_offset):
    return timedelta(hours=int(utc_offset[1:3]), minutes= int(utc_offset[3:5]))


LOCAL_UTC_OFFSET = get_local_utc_offset()
LOCAL_UTC_OFFSET_TIMEDELTA = get_timedelta_from_utc_offset(LOCAL_UTC_OFFSET)