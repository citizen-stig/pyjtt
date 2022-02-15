## Description

PyJTT (Python Jira Time Tracker) is a desktop applicatoin for tracking time to issues in Atlassian Jira. It uses Qt framework and python.

## Features
* Working with JIRA work logs (add, edit, remove). Ease of working with daily work log
* "Online" tracking - track time of issue, that you're currently working on
* Ability to refresh worklog, if it was changed in JIRA Web interface

## Requirements
* JIRA version > 5
* Enabled REST API in JIRA
* Windows, MacOS or GNU/Linux

## How to start
- Download PyJTT distribution and start it.
- Enter address of JIRA instance. 
- Enter your login and password. 
Notice(!): login and password are stored in plain text, so be careful with "Saving credentials" option.
PyJTT will get issues with accordance to filter from JIRA at start, but if you want to add worklog to issue, that is not presented in list, enter key of this issue in edit field on issues tab and click find it. Issue should appears in list of issues.
- Select issue. Double click open dialog window for adding new worklog. 
- Start tracking button will start timer for "online" tracking. 
- Existed worklogs can be edited on Worklogs tab.

##Troubleshooting
1) Certificate package
https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
2) Building as an .app with icon
https://github.com/pyinstaller/pyinstaller/issues/5154
