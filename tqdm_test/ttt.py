#!/usr/bin/python
# coding:UTF-8
from PyQt5 import QtWidgets, QtCore
import sys
from PyQt5.QtCore import *
import time


# 继承 QObject
class Runthread(QtCore.QObject):
    #  通过类成员对象定义信号对象
    signal = pyqtSignal(str)

    def __init__(self):
        super(Runthread, self).__init__()
        self.flag = True

    def __del__(self):
        print(">>> __del__")

    def run(self):
        i = 0
        while self.flag:
            time.sleep(0.1)
            if i <= 50:
                self.signal.emit(str(i))  # 注意这里与_signal = pyqtSignal(str)中的类型相同
                i += 1
        print(">>> run end: ")


class Example(QtWidgets.QWidget):
    #  通过类成员对象定义信号对象
    _startThread = pyqtSignal()

    def __init__(self):
        super(Example, self).__init__()
        # 按钮初始化
        self.button_start = QtWidgets.QPushButton('开始', self)
        self.button_stop = QtWidgets.QPushButton('停止', self)
        self.button_start.move(60, 80)
        self.button_stop.move(160, 80)
        self.button_start.clicked.connect(self.start)  # 绑定多线程触发事件
        self.button_stop.clicked.connect(self.stop)  # 绑定多线程触发事件

        # 进度条设置
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(50, 50, 210, 25)
        self.pbar.setValue(0)

        # 窗口初始化
        self.setGeometry(300, 300, 300, 200)
        self.show()


    def start(self):
        self.myT = Runthread()  # 创建线程对象
        self.thread = QThread(self)  # 初始化QThread子线程

        # 把自定义线程加入到QThread子线程中
        self.myT.moveToThread(self.thread)

        self._startThread.connect(self.myT.run)  # 只能通过信号-槽启动线程处理函数
        self.myT.signal.connect(self.call_backlog)

        if self.thread.isRunning():  # 如果该线程正在运行，则不再重新启动
            return

        # 先启动QThread子线程
        self.myT.flag = True
        self.thread.start()
        # 发送信号，启动线程处理函数
        # 不能直接调用，否则会导致线程处理函数和主线程是在同一个线程，同样操作不了主界面
        self._startThread.emit()

    def stop(self):
        if not self.thread.isRunning():  # 如果该线程已经结束，则不再重新关闭
            return
        self.myT.flag = False
        self.stop_thread()

    def call_backlog(self, msg):
        self.pbar.setValue(int(msg))  # 将线程的参数传入进度条

    def stop_thread(self):
        print(">>> stop_thread... ")
        if not self.thread.isRunning():
            return
        self.thread.quit()  # 退出
        self.thread.wait()  # 回收资源
        print(">>> stop_thread end... ")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = Example()
    myshow.show()
    sys.exit(app.exec_())
