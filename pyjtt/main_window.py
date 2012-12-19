# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created: Wed Dec 19 08:56:51 2012
#      by: PyQt4 UI code generator 4.9.6
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
        MainWindow.resize(640, 489)
        MainWindow.setMinimumSize(QtCore.QSize(640, 480))
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
        self.gridLayout_4 = QtGui.QGridLayout(self.tabIssues)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.lineIssueKey = QtGui.QLineEdit(self.tabIssues)
        self.lineIssueKey.setText(_fromUtf8(""))
        self.lineIssueKey.setObjectName(_fromUtf8("lineIssueKey"))
        self.gridLayout_4.addWidget(self.lineIssueKey, 0, 0, 1, 1)
        self.AddIssue = QtGui.QPushButton(self.tabIssues)
        self.AddIssue.setFlat(False)
        self.AddIssue.setObjectName(_fromUtf8("AddIssue"))
        self.gridLayout_4.addWidget(self.AddIssue, 0, 1, 1, 1)
        self.tableIssues = QtGui.QTableWidget(self.tabIssues)
        self.tableIssues.setObjectName(_fromUtf8("tableIssues"))
        self.tableIssues.setColumnCount(3)
        self.tableIssues.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableIssues.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableIssues.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableIssues.setHorizontalHeaderItem(2, item)
        self.gridLayout_4.addWidget(self.tableIssues, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabIssues, _fromUtf8(""))
        self.tabWorklogs = QtGui.QWidget()
        self.tabWorklogs.setObjectName(_fromUtf8("tabWorklogs"))
        self.tabWidget.addTab(self.tabWorklogs, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.startStopTracking = QtGui.QCommandLinkButton(self.centralwidget)
        self.startStopTracking.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startStopTracking.sizePolicy().hasHeightForWidth())
        self.startStopTracking.setSizePolicy(sizePolicy)
        self.startStopTracking.setCheckable(True)
        self.startStopTracking.setObjectName(_fromUtf8("startStopTracking"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.startStopTracking)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lableSelectIssue = QtGui.QLabel(self.centralwidget)
        self.lableSelectIssue.setObjectName(_fromUtf8("lableSelectIssue"))
        self.verticalLayout.addWidget(self.lableSelectIssue)
        self.labelTimeSpent = QtGui.QLabel(self.centralwidget)
        self.labelTimeSpent.setObjectName(_fromUtf8("labelTimeSpent"))
        self.verticalLayout.addWidget(self.labelTimeSpent)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.verticalLayout)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Jira Time Tracker", None))
        self.lineIssueKey.setPlaceholderText(_translate("MainWindow", "Enter issue key...", None))
        self.AddIssue.setText(_translate("MainWindow", "Add", None))
        item = self.tableIssues.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Key", None))
        item = self.tableIssues.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Summary", None))
        item = self.tableIssues.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Action", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabIssues), _translate("MainWindow", "Issues", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWorklogs), _translate("MainWindow", "Worklogs", None))
        self.startStopTracking.setText(_translate("MainWindow", "Start Tracking", None))
        self.lableSelectIssue.setText(_translate("MainWindow", "No issue selected", None))
        self.labelTimeSpent.setText(_translate("MainWindow", "00:00:00", None))

