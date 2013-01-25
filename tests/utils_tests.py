#!/usr/bin/env python2
from __future__ import unicode_literals
__author__ = 'Nikolay Golub'
import sys, unittest, os, datetime, ConfigParser
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

import utils

def _write_sample_file(filename, data):
    sample_file = open(filename, 'w')
    sample_file.write(data)
    sample_file.close()

class pyjttUtilsTest(unittest.TestCase):
# utils.get_db_filename
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

# utils.get_local_utc_offset
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

# utils.get_settings
    def test_get_settings_sanity(self):
        normal_filename = 'normal.cfg'
        normal = ("[jira]\n"
                  "host = http://jira.example.com\n"
                  "login = username\n"
                  "password = secret\n")
        _write_sample_file(normal_filename, normal)
        host, login, password  = utils.get_settings(normal_filename)
        self.assertEqual(host, 'http://jira.example.com')
        self.assertEqual(login, 'username')
        self.assertEqual(password, 'secret')
        os.remove(normal_filename)

    def test_get_settings_empty(self):
        # emtpy host
        empty_filename = 'empty.cfg'
        empty = ("[jira]\n"
                  "host = \n"
                  "login = username\n"
                  "password = secret\n")
        _write_sample_file(empty_filename, empty)
        host, login, password  = utils.get_settings(empty_filename)
        self.assertEqual(host, '')
        self.assertEqual(login, 'username')
        self.assertEqual(password, 'secret')
        os.remove(empty_filename)
        empty_filename = 'empty.cfg'
        empty = ("[jira]\n"
                 "host = http://jira.example.com\n"
                 "login = \n"
                 "password = secret\n")
        _write_sample_file(empty_filename, empty)
        host, login, password  = utils.get_settings(empty_filename)
        self.assertEqual(host, 'http://jira.example.com')
        self.assertEqual(login, '')
        self.assertEqual(password, 'secret')
        os.remove(empty_filename)
        empty_filename = 'empty.cfg'
        empty = ("[jira]\n"
                 "host = http://jira.example.com\n"
                 "login = username\n"
                 "password = \n")
        _write_sample_file(empty_filename, empty)
        host, login, password  = utils.get_settings(empty_filename)
        self.assertEqual(host, 'http://jira.example.com')
        self.assertEqual(login, 'username')
        self.assertEqual(password, '')
        os.remove(empty_filename)

    def test_get_settings_missed(self):
        # emtpy host
        missed_filename = 'missed.cfg'
        missed = ("[jira]\n"
                 "login = username\n"
                 "password = secret\n")
        _write_sample_file(missed_filename, missed)
        host, login, password  = utils.get_settings(missed_filename)
        self.assertEqual(host, '')
        self.assertEqual(login, 'username')
        self.assertEqual(password, 'secret')
        os.remove(missed_filename)
        missed_filename = 'missed.cfg'
        missed = ("[jira]\n")
        _write_sample_file(missed_filename, missed)
        host, login, password  = utils.get_settings(missed_filename)
        self.assertEqual(host, '')
        self.assertEqual(login, '')
        self.assertEqual(password, '')
        os.remove(missed_filename)
        missed_filename = 'missed.cfg'
        missed = ("\n\n")
        _write_sample_file(missed_filename, missed)
        host, login, password  = utils.get_settings(missed_filename)
        self.assertEqual(host, '')
        self.assertEqual(login, '')
        self.assertEqual(password, '')
        os.remove(missed_filename)

    def test_get_settings_errors(self):
        self.assertEqual(utils.get_settings('no_such_file'), ('', '', ''))
        self.assertEqual(utils.get_settings(''), ('', '', ''))


# utils.save_settings
    def test_save_settings_normal(self):
        normal_filename = 'save_simple.cfg'
        creds = ( 'http://jira.example.com', 'username', 'secret')
        utils.save_settings(normal_filename, creds)
        r_creds = utils.get_settings(normal_filename)
        self.assertEqual(creds, r_creds)
        os.remove(normal_filename)

    def test_save_settings_adv(self):
        adv_filename = 'save_simple.cfg'
        creds = ( '', 'username', 'secret')
        utils.save_settings(adv_filename, creds)
        r_creds = utils.get_settings(adv_filename)
        self.assertEqual(creds, r_creds)
        os.remove(adv_filename)
        adv_filename = 'save_simple.cfg'
        creds = ( 'http://jira.example.com', '', 'secret')
        utils.save_settings(adv_filename, creds)
        r_creds = utils.get_settings(adv_filename)
        self.assertEqual(creds, r_creds)
        os.remove(adv_filename)
        creds = ( 'http://jira.example.com', 'username', '')
        utils.save_settings(adv_filename, creds)
        r_creds = utils.get_settings(adv_filename)
        self.assertEqual(creds, r_creds)
        os.remove(adv_filename)

    def test_save_settings_errors(self):
        # wrong file name, etc
        creds = ( 'http://jira.example.com', 'username', 'secret')
        with self.assertRaises(IOError):
            utils.save_settings(os.path.join('no', 'such', 'file'), creds)
        creds = ( 'http://jira.example.com', 'username')
        with self.assertRaises(ValueError):
            utils.save_settings(os.path.join('example'), creds)


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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(pyjttUtilsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)