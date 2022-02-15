# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_screen.ui'
#
# Created: Fri Jun 13 14:59:45 2014
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

import os
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Ui_loginWindow(object):
    def setupUi(self, loginWindow):
        loginWindow.setObjectName("loginWindow")
        loginWindow.resize(480, 200)
        loginWindow.setMinimumSize(QtCore.QSize(480, 200))
        loginWindow.setMaximumSize(QtCore.QSize(640, 200))
        loginWindow.setSizeIncrement(QtCore.QSize(10, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path('resources/icons/icon.png')))
        loginWindow.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(loginWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.labelHostAddress = QtWidgets.QLabel(loginWindow)
        self.labelHostAddress.setObjectName("labelHostAddress")
        self.gridLayout.addWidget(self.labelHostAddress, 0, 0, 1, 1)
        self.lineEditHostAddress = QtWidgets.QLineEdit(loginWindow)
#        self.lineEditHostAddress.setInputMethodHints(QtCore.Qt.ImhNone)
#        self.lineEditHostAddress.setInputMethodHints()
        self.lineEditHostAddress.setObjectName("lineEditHostAddress")
        self.gridLayout.addWidget(self.lineEditHostAddress, 0, 1, 1, 1)
        self.line = QtWidgets.QFrame(loginWindow)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.labelLogin = QtWidgets.QLabel(loginWindow)
        self.labelLogin.setObjectName("labelLogin")
        self.gridLayout.addWidget(self.labelLogin, 2, 0, 1, 1)
        self.lineEditLogin = QtWidgets.QLineEdit(loginWindow)
        self.lineEditLogin.setObjectName("lineEditLogin")
        self.gridLayout.addWidget(self.lineEditLogin, 2, 1, 1, 1)
        self.labelPassowrd = QtWidgets.QLabel(loginWindow)
        self.labelPassowrd.setObjectName("labelPassowrd")
        self.gridLayout.addWidget(self.labelPassowrd, 3, 0, 1, 1)
        self.lineEditPassword = QtWidgets.QLineEdit(loginWindow)
        self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEditPassword.setObjectName("lineEditPassword")
        self.gridLayout.addWidget(self.lineEditPassword, 3, 1, 1, 1)
        self.checkBoxSaveCredentials = QtWidgets.QCheckBox(loginWindow)
        self.checkBoxSaveCredentials.setObjectName("checkBoxSaveCredentials")
        self.gridLayout.addWidget(self.checkBoxSaveCredentials, 4, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(loginWindow)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)

        self.retranslateUi(loginWindow)
        QtCore.QMetaObject.connectSlotsByName(loginWindow)

    def retranslateUi(self, loginWindow):
        _translate = QtCore.QCoreApplication.translate
        loginWindow.setWindowTitle(_translate("loginWindow", "Login"))
        self.labelHostAddress.setText(_translate("loginWindow", "Jira Host Address"))
        self.lineEditHostAddress.setPlaceholderText(_translate("loginWindow", "https://jira.example.com/"))
        self.labelLogin.setText(_translate("loginWindow", "Login"))
        self.labelPassowrd.setText(_translate("loginWindow", "Password"))
        self.checkBoxSaveCredentials.setToolTip(_translate("loginWindow", "Credentials will be saved in plain text!"))
        self.checkBoxSaveCredentials.setText(_translate("loginWindow", "Save Password"))

