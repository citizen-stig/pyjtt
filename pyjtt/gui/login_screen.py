# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_screen.ui'
#
# Created: Mon Jan 28 09:59:34 2013
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

class Ui_loginWindow(object):
    def setupUi(self, loginWindow):
        loginWindow.setObjectName(_fromUtf8("loginWindow"))
        loginWindow.resize(320, 160)
        loginWindow.setMinimumSize(QtCore.QSize(320, 160))
        loginWindow.setMaximumSize(QtCore.QSize(320, 160))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/clock_apple.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        loginWindow.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(loginWindow)
        self.buttonBox.setGeometry(QtCore.QRect(140, 130, 166, 21))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.labelHostAddress = QtGui.QLabel(loginWindow)
        self.labelHostAddress.setGeometry(QtCore.QRect(10, 10, 121, 21))
        self.labelHostAddress.setObjectName(_fromUtf8("labelHostAddress"))
        self.lineEditHostAddress = QtGui.QLineEdit(loginWindow)
        self.lineEditHostAddress.setGeometry(QtCore.QRect(140, 10, 171, 20))
        self.lineEditHostAddress.setInputMask(_fromUtf8(""))
        self.lineEditHostAddress.setObjectName(_fromUtf8("lineEditHostAddress"))
        self.labelLogin = QtGui.QLabel(loginWindow)
        self.labelLogin.setGeometry(QtCore.QRect(10, 50, 121, 21))
        self.labelLogin.setObjectName(_fromUtf8("labelLogin"))
        self.lineEditLogin = QtGui.QLineEdit(loginWindow)
        self.lineEditLogin.setGeometry(QtCore.QRect(140, 50, 171, 20))
        self.lineEditLogin.setObjectName(_fromUtf8("lineEditLogin"))
        self.lineEditPassword = QtGui.QLineEdit(loginWindow)
        self.lineEditPassword.setGeometry(QtCore.QRect(140, 80, 171, 20))
        self.lineEditPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassword.setObjectName(_fromUtf8("lineEditPassword"))
        self.labelPassowrd = QtGui.QLabel(loginWindow)
        self.labelPassowrd.setGeometry(QtCore.QRect(10, 80, 121, 21))
        self.labelPassowrd.setObjectName(_fromUtf8("labelPassowrd"))
        self.line = QtGui.QFrame(loginWindow)
        self.line.setGeometry(QtCore.QRect(10, 30, 301, 21))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.checkBoxSaveCredentials = QtGui.QCheckBox(loginWindow)
        self.checkBoxSaveCredentials.setGeometry(QtCore.QRect(10, 110, 121, 18))
        self.checkBoxSaveCredentials.setObjectName(_fromUtf8("checkBoxSaveCredentials"))

        self.retranslateUi(loginWindow)
        QtCore.QMetaObject.connectSlotsByName(loginWindow)

    def retranslateUi(self, loginWindow):
        loginWindow.setWindowTitle(_translate("loginWindow", "Login", None))
        self.labelHostAddress.setText(_translate("loginWindow", "Jira Host Address", None))
        self.lineEditHostAddress.setPlaceholderText(_translate("loginWindow", "https://jira.example.com/", None))
        self.labelLogin.setText(_translate("loginWindow", "Login", None))
        self.labelPassowrd.setText(_translate("loginWindow", "Password", None))
        self.checkBoxSaveCredentials.setText(_translate("loginWindow", "Save Credentials", None))

import pyjtt_rc
