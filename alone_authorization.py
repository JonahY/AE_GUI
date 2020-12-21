# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alone_authorization.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(483, 180)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("#license_file {border-style:outset;border-width:2px;border-color: rgb(48, 0, 72);color: rgb(48, 0, 72);font: 10pt \"Verdana\";;}\n"
"#mac {background-color: transparent;border:none;border-style:outset;color: rgb(48, 0, 72);font: 75 10pt \"Verdana\";}\n"
"#activate_status {background-color: transparent;border:none;border-style:outset;color: rgb(255, 0, 0);font: 75 10pt \"Verdana\";}")
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
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 241, 27))
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
        self.layoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 50, 441, 51))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.activate_status = QtWidgets.QTextEdit(self.layoutWidget_2)
        self.activate_status.setReadOnly(True)
        self.activate_status.setObjectName("activate_status")
        self.gridLayout.addWidget(self.activate_status, 0, 1, 2, 1)
        self.layoutWidget_3 = QtWidgets.QWidget(Dialog)
        self.layoutWidget_3.setGeometry(QtCore.QRect(20, 10, 451, 25))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.license_file = QtWidgets.QLineEdit(self.layoutWidget_3)
        self.license_file.setObjectName("license_file")
        self.horizontalLayout_2.addWidget(self.license_file)
        self.show_license = QtWidgets.QToolButton(self.layoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.show_license.setFont(font)
        self.show_license.setObjectName("show_license")
        self.horizontalLayout_2.addWidget(self.show_license)
        self.activate = QtWidgets.QPushButton(self.layoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activate.setFont(font)
        self.activate.setObjectName("activate")
        self.horizontalLayout_2.addWidget(self.activate)
        self.update = QtWidgets.QPushButton(Dialog)
        self.update.setEnabled(False)
        self.update.setGeometry(QtCore.QRect(390, 150, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.update.setFont(font)
        self.update.setObjectName("update")
        self.abort = QtWidgets.QPushButton(Dialog)
        self.abort.setGeometry(QtCore.QRect(300, 150, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.abort.setFont(font)
        self.abort.setObjectName("abort")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Check for license"))
        self.groupBox.setTitle(_translate("Dialog", "Activation information"))
        self.label_2.setText(_translate("Dialog", "MAC address:"))
        self.label_3.setText(_translate("Dialog", "Status:"))
        self.label.setText(_translate("Dialog", "License file"))
        self.license_file.setPlaceholderText(_translate("Dialog", "license.lic"))
        self.show_license.setText(_translate("Dialog", "..."))
        self.activate.setText(_translate("Dialog", "Activate"))
        self.update.setText(_translate("Dialog", "Update"))
        self.abort.setText(_translate("Dialog", "Abort"))
