# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created: Thu Jun  6 09:12:20 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(640, 480)
        MainWindow.setMinimumSize(QtCore.QSize(640, 480))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/icons/clock.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(False)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabIssues = QtGui.QWidget()
        self.tabIssues.setObjectName(_fromUtf8("tabIssues"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabIssues)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lineIssueKey = QtGui.QLineEdit(self.tabIssues)
        self.lineIssueKey.setText(_fromUtf8(""))
        self.lineIssueKey.setObjectName(_fromUtf8("lineIssueKey"))
        self.gridLayout_3.addWidget(self.lineIssueKey, 0, 0, 1, 1)
        self.FindIssue = QtGui.QPushButton(self.tabIssues)
        self.FindIssue.setFlat(False)
        self.FindIssue.setObjectName(_fromUtf8("FindIssue"))
        self.gridLayout_3.addWidget(self.FindIssue, 0, 1, 1, 1)
        self.tableIssues = QtGui.QTableWidget(self.tabIssues)
        self.tableIssues.setFrameShape(QtGui.QFrame.StyledPanel)
        self.tableIssues.setFrameShadow(QtGui.QFrame.Plain)
        self.tableIssues.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableIssues.setAlternatingRowColors(True)
        self.tableIssues.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableIssues.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableIssues.setWordWrap(True)
        self.tableIssues.setObjectName(_fromUtf8("tableIssues"))
        self.tableIssues.setColumnCount(2)
        self.tableIssues.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableIssues.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableIssues.setHorizontalHeaderItem(1, item)
        self.tableIssues.horizontalHeader().setDefaultSectionSize(100)
        self.tableIssues.horizontalHeader().setMinimumSectionSize(30)
        self.tableIssues.verticalHeader().setVisible(False)
        self.tableIssues.verticalHeader().setDefaultSectionSize(22)
        self.tableIssues.verticalHeader().setMinimumSectionSize(17)
        self.tableIssues.verticalHeader().setStretchLastSection(False)
        self.gridLayout_3.addWidget(self.tableIssues, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabIssues, _fromUtf8(""))
        self.tabWorklogs = QtGui.QWidget()
        self.tabWorklogs.setObjectName(_fromUtf8("tabWorklogs"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabWorklogs)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.dateDayWorklogEdit = QtGui.QDateEdit(self.tabWorklogs)
        self.dateDayWorklogEdit.setCalendarPopup(True)
        self.dateDayWorklogEdit.setDate(QtCore.QDate(2001, 1, 1))
        self.dateDayWorklogEdit.setObjectName(_fromUtf8("dateDayWorklogEdit"))
        self.gridLayout_2.addWidget(self.dateDayWorklogEdit, 0, 0, 1, 1)
        self.editWorklog = QtGui.QPushButton(self.tabWorklogs)
        self.editWorklog.setObjectName(_fromUtf8("editWorklog"))
        self.gridLayout_2.addWidget(self.editWorklog, 0, 1, 1, 1)
        self.removeWorklog = QtGui.QPushButton(self.tabWorklogs)
        self.removeWorklog.setObjectName(_fromUtf8("removeWorklog"))
        self.gridLayout_2.addWidget(self.removeWorklog, 0, 2, 1, 1)
        self.tableDayWorklog = QtGui.QTableWidget(self.tabWorklogs)
        self.tableDayWorklog.setFrameShape(QtGui.QFrame.StyledPanel)
        self.tableDayWorklog.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableDayWorklog.setAlternatingRowColors(True)
        self.tableDayWorklog.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableDayWorklog.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableDayWorklog.setObjectName(_fromUtf8("tableDayWorklog"))
        self.tableDayWorklog.setColumnCount(6)
        self.tableDayWorklog.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableDayWorklog.setHorizontalHeaderItem(5, item)
        self.tableDayWorklog.verticalHeader().setVisible(False)
        self.tableDayWorklog.verticalHeader().setDefaultSectionSize(22)
        self.gridLayout_2.addWidget(self.tableDayWorklog, 1, 0, 1, 3)
        self.labelDaySummary = QtGui.QLabel(self.tabWorklogs)
        self.labelDaySummary.setText(_fromUtf8(""))
        self.labelDaySummary.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelDaySummary.setObjectName(_fromUtf8("labelDaySummary"))
        self.gridLayout_2.addWidget(self.labelDaySummary, 2, 0, 1, 3)
        self.tabWidget.addTab(self.tabWorklogs, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.widgetOnlineTracking = QtGui.QWidget(self.centralwidget)
        self.widgetOnlineTracking.setObjectName(_fromUtf8("widgetOnlineTracking"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widgetOnlineTracking)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(1, -1, -1, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelSelectedIssue = QtGui.QLabel(self.widgetOnlineTracking)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelSelectedIssue.sizePolicy().hasHeightForWidth())
        self.labelSelectedIssue.setSizePolicy(sizePolicy)
        self.labelSelectedIssue.setAcceptDrops(False)
        self.labelSelectedIssue.setScaledContents(False)
        self.labelSelectedIssue.setMargin(0)
        self.labelSelectedIssue.setIndent(-1)
        self.labelSelectedIssue.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.labelSelectedIssue.setObjectName(_fromUtf8("labelSelectedIssue"))
        self.verticalLayout.addWidget(self.labelSelectedIssue)
        self.labelTimeSpent = QtGui.QLabel(self.widgetOnlineTracking)
        self.labelTimeSpent.setObjectName(_fromUtf8("labelTimeSpent"))
        self.verticalLayout.addWidget(self.labelTimeSpent)
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.widgetOnlineTracking)
        self.startStopTracking = QtGui.QPushButton(self.centralwidget)
        self.startStopTracking.setMinimumSize(QtCore.QSize(131, 41))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/icons/start.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.startStopTracking.setIcon(icon1)
        self.startStopTracking.setIconSize(QtCore.QSize(32, 32))
        self.startStopTracking.setCheckable(True)
        self.startStopTracking.setObjectName(_fromUtf8("startStopTracking"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.startStopTracking)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionReresh_issue = QtGui.QAction(MainWindow)
        self.actionReresh_issue.setObjectName(_fromUtf8("actionReresh_issue"))
        self.actionFull_refresh = QtGui.QAction(MainWindow)
        self.actionFull_refresh.setObjectName(_fromUtf8("actionFull_refresh"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionRefresh = QtGui.QAction(MainWindow)
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuFile.addAction(self.actionReresh_issue)
        self.menuFile.addAction(self.actionFull_refresh)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.lineIssueKey, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.FindIssue.click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tabWidget, self.dateDayWorklogEdit)
        MainWindow.setTabOrder(self.dateDayWorklogEdit, self.tableDayWorklog)
        MainWindow.setTabOrder(self.tableDayWorklog, self.editWorklog)
        MainWindow.setTabOrder(self.editWorklog, self.removeWorklog)
        MainWindow.setTabOrder(self.removeWorklog, self.lineIssueKey)
        MainWindow.setTabOrder(self.lineIssueKey, self.FindIssue)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Jira Time Tracker", None))
        self.lineIssueKey.setPlaceholderText(_translate("MainWindow", "Enter issue key...", None))
        self.FindIssue.setText(_translate("MainWindow", "Add", None))
        self.tableIssues.setSortingEnabled(True)
        item = self.tableIssues.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Key", None))
        item = self.tableIssues.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Summary", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabIssues), _translate("MainWindow", "Issues", None))
        self.editWorklog.setText(_translate("MainWindow", "Edit", None))
        self.removeWorklog.setText(_translate("MainWindow", "Remove", None))
        self.tableDayWorklog.setSortingEnabled(True)
        item = self.tableDayWorklog.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Key", None))
        item = self.tableDayWorklog.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Summary", None))
        item = self.tableDayWorklog.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Start Time", None))
        item = self.tableDayWorklog.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "End Time", None))
        item = self.tableDayWorklog.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Time Spent", None))
        item = self.tableDayWorklog.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "worklog_id", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWorklogs), _translate("MainWindow", "Worklogs", None))
        self.labelSelectedIssue.setText(_translate("MainWindow", "No issue selected", None))
        self.labelTimeSpent.setText(_translate("MainWindow", "00:00:00", None))
        self.startStopTracking.setText(_translate("MainWindow", "Start Tracking", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionReresh_issue.setText(_translate("MainWindow", "Reresh issue", None))
        self.actionFull_refresh.setText(_translate("MainWindow", "Full refresh", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionRefresh.setText(_translate("MainWindow", "refresh!", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))

import pyjtt_res_rc
