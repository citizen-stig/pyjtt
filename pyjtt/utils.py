#!/usr/bin/env python
#
from __future__ import unicode_literals
from datetime import datetime
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
    return login + '_' + jirahost.replace('http://', '').replace('/','').replace(':', '')\
           + '.db'



