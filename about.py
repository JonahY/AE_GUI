# -*- coding: utf-8 -*-
"""
@version: 2.0
@author: Jonah
@file: __init__.py
@time: 2021/11/10 12:56
"""
# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import resource


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(483, 120)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("#information {background-color: transparent;border:none;border-style:outset;color: rgb(48, 0, 72);font: 75 10pt \"Verdana\";}")
        self.about = QtWidgets.QGroupBox(Dialog)
        self.about.setGeometry(QtCore.QRect(10, 1, 461, 111))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.about.setFont(font)
        self.about.setObjectName("about")
        self.information = QtWidgets.QTextEdit(self.about)
        self.information.setGeometry(QtCore.QRect(10, 20, 441, 91))
        self.information.setReadOnly(True)
        self.information.setObjectName("information")
        self.label = QtWidgets.QLabel(self.about)
        self.label.setGeometry(QtCore.QRect(325, 20, 54, 50))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/XJTU.gif"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.about)
        self.label_2.setGeometry(QtCore.QRect(380, 20, 40, 50))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/MSE.gif"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About information"))
        self.about.setTitle(_translate("Dialog", "About"))
        self.information.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Verdana\'; font-size:10pt; font-weight:72; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
