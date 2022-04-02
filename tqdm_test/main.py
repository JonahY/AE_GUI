from PyQt5.QtGui import QTextCursor

from lineEditGUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer, QThread, QTime, pyqtSlot, QProcess
from time import sleep
from config import config_dict, STDOUT_WRITE_STREAM_CONFIG, TQDM_WRITE_STREAM_CONFIG, STREAM_CONFIG_KEY_QUEUE, \
    STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER
import output_redirection_tools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, QObject, QThread, Qt
import third_party_module_not_to_change
from tqdm.auto import tqdm
import time


class MyThread(QThread):
    signalForText = pyqtSignal(str)

    def __init__(self, data=None, parent=None):
        super(MyThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.signalForText.emit(str(text))  # 发射信号

    def run(self):
        # 演示代码
        for i in range(10):
            print("|" * (i // 1), i / 1, "%\r", end='')
            sleep(0.0)
        print("End")


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(MainForm, self).__init__()
        self.setupUi(self)

        # self.th = MyThread()
        # self.th.signalForText.connect(self.outputWritten)
        # sys.stdout = self.th

        self.pushButton.clicked.connect(self._btn_go_clicked)
        self.thread_initialize = QThread()
        self.init_procedure_object = LongProcedureWrapper(self)

        # sys.stdout = EmittingStr(textWritten=self.outputWritten)
        # sys.stderr = EmittingStr(textWritten=self.outputWritten)

        # std out stream management
        # create console text read thread + receiver object
        self.thread_std_out_queue_listener = QThread()
        self.std_out_text_receiver = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.std_out_text_receiver.queue_std_out_element_received_signal.connect(self.append_text)
        # attach console text receiver to console text thread
        self.std_out_text_receiver.moveToThread(self.thread_std_out_queue_listener)
        # attach to start / stop methods
        self.thread_std_out_queue_listener.started.connect(self.std_out_text_receiver.run)
        self.thread_std_out_queue_listener.start()

        self.thread_tqdm_queue_listener = QThread()
        self.tqdm_text_receiver = config_dict[TQDM_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.tqdm_text_receiver.queue_tqdm_element_received_signal.connect(self.set_tqdm_text)
        # attach console text receiver to console text thread
        self.tqdm_text_receiver.moveToThread(self.thread_tqdm_queue_listener)
        # attach to start / stop methods
        self.thread_tqdm_queue_listener.started.connect(self.tqdm_text_receiver.run)
        self.thread_tqdm_queue_listener.start()

    def set_tqdm_text(self, text: str):
        new_text = text
        if new_text.find('\r') >= 0:
            new_text = new_text.replace('\r', '').rstrip()
            if new_text:
                self.lineEdit.setText(new_text)
        else:
            # we suppose that all TQDM prints have \r, so drop the rest
            pass

    def append_text(self, text: str):
        self.textBrowser.moveCursor(QTextCursor.End)
        self.textBrowser.insertPlainText(text)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()
        # self.lineEdit.setText(text)

    def search(self):
        try:
            self.t = MyThread()
            self.t.start()
        except Exception as e:
            raise e

    def genMastClicked(self):
        """Runs the main function."""
        print('Running...')
        self.search()

        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)

    def _btn_go_clicked(self):
        # prepare thread for long operation
        self.init_procedure_object.moveToThread(self.thread_initialize)
        self.thread_initialize.started.connect(self.init_procedure_object.run)
        # start thread
        self.pushButton.setEnabled(False)
        self.thread_initialize.start()
        print(self.thread_initialize.get)


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setMinimumWidth(500)

        self.btn_perform_actions = QToolButton(self)
        self.btn_perform_actions.setText('Launch long processing')
        self.btn_perform_actions.clicked.connect(self._btn_go_clicked)

        self.text_edit_std_out = StdOutTextEdit(self)
        self.text_edit_tqdm = StdTQDMTextEdit(self)

        self.thread_initialize = QThread()
        self.init_procedure_object = LongProcedureWrapper(self)

        # std out stream management
        # create console text read thread + receiver object
        self.thread_std_out_queue_listener = QThread()
        self.std_out_text_receiver = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.std_out_text_receiver.queue_std_out_element_received_signal.connect(self.text_edit_std_out.append_text)
        # attach console text receiver to console text thread
        self.std_out_text_receiver.moveToThread(self.thread_std_out_queue_listener)
        # attach to start / stop methods
        self.thread_std_out_queue_listener.started.connect(self.std_out_text_receiver.run)
        self.thread_std_out_queue_listener.start()

        # NEW: TQDM stream management
        self.thread_tqdm_queue_listener = QThread()
        self.tqdm_text_receiver = config_dict[TQDM_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.tqdm_text_receiver.queue_tqdm_element_received_signal.connect(self.text_edit_tqdm.set_tqdm_text)
        # attach console text receiver to console text thread
        self.tqdm_text_receiver.moveToThread(self.thread_tqdm_queue_listener)
        # attach to start / stop methods
        self.thread_tqdm_queue_listener.started.connect(self.tqdm_text_receiver.run)
        self.thread_tqdm_queue_listener.start()

        layout.addWidget(self.btn_perform_actions)
        layout.addWidget(self.text_edit_std_out)
        layout.addWidget(self.text_edit_tqdm)
        self.setLayout(layout)
        self.show()

    @pyqtSlot()
    def _btn_go_clicked(self):
        # prepare thread for long operation
        self.init_procedure_object.moveToThread(self.thread_initialize)
        self.thread_initialize.started.connect(self.init_procedure_object.run)
        # self.thread_initialize.started.connect(lambda: self.init_procedure_object.run(self.text_edit_tqdm))
        # start thread
        self.btn_perform_actions.setEnabled(False)
        self.thread_initialize.start()


class StdOutTextEdit(QTextEdit):
    def __init__(self, parent):
        super(StdOutTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        self.setLineWidth(50)
        self.setMinimumWidth(500)

    @pyqtSlot(str)
    def append_text(self, text: str):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)


class StdTQDMTextEdit(QLineEdit):
    def __init__(self, parent):
        super(StdTQDMTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        self.setEnabled(True)
        self.setMinimumWidth(500)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setClearButtonEnabled(True)

    @pyqtSlot(str)
    def set_tqdm_text(self, text: str):
        new_text = text
        if new_text.find('\r') >= 0:
            new_text = new_text.replace('\r', '').rstrip()
            if new_text:
                self.setText(new_text)
        else:
            # we suppose that all TQDM prints have \r, so drop the rest
            pass


class LongProcedureWrapper(QObject):
    def __init__(self, main_app: MainApp):
        super(LongProcedureWrapper, self).__init__()
        # self._main_app = main_app

    @pyqtSlot()
    def run(self):
        # third_party_module_not_to_change.long_procedure()
        tqdm_obect = tqdm(range(10), unit_scale=True, dynamic_ncols=True)
        tqdm_obect.set_description("My progress bar description")
        for i in tqdm_obect:
            time.sleep(0.1)
            print(i)
        # text_edit_tqdm.clear()
        for i in tqdm_obect:
            time.sleep(0.2)
            print(i)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # win_main = MainForm()
    # win_main.show()
    ex = MainApp()
    sys.exit(app.exec_())
