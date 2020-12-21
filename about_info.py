import sys
from PyQt5 import QtWidgets, Qt
from about import Ui_Dialog

class AboutWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle('About Information')
        self.information.setText('This software is owned by Jonah Yuan.\nPlease send an email to apply for a license.\n'
                                 'E-mail addresses: binchengy@163.com\nInstitution: State Key Laboratory for '
                                 'Mechanical Behavior of Materials, Xi’an Jiaotong University, Xi’an 710049, China')


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    win = AboutWindow()
    win.show()
    sys.exit(app.exec_())