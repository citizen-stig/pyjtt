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
import os

import start

logger_instance=None


def _get_loglevel():
    DEFAULT_LOGLEVEL = 'INFO'
    config = ConfigParser.ConfigParser()
    try:
        config.read(start.config_filename)
        loglevel = config.get('main', 'loglevel', DEFAULT_LOGLEVEL).upper()
        if loglevel not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
            loglevel = DEFAULT_LOGLEVEL
    except ConfigParser.NoSectionError:
        loglevel = DEFAULT_LOGLEVEL
        config.add_section('main')
        config.set('main', 'loglevel', loglevel)
        if not os.path.isdir(start.get_app_working_dir()):
            os.mkdir(start.get_app_working_dir())
        with open(start.config_filename, 'wb') as config_file:
            config.write(config_file)
    except ConfigParser.NoOptionError:
        loglevel = DEFAULT_LOGLEVEL
        config.set('main', 'loglevel', loglevel)
        if not os.path.isdir(start.get_app_working_dir()):
            os.mkdir(start.get_app_working_dir())
        with open(start.config_filename, 'wb') as config_file:
            config.write(config_file)
    return loglevel


def get_logger():
    global logger_instance
    if logger_instance:
        return logger_instance
    LOG_FILENAME = os.path.join(start.get_app_working_dir(), 'pyjtt.log')
    logger = logging.getLogger('pyjtt_logger')
    loglevel = _get_loglevel()
    logger.setLevel(getattr(logging, loglevel))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s')
    rotater = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, mode='a', encoding='utf-8', maxBytes=10485760, backupCount=5)
    rotater.setFormatter(formatter)
    logger.addHandler(rotater)
    logger_instance = logger
    return logger

