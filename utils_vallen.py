import math
import os
import time
import numpy as np
import multiprocessing
from multiprocessing.managers import BaseManager
from PyQt5 import QtCore, Qt
from pac import Preprocessing
from utils import catchError, Reload


class GlobalV_Vallen():
    def __init__(self):
        self.data_tra = []
        self.data_pri = []
        self.chan_1 = []
        self.chan_2 = []
        self.chan_3 = []
        self.chan_4 = []

    def append_tra(self, arg):
        self.data_tra.append(arg)

    def append_pri(self, arg):
        self.data_pri.append(arg)

    def append_1(self, arg):
        self.chan_1.append(arg)

    def append_2(self, arg):
        self.chan_2.append(arg)

    def append_3(self, arg):
        self.chan_3.append(arg)

    def append_4(self, arg):
        self.chan_4.append(arg)

    def get_tra(self):
        return self.data_tra

    def get_pri(self):
        return self.data_pri

    def get_1(self):
        return self.chan_1

    def get_2(self):
        return self.chan_2

    def get_3(self):
        return self.chan_3

    def get_4(self):
        return self.chan_4


class ConvertVallenData(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, path_pri, path_tra, fold, mode, counts):
        super(ConvertVallenData, self).__init__()
        self.path_pri = path_pri
        self.path_tra = path_tra
        self.fold = fold
        self.mode = mode
        self.counts = counts

    @catchError('Error In Converting Vallen Data')
    def run(self):
        print("=" * 27 + " Loading... " + "=" * 28)
        start = time.time()

        manager = BaseManager()
        manager.register('GlobalV_Vallen', GlobalV_Vallen)
        manager.start()
        obj = manager.GlobalV_Vallen()

        # Multiprocessing acceleration
        pool = multiprocessing.Pool(processes=1)
        for _ in range(1):
            reload = Reload(self.path_pri, self.path_tra, self.fold)
            pool.apply_async(reload.read_vallen, (self.mode, self.counts, obj, ))

        pool.close()
        pool.join()

        end = time.time()

        data_tra = sorted(obj.get_tra(), key=lambda x: x[-1])
        data_pri = np.array(obj.get_pri())
        chan_1 = np.array(obj.get_1())
        chan_2 = np.array(obj.get_2())
        chan_3 = np.array(obj.get_3())
        chan_4 = np.array(obj.get_4())

        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".
              format(time.asctime(time.localtime(time.time())), (end - start) / 60))
        if self.mode == 'Load both' or self.mode == 'Load waveforms only':
            print("Waveform Info--All channel: %d" % len(data_tra))
        if self.mode == 'Load both' or self.mode == 'Load features only':
            print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
                  (data_pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0],
                   chan_4.shape[0]))
        self._signal.emit([data_tra, data_pri, chan_1, chan_2, chan_3, chan_4])
