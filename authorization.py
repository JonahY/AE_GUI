# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'authorization.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(483, 310)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("#license_file {border-style:outset;border-width:2px;border-color: rgb(48, 0, 72);color: rgb(48, 0, 72);font: 10pt \"Verdana\";;}\n"
"#mac {background-color: transparent;border:none;border-style:outset;color: rgb(48, 0, 72);font: 75 10pt \"Verdana\";}\n"
"#activate_status {background-color: transparent;border:none;border-style:outset;color: rgb(255, 0, 0);font: 75 10pt \"Verdana\";}\n"
"#information {background-color: transparent;border:none;border-style:outset;color: rgb(48, 0, 72);font: 75 10pt \"Verdana\";}")
        Dialog.setSizeGripEnabled(False)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 40, 461, 101))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 241, 20))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.mac = QtWidgets.QLineEdit(self.layoutWidget)
        self.mac.setReadOnly(True)
        self.mac.setObjectName("mac")
        self.horizontalLayout.addWidget(self.mac)
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 50, 441, 41))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.activate_status = QtWidgets.QTextEdit(self.layoutWidget1)
        self.activate_status.setReadOnly(True)
        self.activate_status.setObjectName("activate_status")
        self.gridLayout.addWidget(self.activate_status, 0, 1, 2, 1)
        self.abort = QtWidgets.QPushButton(Dialog)
        self.abort.setGeometry(QtCore.QRect(300, 280, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.abort.setFont(font)
        self.abort.setObjectName("abort")
        self.enter = QtWidgets.QPushButton(Dialog)
        self.enter.setEnabled(False)
        self.enter.setGeometry(QtCore.QRect(390, 280, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.enter.setFont(font)
        self.enter.setObjectName("enter")
        self.about = QtWidgets.QGroupBox(Dialog)
        self.about.setGeometry(QtCore.QRect(10, 150, 461, 121))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.about.setFont(font)
        self.about.setObjectName("about")
        self.information = QtWidgets.QTextEdit(self.about)
        self.information.setGeometry(QtCore.QRect(10, 21, 441, 91))
        self.information.setReadOnly(True)
        self.information.setObjectName("information")
        self.label_4 = QtWidgets.QLabel(self.about)
        self.label_4.setGeometry(QtCore.QRect(380, 20, 40, 50))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/MSE.gif"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.about)
        self.label_5.setGeometry(QtCore.QRect(325, 20, 54, 50))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/XJTU.gif"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.layoutWidget2 = QtWidgets.QWidget(Dialog)
        self.layoutWidget2.setGeometry(QtCore.QRect(20, 10, 451, 25))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.license_file = QtWidgets.QLineEdit(self.layoutWidget2)
        self.license_file.setObjectName("license_file")
        self.horizontalLayout_2.addWidget(self.license_file)
        self.show_license = QtWidgets.QToolButton(self.layoutWidget2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.show_license.setFont(font)
        self.show_license.setObjectName("show_license")
        self.horizontalLayout_2.addWidget(self.show_license)
        self.activate = QtWidgets.QPushButton(self.layoutWidget2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activate.setFont(font)
        self.activate.setObjectName("activate")
        self.horizontalLayout_2.addWidget(self.activate)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Activation"))
        self.groupBox.setTitle(_translate("Dialog", "Activation information"))
        self.label_2.setText(_translate("Dialog", "MAC address:"))
        self.label_3.setText(_translate("Dialog", "Status:"))
        self.abort.setText(_translate("Dialog", "Abort"))
        self.enter.setText(_translate("Dialog", "Continue"))
        self.about.setTitle(_translate("Dialog", "About"))
        self.information.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Verdana\'; font-size:10pt; font-weight:72; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label.setText(_translate("Dialog", "License file"))
        self.license_file.setPlaceholderText(_translate("Dialog", "license.lic"))
        self.show_license.setText(_translate("Dialog", "..."))
        self.activate.setText(_translate("Dialog", "Activate"))
