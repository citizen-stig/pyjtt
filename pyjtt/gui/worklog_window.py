# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'worklog_window.ui'
#
# Created: Sun Feb 24 13:29:56 2013
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
        WorklogWindow.resize(331, 260)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WorklogWindow.sizePolicy().hasHeightForWidth())
        WorklogWindow.setSizePolicy(sizePolicy)
        WorklogWindow.setMinimumSize(QtCore.QSize(320, 260))
        WorklogWindow.setMaximumSize(QtCore.QSize(600, 800))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/set1/icons/set1/clock.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WorklogWindow.setWindowIcon(icon)
        WorklogWindow.setWhatsThis(_fromUtf8(""))
        self.gridLayout = QtGui.QGridLayout(WorklogWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelIssue = QtGui.QLabel(WorklogWindow)
        self.labelIssue.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelIssue.setObjectName(_fromUtf8("labelIssue"))
        self.verticalLayout.addWidget(self.labelIssue)
        self.line = QtGui.QFrame(WorklogWindow)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_2.setContentsMargins(3, -1, -1, -1)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.labelDate = QtGui.QLabel(WorklogWindow)
        self.labelDate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelDate.setObjectName(_fromUtf8("labelDate"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelDate)
        self.dateEdit = QtGui.QDateEdit(WorklogWindow)
        self.dateEdit.setWrapping(False)
        self.dateEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.dateEdit.setReadOnly(False)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName(_fromUtf8("dateEdit"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.dateEdit)
        self.horizontalLayout.addLayout(self.formLayout_2)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.formLayout.setContentsMargins(-1, -1, 3, -1)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(6)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.labelStart = QtGui.QLabel(WorklogWindow)
        self.labelStart.setObjectName(_fromUtf8("labelStart"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelStart)
        self.timeStartEdit = QtGui.QTimeEdit(WorklogWindow)
        self.timeStartEdit.setWrapping(True)
        self.timeStartEdit.setCalendarPopup(False)
        self.timeStartEdit.setObjectName(_fromUtf8("timeStartEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.timeStartEdit)
        self.labelEnd = QtGui.QLabel(WorklogWindow)
        self.labelEnd.setObjectName(_fromUtf8("labelEnd"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelEnd)
        self.timeEndEdit = QtGui.QTimeEdit(WorklogWindow)
        self.timeEndEdit.setEnabled(True)
        self.timeEndEdit.setWrapping(True)
        self.timeEndEdit.setObjectName(_fromUtf8("timeEndEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.timeEndEdit)
        self.horizontalLayout.addLayout(self.formLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.labelComment = QtGui.QLabel(WorklogWindow)
        self.labelComment.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelComment.setObjectName(_fromUtf8("labelComment"))
        self.verticalLayout_3.addWidget(self.labelComment)
        self.plainTextCommentEdit = QtGui.QPlainTextEdit(WorklogWindow)
        self.plainTextCommentEdit.setObjectName(_fromUtf8("plainTextCommentEdit"))
        self.verticalLayout_3.addWidget(self.plainTextCommentEdit)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 0, 1, 1)
        self.labelSpent = QtGui.QLabel(WorklogWindow)
        self.labelSpent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelSpent.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelSpent.setObjectName(_fromUtf8("labelSpent"))
        self.gridLayout.addWidget(self.labelSpent, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(WorklogWindow)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.retranslateUi(WorklogWindow)
        QtCore.QMetaObject.connectSlotsByName(WorklogWindow)

    def retranslateUi(self, WorklogWindow):
        WorklogWindow.setWindowTitle(_translate("WorklogWindow", "Some Worklog", None))
        self.labelIssue.setText(_translate("WorklogWindow", "ISSUE: SUMMARY", None))
        self.labelDate.setText(_translate("WorklogWindow", "Date:", None))
        self.dateEdit.setDisplayFormat(_translate("WorklogWindow", "MM/dd/yyyy", None))
        self.labelStart.setText(_translate("WorklogWindow", "Start time", None))
        self.timeStartEdit.setDisplayFormat(_translate("WorklogWindow", "hh:mm", None))
        self.labelEnd.setText(_translate("WorklogWindow", "End time", None))
        self.timeEndEdit.setDisplayFormat(_translate("WorklogWindow", "hh:mm", None))
        self.labelComment.setText(_translate("WorklogWindow", "Comment:", None))
        self.labelSpent.setText(_translate("WorklogWindow", "Time Spent :", None))

import pyjtt_icons_rc
