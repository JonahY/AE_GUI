"""
@version: 2.0
@author: Jonah
@file: __init__.py
@time: 2021/11/10 12:56
"""

import sys, os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

import sys
import os
from PyQt5 import QtWidgets, Qt
from authorization import Ui_Dialog
from alone_auth import AuthorizeWindow
from about_info import AboutWindow
from get_mac_addr import get_mac_address
from check_license import CheckLicense
from AEScoder import PrpCrypt
from Controller import MainForm
from multiprocessing import freeze_support


def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable) # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__) # 没打包前的py目录


PROJECT_PATH = app_path()


class AuthWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, win_main):
        super(AuthWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        # self.setFixedSize(self.width(), self.height())

        self.win_main = win_main
        self.active_time = ''
        self.psw = ''

        self.abort.clicked.connect(self.close)
        self.show_license.clicked.connect(self.get_license)
        self.Read_license()

        self.init_UI()
        self.activate.clicked.connect(self.init_UI_2)
        self.enter.clicked.connect(self.OPEN)
        self.information.setText('This software is owned by Yuan.\nPlease send an email to apply for a license.\n'
                                 'E-mail addresses: binchengy@163.com\nInstitution: State Key Laboratory for '
                                 'Mechanical Behavior of Materials, Xi’an Jiaotong University, Xi’an 710049, China')

    def init_UI(self):
        self.setWindowFlags(Qt.Qt.CustomizeWindowHint)
        a = get_mac_address()
        self.mac.setText(a)
        self.init_UI_2()

    def init_UI_2(self):
        check_state = self.check_license_state()
        if check_state == False:
            self.license_file.setEnabled(True)
            self.activate.setEnabled(True)
        else:
            self.license_file.setEnabled(False)
            self.activate.setEnabled(False)
            self.enter.setEnabled(True)

    def check_license_state(self):
        if self.active_time and self.psw:
            check_time_result = CheckLicense().check_date(self.active_time)
            check_psw_result = CheckLicense().check_psw(self.psw)
            date_time = str(self.active_time).replace('T', ' ')
            if check_psw_result:
                if check_time_result:
                    self.activate_status.setText(f'Activation is successful!\nAuthorization ends in {date_time}.')
                    return True
                else:
                    self.activate_status.setText(f'Activation code has expired!\nAuthorization ends in {date_time}.')
        elif self.active_time == self.psw == False:
            self.activate_status.setText(f'Activation is failed!\nPlease change license.')
        else:
            self.activate_status.setText(f'Not activated!\nPlease activate the software.')
        return False

    def get_license(self):
        license_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select license", "C:/", "All Files (*.lic);;Text Files (*.txt)")  # 设置文件扩展名过滤,注意用双分号间隔
        filename = license_file_path.split('/')[-1]
        if filename:
            with open(license_file_path, 'r') as license_file:
                x = license_file.readline()
            files = self.get_license_files()
            if files:
                for file in files:
                    os.remove(PROJECT_PATH + '/lic/' + file)
            license_file_path_new = PROJECT_PATH + '/lic/'+filename
            with open(license_file_path_new, 'w') as f:
                f.write(x)
                f.close()
            self.Read_license()
        pass

    def get_license_files(self):
        path = PROJECT_PATH + '/lic'
        files = os.listdir(path)
        return files

    def Read_license(self):
        path = PROJECT_PATH + '/lic'
        files = self.get_license_files()
        if files:
            filename = files[0]
            self.license_file.setText(filename)
            with open(path + '/' + filename, 'r', encoding='utf-8') as f:
                lic_msg = f.read()
                f.close()
            # str to bytes
            lic_msg = bytes(lic_msg, encoding="utf8")
            pc = PrpCrypt('XJTU_MSE_MBM_714_753_yBc')  # 初始化密钥
            license_str = pc.decrypt(lic_msg)  # 解密
            if license_str:
                license_dic = eval(license_str)
                mac = license_dic['mac']
                self.active_time = license_dic['time_str']
                self.psw = license_dic['psw']
            else:
                self.active_time = False
                self.psw = False
        else:
            self.license_file.setEnabled(True)
            self.show_license.setEnabled(True)

    def OPEN(self):
        self.close()
        self.win_main.show()


if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    win_auth = AuthorizeWindow()
    win_about = AboutWindow()
    win_main = MainForm(win_auth, win_about)
    win = AuthWindow(win_main)
    win.show()
    sys.exit(app.exec_())