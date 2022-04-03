# looks like an unused import, but it actually does the TQDM class trick to intercept prints
import output_redirection_tools  # KEEP ME !!!

import logging
import sys
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import pyqtSlot, QObject, QThread
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QTextEdit, QWidget, QToolButton, QVBoxLayout, QApplication, QLineEdit

from config import config_dict, STDOUT_WRITE_STREAM_CONFIG, TQDM_WRITE_STREAM_CONFIG, STREAM_CONFIG_KEY_QUEUE, \
    STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER
# from my_logging import setup_logging
import third_party_module_not_to_change
from tqdm.auto import tqdm
import time


class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        # setup_logging(self.__class__.__name__)

        # self.__logger = logging.getLogger(self.__class__.__name__)
        # self.__logger.setLevel(logging.DEBUG)

        # self.queue_std_out = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QUEUE]
        # self.queue_tqdm = config_dict[TQDM_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QUEUE]

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
        # start thread
        self.btn_perform_actions.setEnabled(False)
        self.thread_initialize.start()

        # self.thread = ThreadTest()
        # self.thread._signal.connect(self.return_date)
        # self.thread.start()

    def return_date(self, result):
        print(result)


class StdOutTextEdit(QTextEdit):
    def __init__(self, parent):
        super(StdOutTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        self.setLineWidth(50)
        self.setMinimumWidth(500)
        self.setFont(QFont('Consolas', 11))

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
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setClearButtonEnabled(True)
        self.setFont(QFont('Consolas', 11))

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
        self._main_app = main_app

    @pyqtSlot()
    def run(self):
        third_party_module_not_to_change.long_procedure()


class ThreadTest(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self):
        super(ThreadTest, self).__init__()

    def run(self):
        tqdm_obect = tqdm(range(10), unit_scale=True, dynamic_ncols=True)
        tqdm_obect.set_description("My progress bar description")
        for i in tqdm_obect:
            time.sleep(0.1)
            print(i)
        self._signal.emit('return')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainApp()
    sys.exit(app.exec_())
