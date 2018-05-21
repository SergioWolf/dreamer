# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_password.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(363, 161)
        self.lineEditLogin = QtWidgets.QLineEdit(Dialog)
        self.lineEditLogin.setGeometry(QtCore.QRect(110, 30, 221, 20))
        self.lineEditLogin.setObjectName("lineEditLogin")
        self.lineEditPassword = QtWidgets.QLineEdit(Dialog)
        self.lineEditPassword.setGeometry(QtCore.QRect(110, 60, 221, 20))
        self.lineEditPassword.setObjectName("lineEditPassword")
        self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(60, 30, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 60, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pushButtonOk = QtWidgets.QPushButton(Dialog)
        self.pushButtonOk.setGeometry(QtCore.QRect(140, 110, 75, 23))
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.pushButtonCancel = QtWidgets.QPushButton(Dialog)
        self.pushButtonCancel.setGeometry(QtCore.QRect(240, 110, 75, 23))
        self.pushButtonCancel.setObjectName("pushButtonCancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Login"))
        self.label_2.setText(_translate("Dialog", "Password"))
        self.pushButtonOk.setText(_translate("Dialog", "OK"))
        self.pushButtonCancel.setText(_translate("Dialog", "Cancel"))

