import sys
from queue import Queue

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from config import config_dict, IS_STREAMS_REDIRECTION_SETUP_DONE, TQDM_WRITE_STREAM_CONFIG, STDOUT_WRITE_STREAM_CONFIG, \
    STREAM_CONFIG_KEY_QUEUE, STREAM_CONFIG_KEY_STREAM, STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER


class QueueWriteStream(object):
    def __init__(self, q: Queue):
        self.queue = q

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass


def perform_tqdm_default_out_stream_hack(tqdm_file_stream, tqdm_nb_columns=None):
    import tqdm
    # save original class into module
    tqdm.orignal_class = tqdm.tqdm

    class TQDMPatch(tqdm.orignal_class):
        """
        Derive from original class
        """

        def __init__(self, iterable=None, desc=None, total=None, leave=True,
                     file=None, ncols=None, mininterval=0.1, maxinterval=10.0,
                     miniters=None, ascii=None, disable=False, unit='it',
                     unit_scale=False, dynamic_ncols=False, smoothing=0.3,
                     bar_format=None, initial=0, position=None, postfix=None,
                     unit_divisor=1000, gui=False, **kwargs):
            super(TQDMPatch, self).__init__(iterable, desc, total, leave,
                                            tqdm_file_stream,  # change any chosen file stream with our's
                                            tqdm_nb_columns,  # change nb of columns (gui choice),
                                            mininterval, maxinterval,
                                            miniters, ascii, disable, unit,
                                            unit_scale,
                                            False,  # change param
                                            smoothing,
                                            bar_format, initial, position, postfix,
                                            unit_divisor, gui, **kwargs)
            print('TQDM Patch called')  # check it works

        @classmethod
        def write(cls, s, file=None, end="\n", nolock=False):
            super(TQDMPatch, cls).write(s=s, file=file, end=end, nolock=nolock)
            #tqdm.orignal_class.write(s=s, file=file, end=end, nolock=nolock)

        # all other tqdm.orignal_class @classmethod methods may need to be redefined !

    # # I mainly used tqdm.auto in my modules, so use that for patch
    # # unsure if this will work with all possible tqdm import methods
    # # might not work for tqdm_gui !
    import tqdm.auto as AUTO
    #
    # # change original class with the patched one, the original still exists
    AUTO.tqdm = TQDMPatch
    #tqdm.tqdm = TQDMPatch


def setup_streams_redirection(tqdm_nb_columns=None):
    if config_dict[IS_STREAMS_REDIRECTION_SETUP_DONE]:
        pass
    else:
        configure_tqdm_redirection(tqdm_nb_columns)
        configure_std_out_redirection()
        config_dict[IS_STREAMS_REDIRECTION_SETUP_DONE] = True


def configure_std_out_redirection():
    queue_std_out = Queue()
    config_dict[STDOUT_WRITE_STREAM_CONFIG] = {
        STREAM_CONFIG_KEY_QUEUE: queue_std_out,
        STREAM_CONFIG_KEY_STREAM: QueueWriteStream(queue_std_out),
        STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER: StdOutTextQueueReceiver(q=queue_std_out)
    }
    perform_std_out_hack()


def perform_std_out_hack():
    sys.stdout = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_STREAM]


def configure_tqdm_redirection(tqdm_nb_columns=None):
    queue_tqdm = Queue()
    config_dict[TQDM_WRITE_STREAM_CONFIG] = {
        STREAM_CONFIG_KEY_QUEUE: queue_tqdm,
        STREAM_CONFIG_KEY_STREAM: QueueWriteStream(queue_tqdm),
        STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER: TQDMTextQueueReceiver(q=queue_tqdm)
    }
    perform_tqdm_default_out_stream_hack(
        tqdm_file_stream=config_dict[TQDM_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_STREAM],
        tqdm_nb_columns=tqdm_nb_columns)


class StdOutTextQueueReceiver(QObject):
    # we are forced to define 1 signal per class
    # see https://stackoverflow.com/questions/50294652/how-to-create-pyqtsignals-dynamically
    queue_std_out_element_received_signal = pyqtSignal(str)

    def __init__(self, q: Queue, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.queue = q

    @pyqtSlot()
    def run(self):
        self.queue_std_out_element_received_signal.emit('---> STD OUT Queue reception Started <---\n')
        while True:
            text = self.queue.get()
            self.queue_std_out_element_received_signal.emit(text)


class TQDMTextQueueReceiver(QObject):
    # we are forced to define 1 signal per class
    # see https://stackoverflow.com/questions/50294652/how-to-create-pyqtsignals-dynamically
    queue_tqdm_element_received_signal = pyqtSignal(str)

    def __init__(self, q: Queue, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.queue = q

    @pyqtSlot()
    def run(self):
        # we assume that all TQDM outputs start with \r, so use that to show stream reception is started
        self.queue_tqdm_element_received_signal.emit('\r---> TQDM Queue reception Started <---\n')
        while True:
            text = self.queue.get()
            self.queue_tqdm_element_received_signal.emit(text)


setup_streams_redirection()