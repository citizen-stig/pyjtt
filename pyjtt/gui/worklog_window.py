# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'worklog_window.ui'
#
# Created: Mon Jan 28 09:59:40 2013
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

class Ui_WorklogWindow(object):
    def setupUi(self, WorklogWindow):
        WorklogWindow.setObjectName(_fromUtf8("WorklogWindow"))
        WorklogWindow.resize(320, 264)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WorklogWindow.sizePolicy().hasHeightForWidth())
        WorklogWindow.setSizePolicy(sizePolicy)
        WorklogWindow.setMinimumSize(QtCore.QSize(320, 264))
        WorklogWindow.setMaximumSize(QtCore.QSize(320, 264))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/clock_apple.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WorklogWindow.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(WorklogWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.labelIssue = QtGui.QLabel(WorklogWindow)
        self.labelIssue.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelIssue.setObjectName(_fromUtf8("labelIssue"))
        self.gridLayout.addWidget(self.labelIssue, 0, 0, 1, 2)
        self.line_2 = QtGui.QFrame(WorklogWindow)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 2)
        self.line = QtGui.QFrame(WorklogWindow)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(WorklogWindow)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelStart = QtGui.QLabel(WorklogWindow)
        self.labelStart.setObjectName(_fromUtf8("labelStart"))
        self.horizontalLayout.addWidget(self.labelStart)
        self.timeStartEdit = QtGui.QTimeEdit(WorklogWindow)
        self.timeStartEdit.setObjectName(_fromUtf8("timeStartEdit"))
        self.horizontalLayout.addWidget(self.timeStartEdit)
        self.labelEnd = QtGui.QLabel(WorklogWindow)
        self.labelEnd.setObjectName(_fromUtf8("labelEnd"))
        self.horizontalLayout.addWidget(self.labelEnd)
        self.timeEndEdit = QtGui.QTimeEdit(WorklogWindow)
        self.timeEndEdit.setEnabled(True)
        self.timeEndEdit.setObjectName(_fromUtf8("timeEndEdit"))
        self.horizontalLayout.addWidget(self.timeEndEdit)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.labelComment = QtGui.QLabel(WorklogWindow)
        self.labelComment.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelComment.setObjectName(_fromUtf8("labelComment"))
        self.verticalLayout_3.addWidget(self.labelComment)
        self.plainTextCommentEdit = QtGui.QPlainTextEdit(WorklogWindow)
        self.plainTextCommentEdit.setObjectName(_fromUtf8("plainTextCommentEdit"))
        self.verticalLayout_3.addWidget(self.plainTextCommentEdit)
        self.gridLayout.addLayout(self.verticalLayout_3, 5, 0, 1, 2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.labelDate = QtGui.QLabel(WorklogWindow)
        self.labelDate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelDate.setObjectName(_fromUtf8("labelDate"))
        self.horizontalLayout_2.addWidget(self.labelDate)
        self.dateEdit = QtGui.QDateEdit(WorklogWindow)
        self.dateEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.dateEdit.setReadOnly(False)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.horizontalLayout_2.addWidget(self.dateEdit)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.labelSpent = QtGui.QLabel(WorklogWindow)
        self.labelSpent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelSpent.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelSpent.setObjectName(_fromUtf8("labelSpent"))
        self.gridLayout.addWidget(self.labelSpent, 6, 1, 1, 1)

        self.retranslateUi(WorklogWindow)
        QtCore.QMetaObject.connectSlotsByName(WorklogWindow)

    def retranslateUi(self, WorklogWindow):
        WorklogWindow.setWindowTitle(_translate("WorklogWindow", "Some Worklog", None))
        self.labelIssue.setText(_translate("WorklogWindow", "ISSUE: SUMMARY", None))
        self.labelStart.setText(_translate("WorklogWindow", "Start time", None))
        self.timeStartEdit.setDisplayFormat(_translate("WorklogWindow", "hh:mm", None))
        self.labelEnd.setText(_translate("WorklogWindow", "End time", None))
        self.timeEndEdit.setDisplayFormat(_translate("WorklogWindow", "hh:mm", None))
        self.labelComment.setText(_translate("WorklogWindow", "Comment:", None))
        self.labelDate.setText(_translate("WorklogWindow", "Date:", None))
        self.dateEdit.setDisplayFormat(_translate("WorklogWindow", "MM/dd/yyyy", None))
        self.labelSpent.setText(_translate("WorklogWindow", "Time Spent :", None))

import pyjtt_rc
