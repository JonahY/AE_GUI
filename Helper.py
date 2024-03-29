"""
@version: 2.0
@author: Jonah
@file: __init__.py
@time: 2021/11/10 12:56
"""

from Visualization import AuthWindow
from alone_auth import AuthorizeWindow
from about_info import AboutWindow
from Controller import MainForm
from PyQt5 import QtWidgets
from multiprocessing import freeze_support
import sys
import os


if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    win_auth = AuthorizeWindow()
    win_about = AboutWindow()
    win_main = MainForm(win_auth, win_about)
    win = AuthWindow(win_main)
    win.show()
    sys.exit(app.exec_())