# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_screen.ui'
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

class Ui_loginWindow(object):
    def setupUi(self, loginWindow):
        loginWindow.setObjectName(_fromUtf8("loginWindow"))
        loginWindow.resize(340, 200)
        loginWindow.setMinimumSize(QtCore.QSize(340, 200))
        loginWindow.setMaximumSize(QtCore.QSize(340, 200))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/icons/clock.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        loginWindow.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(loginWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.labelHostAddress = QtGui.QLabel(loginWindow)
        self.labelHostAddress.setObjectName(_fromUtf8("labelHostAddress"))
        self.gridLayout.addWidget(self.labelHostAddress, 0, 0, 1, 1)
        self.lineEditHostAddress = QtGui.QLineEdit(loginWindow)
        self.lineEditHostAddress.setInputMask(_fromUtf8(""))
        self.lineEditHostAddress.setObjectName(_fromUtf8("lineEditHostAddress"))
        self.gridLayout.addWidget(self.lineEditHostAddress, 0, 1, 1, 1)
        self.line = QtGui.QFrame(loginWindow)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.labelLogin = QtGui.QLabel(loginWindow)
        self.labelLogin.setObjectName(_fromUtf8("labelLogin"))
        self.gridLayout.addWidget(self.labelLogin, 2, 0, 1, 1)
        self.lineEditLogin = QtGui.QLineEdit(loginWindow)
        self.lineEditLogin.setObjectName(_fromUtf8("lineEditLogin"))
        self.gridLayout.addWidget(self.lineEditLogin, 2, 1, 1, 1)
        self.labelPassowrd = QtGui.QLabel(loginWindow)
        self.labelPassowrd.setObjectName(_fromUtf8("labelPassowrd"))
        self.gridLayout.addWidget(self.labelPassowrd, 3, 0, 1, 1)
        self.lineEditPassword = QtGui.QLineEdit(loginWindow)
        self.lineEditPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassword.setObjectName(_fromUtf8("lineEditPassword"))
        self.gridLayout.addWidget(self.lineEditPassword, 3, 1, 1, 1)
        self.checkBoxSaveCredentials = QtGui.QCheckBox(loginWindow)
        self.checkBoxSaveCredentials.setObjectName(_fromUtf8("checkBoxSaveCredentials"))
        self.gridLayout.addWidget(self.checkBoxSaveCredentials, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(loginWindow)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)

        self.retranslateUi(loginWindow)
        QtCore.QMetaObject.connectSlotsByName(loginWindow)

    def retranslateUi(self, loginWindow):
        loginWindow.setWindowTitle(_translate("loginWindow", "Login", None))
        self.labelHostAddress.setText(_translate("loginWindow", "Jira Host Address", None))
        self.lineEditHostAddress.setPlaceholderText(_translate("loginWindow", "https://jira.example.com/", None))
        self.labelLogin.setText(_translate("loginWindow", "Login", None))
        self.labelPassowrd.setText(_translate("loginWindow", "Password", None))
        self.checkBoxSaveCredentials.setToolTip(_translate("loginWindow", "Credentials will be saved in plain text!", None))
        self.checkBoxSaveCredentials.setText(_translate("loginWindow", "Save Credentials", None))

import pyjtt_res_rc
