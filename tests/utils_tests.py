#!/usr/bin/env python
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import sys
import unittest
import os
import datetime


sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import utils


class pyjttUtilsTest(unittest.TestCase):


    # utils.get_local_utc_offset
    def test_get_local_utc_offset_simple(self):
        # simple
        # MSK
        now = datetime.datetime(2013, 1, 4, 16, 35)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '+0400')
        # PST
        now = datetime.datetime(2013, 1, 4, 4, 35)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '-0800')
        # Kabul
        now = datetime.datetime(2013, 1, 4, 17, 5)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '+0430')
        # GMT
        now = datetime.datetime(2013, 1, 4, 12, 35)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '+0000')
        # UTC -12
        now = datetime.datetime(2013, 1, 4, 00, 35)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '-1200')
        # UTC +14
        now = datetime.datetime(2013, 1, 5, 2, 35)
        utcnow = datetime.datetime(2013, 1, 4, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '+1400')
        # Imaginary -530
        now = datetime.datetime(2013, 1, 4, 11, 5)
        utcnow = datetime.datetime(2013, 1, 4, 16, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow), '-0530')
        # Different minutes MSK
        # TODO: Fix this
        #now = datetime.datetime(2013, 1, 4, 11, 5)
        #utcnow = datetime.datetime(2013, 1, 4, 7, 4)
        #self.assertEqual(utils.get_local_utc_offset(now, utcnow), '+0400')

    def test_get_local_utc_offset_errors(self):
        # wrong year
        now = datetime.datetime(2011, 1, 3, 13, 35)
        utcnow = datetime.datetime(2013, 1, 4, 2, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)
        # less than -1200
        now = datetime.datetime(2013, 1, 3, 13, 35)
        utcnow = datetime.datetime(2013, 1, 4, 2, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)
        # more than +1400
        now = datetime.datetime(2013, 1, 4, 16, 36)
        utcnow = datetime.datetime(2013, 1, 4, 2, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)

    # utils.get_timedelta_from_utc_offset
    def test_get_timedelta_from_utc_simple(self):
        time_string = '2012-12-01T22:35:00.000+0400'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=4))
        time_string = '2012-12-01T22:35:00.000+0430'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=4, minutes=30))
        time_string = '-0700'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=-7, minutes=00))
        time_string = '2012-12-01T22:35:00.0000-0930'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=-9, minutes=30))
        time_string = '2012-12-01T22:35:00.0000+1400'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=14, minutes=00))
        time_string = '2012-12-01T22:35:00.0000-1200'
        self.assertEqual(utils.get_timedelta_from_utc_offset(time_string),
                         datetime.timedelta(hours=-12, minutes=0))

    # utils.get_time_spent_string
    def test_get_time_spent_string_normal(self):
        start = datetime.datetime(2013, 1, 2, 15)
        end = datetime.datetime(2013, 1, 2, 17)
        self.assertEqual(utils.get_time_spent_string(end - start), '2h')
        start = datetime.datetime(2013, 1, 2, 15)
        end = datetime.datetime(2013, 1, 2, 15, 30)
        self.assertEqual(utils.get_time_spent_string(end - start), '30m')
        start = datetime.datetime(2013, 1, 2, 15)
        end = datetime.datetime(2013, 1, 2, 17, 30)
        self.assertEqual(utils.get_time_spent_string(end - start), '2h 30m')

    def test_check_jira_issue(self):
        self.assertTrue(utils.check_jira_issue_key('SAMPLE-123'))
        self.assertFalse(utils.check_jira_issue_key(''))
        self.assertFalse(utils.check_jira_issue_key('SAMPLE'))
        self.assertFalse(utils.check_jira_issue_key('321'))
        self.assertFalse(utils.check_jira_issue_key('SAMPLE123'))
        self.assertFalse(utils.check_jira_issue_key('-'))
        self.assertFalse(utils.check_jira_issue_key('sample-123'))

    def test_get_app_workdir(self):
        workdir = utils.get_app_working_dir()
        self.assertTrue(os.access(os.path.dirname(workdir), os.W_OK))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(pyjttUtilsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)