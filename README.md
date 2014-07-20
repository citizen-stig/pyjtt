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
Download PyJTT distribution and start it.
Entrer address of JIRA instance. 
Enter login and password. Notice(!): login and password are stored in plain text, so be careful with "Saving credentials" option.
PyJTT will get some issues from JIRA at start, but if you want to add worklog to issue, that is not presented in list, enter key of this issue in edit field on issues tab and click find it. Issue should appears in list of issues.
Select issue. Double click open dialog window for adding new worklog. 
Start tracking button will start timer for "online" tracking. 
Existed worklogs can be edited on Worklogs tab.
