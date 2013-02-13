#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import logging.handlers
import ConfigParser

config_filename = 'pyjtt_app.cfg'
config = ConfigParser.SafeConfigParser({'loglevel': 'INFO'})
try:
    config.read(config_filename)
    loglevel = config.get('main', 'loglevel', 'DEBUG').upper()
    if loglevel not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        loglevel = config.defaults()['loglevel']
except ConfigParser.NoSectionError:
    loglevel = config.defaults()['loglevel']
    config.add_section('main')
    config.set('main', 'loglevel', loglevel)
    with open(config_filename, 'wb') as config_file:
        config.write(config_file)
except ConfigParser.NoOptionError:
    loglevel = config.defaults()['loglevel']
    config.set('main', 'loglevel', loglevel)
    with open(config_filename, 'wb') as config_file:
        config.write(config_file)

LOG_FILENAME = 'pyjtt.log'
logger = logging.getLogger('pyjtt_logger')
logger.setLevel(getattr(logging, loglevel))
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s')
rotater = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, mode='a', encoding='utf-8', maxBytes=10485760, backupCount=5)
rotater.setFormatter(formatter)
logger.addHandler(rotater)


