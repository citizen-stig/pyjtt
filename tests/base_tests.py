#!/usr/bin/env python2
#
# test module for pyjtt

import unittest, os, sys, ConfigParser, logging, datetime

# add folder concat
sys.path.insert(0, os.path.abspath(os.path.join('..','pyjtt')))

from base_jira_rest import *

class pyjttTestEnv(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.ERROR)
        config = ConfigParser.ConfigParser()
        config.read('test.cfg')
        if config:
                try:
                    self.jirahost = config.get('jira', 'host')
                    self.jirauser = config.get('jira', 'user')
                    self.password = config.get('jira', 'password')
                    self.display_name = config.get('jira', 'display_name')
                    self.empty_issue_key = config.get('jira', 'empty_issue')
                    self.nonempty_issue_key = config.get('jira', 'nonempty_issue')
                    self.email = config.get('jira', 'email')
                except ConfigParser.NoSectionError as e:
                    logging.error('Section %s is missed in configuration file!' % e[0])
                    sys.exit(1)
                except ConfigParser.NoOptionError as e:
                    logging.error('Option %s is missed in configuration file!' % e[0])
                    sys.exit(1)
        else:
            logging.error('Error, no config file, exit')
            sys.exit(1)
        self.wt = WorklogsTable(self.jirauser, self.password, self.jirahost)



    def tearDown(self):
        os.remove(self.wt.dbname)
        del self.wt


class pyjttBaseTests(pyjttTestEnv):
    def test_user_data(self):
        self.assertEqual(self.display_name, self.wt.user_display_name)
        self.assertEqual(self.email, self.wt.email)

    def test_get_empty_worklog(self):
        self.assertFalse(self.wt.get_worklog(self.empty_issue_key))

    def test_get_nonempty_worklog(self):
        self.assertTrue(self.wt.get_worklog(self.nonempty_issue_key))

    def test_check_sqlite(self):
        self.assertTrue(os.path.isfile(self.wt.dbname))


    def test_wrong_credentials(self):
        with self.assertRaises(urllib2.HTTPError) as cm1:
            wt1 = WorklogsTable(self.jirauser, 'definetly_wrong_password', self.jirahost)
        with self.assertRaises(urllib2.HTTPError) as cm2:
            wt2 = WorklogsTable('no_such_user', self.password, self.jirahost)
        for cm in (cm1,cm2):
            self.assertEqual(cm.exception.code, 401)
            self.assertEqual(cm.exception.msg, 'Unauthorized')


    def test_wrong_host(self):
        with self.assertRaises(urllib2.HTTPError) as cm1:
            wt1 = WorklogsTable(self.jirauser, self.password, 'http://google.com')
        self.assertEqual(cm1.exception.code, 404)
        self.assertEqual(cm1.exception.msg, 'Not Found')
        with self.assertRaises(urllib2.URLError) as cm2:
            wt2 = WorklogsTable(self.jirauser, self.password, 'http://qwebgbgbgbgbgefdkfdsfr.ru')
        wt3 = WorklogsTable(self.jirauser, self.password, self.jirahost.replace('http://', ''))
        self.assertTrue(wt3)



class pyjttWorklogsTests(pyjttTestEnv):
    def setUp(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.ERROR)
        pyjttTestEnv.setUp(self)
        """
        config = ConfigParser.ConfigParser()
        config.read('test.cfg')
        if config:
                try:
                    self.jirahost = config.get('jira', 'host')
                    self.jirauser = config.get('jira', 'user')
                    self.password = config.get('jira', 'password')
                    self.display_name = config.get('jira', 'display_name')
                    self.empty_issue_key = config.get('jira', 'empty_issue')
                    self.nonempty_issue_key = config.get('jira', 'nonempty_issue')
                except ConfigParser.NoSectionError as e:
                    logging.error('Section %s is missed in configuration file!' % e[0])
                    sys.exit(1)
                except ConfigParser.NoOptionError as e:
                    logging.error('Option %s is missed in configuration file!' % e[0])
                    sys.exit(1)
        else:
            logging.error('Error, no config file, exit')
            sys.exit(1)
        self.wt = WorklogsTable(self.jirauser, self.password, self.jirahost)
        """
        self.worklogid = self.wt.add_worklog(self.nonempty_issue_key,
                                        datetime.datetime.now() - datetime.timedelta(minutes=10),
                                        datetime.datetime.now())

    def tearDown(self):
        pyjttTestEnv.tearDown(self)
        #add deletion of worklog


    def test_change_worklog(self):
        if self.worklogid:
            pass
        else:
            self.skipTest('Worklog hasn\'t been created')


    def test_remove_worklog(self):
        if self.worklogid:
            pass
            self.worklog = None
        else:
            self.skipTest('Worklog hasn\'t been created')


if __name__ =='__main__':
    unittest.main()

