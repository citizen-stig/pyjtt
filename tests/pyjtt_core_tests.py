#!/usr/bin/env python
#
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'

import urllib2, json, unittest, sys, logging, os, datetime, random
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import core

class pyjttCoreTest(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
