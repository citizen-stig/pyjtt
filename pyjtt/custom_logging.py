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
#    This module handles all logging events from other modules of PyJTT.
#
#

from __future__ import unicode_literals

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2013, Nikolay Golub"
__license__ = "GPL"

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


