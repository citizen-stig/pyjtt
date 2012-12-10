#!/usr/bin/env python2

import urllib2, json, datetime, logging, sqlite3

class BaseJira(object):
    """Class for base interactions with JIRA via REST api"""
    def __init__(self):
        pass

    def req_api(self, url, login, passwd, data=None):
        if data:
            request = urllib2.Request(url, data,
                                      {'Content-Type': 'application/json'})
        else:
            request = urllib2.Request(url)
        request.add_header('Authorization',
                           'Basic ' \
                           + (login + ":" + passwd).encode('base64').rstrip())
        raw_result = urllib2.urlopen(request)
        result = json.loads(raw_result.read())
        return result

    def del_req(self, url, login, passwd):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header('Authorization',
            'Basic '\
            + (login + ":" + passwd).encode('base64').rstrip())
        request.get_method = lambda: 'DELETE'
        url = opener.open(request)
        logging.debug('Return code is %s' % url.code)
        # 204 Returned if delete was successful
        # 400 Returned if the input is invalid
        #   (e.g. missing required fields, invalid values, and so forth).
        # 403 Returned if the calling
        #   user does not have permission to delete the worklog

    def upd_req(self, url, login, passwd, data):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        request.add_header('Authorization',
            'Basic '\
            + (login + ":" + passwd).encode('base64').rstrip())
        request.get_method = lambda: 'PUT'
        url = opener.open(request)
        logging.debug('Return code is %s' % url.code)



class WorklogsTable(BaseJira):
    """Class for manipulation with JIRA worklogs"""

    def __init__(self, username, password, jirahost):
        BaseJira.__init__(self)
        self.username = username
        self.password = password
        if jirahost[:7] != 'http://':
            jirahost = 'http://' + jirahost
        self.jira = jirahost
        logging.debug('Trying to connect to %s' % self.jira)
        user_url = self.jira + '/rest/api/2/user?username=' + str(username)
        raw_user_info = self.req_api(user_url, self.username, self.password)
        self.user_display_name = raw_user_info['displayName']
        self.email = raw_user_info['emailAddress']
        del raw_user_info
        # create db name.
        self.dbname = self.username + '_'\
                      + self.jira.replace('http://', '').replace('/','').replace(':', '') \
                      + '.db'
        logging.debug('Dbname is %s' % self.dbname)
        logging.debug('Connection to sqlite database')
        self.db_conn = sqlite3.connect(self.dbname)
        cursor = self.db_conn.cursor()
        cursor.execute("""CREATE TABLE if not exists JIRAIssues
                        (jira_issue_id INTEGER PRIMARY KEY,
                        jira_issue_key TEXT,
                        summary TEXT,
                        link TEXT)""")
        cursor.execute("""CREATE TABLE if not exists Worklogs
                        (worklog_id INTEGER,
                         jira_issue_id INTEGER,
                         comment TEXT,
                         start_date TIMESTAMP,
                         end_date TIMESTAMP)""")
        self.db_conn.commit()
        logging.debug('Worklog Table object has been created')

    def __del__(self):
        if hasattr(self, 'db_conn'):
            logging.debug('Closing worklog database')
            self.db_conn.close()

    def get_worklog(self, issue_key):
        #TODO: add checking of jira key
        jira_timeformat = '%Y-%m-%dT%H:%M:%S'
        strptime = datetime.datetime.strptime
        if len(issue_key) < 3:
            logging.error('Jira issue key is too short')
            return
        issue_url = self.jira + '/rest/api/2/issue/' + issue_key
        #TODO: handle of unexisted issue
        logging.debug('Request worklog for issue %s' % issue_key)
        try:
            raw_issue_data = self.req_api(issue_url, self.username, self.password)
        except urllib2.HTTPError as e:
            logging.error('Can\'t get worklog for issue %s' % issue_key)
            logging.error(e)
            return

        formated_worklog = {}
        if not raw_issue_data['fields']['worklog']['worklogs']:
            logging.info('Worklog is emtpty for this issue')
            return
        else:
            for a in raw_issue_data['fields']['worklog']['worklogs']:
                if a['author']['name'] == self.username:
    #                end_date =
                    time_spent = datetime.timedelta(minutes=0)
                    for timeframe in a['timeSpent'].split(' '):
                        time_spent += self.__convert_to_timedelta(timeframe)
                    formated_worklog[a['id']] = ( strptime(a['started'][:19],
                                                            jira_timeformat),
                                                  strptime(a['started'][:19],
                                                            jira_timeformat) + \
                                                  time_spent,
                                                  a.get('comment', ''))
                # If issue hasn't been requested before, add id, key, summary
                # and link to jira_issues table, and add all worklogs
            if not formated_worklog:
                logging.info('User didn\'t spend time on this issue')
                return
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT '
                           '    jira_issue_key '
                           'FROM '
                           '    JIRAIssues '
                           'WHERE '
                           '    jira_issue_key = ?', [issue_key])
            issue_in_db = cursor.fetchone()

            if issue_in_db:
                logging.debug('Issue has been requested before, '
                              'start sync procedure for this issue')
                #TODO: add call of sync function
            else:
                # if issue has been requsted before, call sync table for this
                # issue
                logging.debug('Issue hasn\'t been requested before, '
                              'adding it to table')
                i = ( raw_issue_data['id'],
                      raw_issue_data['key'],
                      raw_issue_data['fields']['summary'])
                cursor.execute('INSERT INTO '
                               'JIRAIssues (jira_issue_id, jira_issue_key, summary) '
                               'VALUES (?,?,?)', i)
                for w_id, w_val in formated_worklog.iteritems():
                    entry = (int(w_id), int(raw_issue_data['id']), w_val[2], w_val[0], w_val[1] )
                    cursor.execute("""INSERT INTO Worklogs (worklog_id, jira_issue_id, comment, start_date, end_date)
                                    VALUES (?,?,?,?,?)""", entry)
                self.db_conn.commit()
            logging.debug('Worklog Table has been updated')

            return formated_worklog


    def add_worklog(self, issue_key, start_date, end_date, comment=None):
        logging.debug('Adding worklog to issue %s' % issue_key)
        add_url = self.jira + '/rest/api/2/issue/' + issue_key + '/worklog'
        # TODO: add timezone offset calculation
        time_spent = ''
        started = start_date.strftime('%Y-%m-%dT%H:%M:%S') + '.000+0400'
        # TODO : add checking of end and start date diffenrece
        spent = end_date - start_date
        if spent.days:
            time_spent += str(spent.days) +'d '
        elif spent.seconds:
            time_spent += str(self.__int_round(spent.seconds / 60 )) + 'm'
        # TODO: add handling of empty string
        time_spent = time_spent.strip()
        logging.debug('Time spent: %s' % time_spent)
        data = {
            'started' : started,
            'timeSpent' : time_spent
        }
        if comment:
            data['comment'] = comment
        #json_data = json.dumps({
        #    'comment': 'Test from python',
        #    "started": "2011-11-25T16:10:48.704+0400",
        #    "timeSpent": "3h 20m"
        #})
        json_data = json.dumps(data)
        logging.debug('1: %s' % json_data)
        new_worklog = self.req_api(add_url,
                                   self.username,
                                   self.password,
                                   json_data)
        # TODO: add checking of added worklog
        # TODO: add writing of added worklog to database
        return new_worklog

    def update_worklog(self, issue_key, worklog_id, start_date=None, end_date=None, comment=None):
        logging.debug('Update worklog')
        upd_url = self.jira + '/rest/api/2/issue/' + issue_key + '/worklog/' + worklog_id
        data = {}
        if start_date:
            data['started'] = start_date.strftime('%Y-%m-%dT%H:%M:%S') + '.000+0400'
        if end_date:
            time_spent = ''
            spent = end_date - start_date
            if spent.days:
                time_spent += str(spent.days) +'d '
            elif spent.seconds:
                time_spent += str(self.__int_round(spent.seconds / 60 )) + 'm'
            data['timeSpent'] = time_spent
        if comment:
            data['comment'] = comment
        json_data = json.dumps(data)
        r = self.upd_req(upd_url, self.username, self.password, json_data )



    def remove_worklog(self, issue_key, worklog_id):
        logging.debug('Start deleting worklog')
        del_url = self.jira + '/rest/api/2/issue/' + issue_key + '/worklog/' + worklog_id
        print del_url
        r = self.del_req(del_url, self.username, self.password )
        logging.debug('Worklog has been deleted.')

    def print_days_work(self, day):
        pass

    def sync_table(self, issue_key=None):
        pass

    def __convert_to_timedelta(self, time_val):
        """
        Given a *time_val* (string) such as '5d', returns a timedelta object
        representing the given value (e.g. timedelta(days=5)).  Accepts the
        following '<num><char>' formats:

        =========   ======= ===================
        Character   Meaning Example
        =========   ======= ===================
        s           Seconds '60s' -> 60 Seconds
        m           Minutes '5m'  -> 5 Minutes
        h           Hours   '24h' -> 24 Hours
        d           Days    '7d'  -> 7 Days
        =========   ======= ===================

        Examples::

        >>> convert_to_timedelta('7d')
        datetime.timedelta(7)
        >>> convert_to_timedelta('24h')
        datetime.timedelta(1)
        >>> convert_to_timedelta('60m')
        datetime.timedelta(0, 3600)
        >>> convert_to_timedelta('120s')
        datetime.timedelta(0, 120)
        """
        timedelta = datetime.timedelta
        num = int(time_val[:-1])
        if time_val.endswith('s'):
            return timedelta(seconds=num)
        elif time_val.endswith('m'):
            return timedelta(minutes=num)
        elif time_val.endswith('h'):
            return timedelta(hours=num)
        elif time_val.endswith('d'):
            return timedelta(days=num)
    def __int_round(self, x, base=5):
        logging.debug('Round %s' % str(x))
        return int(base * round(float(x)/base))


def main():
    pass


if __name__ == '__main__':
    main()
