import sys
import os
from PyQt5 import QtWidgets, Qt
from alone_authorization import Ui_Dialog
from get_mac_addr import get_mac_address
from check_license import CheckLicense
from AEScoder import PrpCrypt
from datetime import datetime


def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable) # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__) # 没打包前的py目录

PROJECT_PATH = app_path()


class AuthorizeWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(AuthorizeWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())

        self.active_time = ''
        self.psw = ''
        self.longest = datetime.now().isoformat().split('.')[0]

        self.get_longest()
        self.init_UI()

        self.show_license.clicked.connect(self.get_license)
        self.activate.clicked.connect(self.init_UI_2)
        self.update.clicked.connect(self.Update)
        self.abort.clicked.connect(self.Close)

    def init_UI(self):
        self.setWindowFlags(Qt.Qt.CustomizeWindowHint)
        a = get_mac_address()
        self.mac.setText(a)
        self.init_UI_2()

    def init_UI_2(self):
        check_state = self.check_license_state()
        if check_state == False:
            self.license_file.setEnabled(True)
        else:
            self.license_file.setEnabled(False)
            self.update.setEnabled(True)

    def check_license_state(self):
        if self.active_time and self.psw:
            check_time_result = CheckLicense().check_update(self.longest, self.active_time)
            check_psw_result = CheckLicense().check_psw(self.psw)
            date_time = str(self.active_time).replace('T', ' ')
            if check_psw_result:
                if check_time_result:
                    self.activate_status.setText(f'Authorization ends in {date_time}.')
                    return True
                else:
                    self.activate_status.setText(f'This authorization period is shorter than the one that has been activated!')
        elif self.active_time == self.psw == False:
            self.activate_status.setText(f'Activation is failed!\nPlease change license.')
        else:
            self.activate_status.setText(f'Not activated!\nPlease activate the software.')
        return False

    def get_license(self):
        license_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select license", "C:/", "All Files (*.lic);;Text Files (*.txt)")  # 设置文件扩展名过滤,注意用双分号间隔
        self.filename = license_file_path.split('/')[-1]
        self.license_file.setText(self.filename)
        if self.filename:
            with open(license_file_path, 'r') as license_file:
                self.input = license_file.readline()
            lic_msg = bytes(self.input, encoding="utf8")
            pc = PrpCrypt('XJTU_MSE_MBM_714')  # 初始化密钥
            license_str = pc.decrypt(lic_msg)  # 解密
            if license_str:
                license_dic = eval(license_str)
                mac = license_dic['mac']
                self.active_time = license_dic['time_str']
                self.psw = license_dic['psw']
            else:
                self.active_time = False
                self.psw = False

    def get_longest(self):
        path = PROJECT_PATH + '/lic'
        files = os.listdir(path)
        if files:
            filename = files[0]
            self.license_file.setText(filename)
            with open(PROJECT_PATH + '/lic/' + filename, 'r', encoding='utf-8') as f:
                lic_msg = f.read()
                f.close()
            lic_msg = bytes(lic_msg, encoding="utf8")
            pc = PrpCrypt('XJTU_MSE_MBM_714')  # 初始化密钥
            license_str = pc.decrypt(lic_msg)  # 解密
            if license_str:
                license_dic = eval(license_str)
                mac = license_dic['mac']
                self.active_time = license_dic['time_str']
                self.longest = self.active_time
                self.psw = license_dic['psw']
            else:
                self.active_time = False
                self.psw = False

    def Update(self):
        path = PROJECT_PATH + '/lic'
        files = os.listdir(path)
        for file in files:
            os.remove(PROJECT_PATH + '/lic/' + file)
        with open(PROJECT_PATH + '/lic/' + self.filename, 'w') as f:
            f.write(self.input)
            f.close()
        self.close()

    def Close(self):
        self.close()


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    win = AuthorizeWindow()
    win.show()
    sys.exit(app.exec_())