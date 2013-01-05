#!/usr/bin/env python2
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import sys, unittest, os, datetime
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import utils

class pyjttUtilsTest(unittest.TestCase):

    def test_get_db_filename(self):
        # simple
        db_filename = utils.get_db_filename('user', 'http://example.com/')
        self.assertEqual(db_filename, 'user_example.com.db')

        db_filename = utils.get_db_filename('user', 'example.com/')
        self.assertEqual(db_filename, 'user_example.com.db')

        db_filename = utils.get_db_filename('user', 'https://example.com/')
        self.assertEqual(db_filename, 'user_example.com.db')

        db_filename = utils.get_db_filename('user', 'jira.example.com/')
        self.assertEqual(db_filename, 'user_jira.example.com.db')

        db_filename = utils.get_db_filename('user', 'http://example.com/jira')
        self.assertEqual(db_filename, 'user_example.comjira.db')

    def test_get_local_utc_offset_simple(self):
        # simple
        # MSK
        now = datetime.datetime(2013, 01, 04, 16, 35)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+0400')
        # PST
        now = datetime.datetime(2013, 01, 04, 04, 35)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'-0800')
        # Kabul
        now = datetime.datetime(2013, 01, 04, 17, 05)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+0430')
        # GMT
        now = datetime.datetime(2013, 01, 04, 12, 35)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+0000')
        # UTC -12
        now = datetime.datetime(2013, 01, 04, 00, 35)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'-1200')
        # UTC +14
        now = datetime.datetime(2013, 01, 05, 02, 35)
        utcnow = datetime.datetime(2013, 01, 04, 12, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+1400')
        # Imaginary -530
        now = datetime.datetime(2013, 01, 04, 11, 05)
        utcnow = datetime.datetime(2013, 01, 04, 16, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'-0530')
    def test_get_local_utc_offset_advanced(self):
        # advanced
        # MSK
        now = datetime.datetime(2013, 01, 04, 01, 35)
        utcnow = datetime.datetime(2013, 01, 03, 21, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+0400')
        # PST
        now = datetime.datetime(2013, 01, 03, 19, 35)
        utcnow = datetime.datetime(2013, 01, 04, 03, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'-0800')
        # Kabul
        now = datetime.datetime(2013, 01, 04, 02, 35)
        utcnow = datetime.datetime(2013, 01, 03, 22, 05)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'+0430')
        # Imaginary -530
        now = datetime.datetime(2013, 01, 03, 21, 05)
        utcnow = datetime.datetime(2013, 01, 04, 02, 35)
        self.assertEqual(utils.get_local_utc_offset(now, utcnow),'-0530')
    def test_get_local_utc_offset_errors(self):
        # wrong year
        now = datetime.datetime(2011, 01, 03, 13, 35)
        utcnow = datetime.datetime(2013, 01, 04, 02, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)
        # less than -1200
        now = datetime.datetime(2013, 01, 03, 13, 35)
        utcnow = datetime.datetime(2013, 01, 04, 02, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)
        # more than +1400
        now = datetime.datetime(2013, 01, 04, 16, 36)
        utcnow = datetime.datetime(2013, 01, 04, 02, 35)
        self.assertRaises(ValueError, utils.get_local_utc_offset, now, utcnow)

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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(pyjttUtilsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)