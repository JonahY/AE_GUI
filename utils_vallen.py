"""
@version: 2.0
@author: Jonah
@file: __init__.py
@Created time: 2022/04/02 00:00
@Last Modified: 2022/04/04 00:28
"""

import time
import numpy as np
from PyQt5 import QtCore, Qt
from utils import catchError, Reload
import sqlite3


class ConvertVallenData(QtCore.QObject):
    #  通过类成员对象定义信号对象
    signal = QtCore.pyqtSignal(list)

    def __init__(self, path_pri, path_tra, fold, mode, counts):
        super(ConvertVallenData, self).__init__()
        self.path_pri = path_pri
        self.path_tra = path_tra
        self.fold = fold
        self.mode = mode
        self.counts = counts

    def __del__(self):
        print(">>> __del__ thread")

    @catchError('Error In Converting Vallen Data')
    def run(self):
        print("=" * 27 + " Loading... " + "=" * 28)
        start = time.time()
        print("=" * 23 + " Loading information " + "=" * 24)
        reload = Reload(self.path_pri, self.path_tra, self.fold)
        conn_tra = sqlite3.connect(self.path_tra)
        conn_pri = sqlite3.connect(self.path_pri)
        result_tra = conn_tra.execute(
            "Select Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI FROM view_tr_data")
        result_pri = conn_pri.execute(
            "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
        data_tra, data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], [], []
        N_tra = reload.sqlite_read(self.path_tra)
        N_pri = reload.sqlite_read(self.path_pri)
        if self.mode == 'Load both' or self.mode == 'Load waveforms only':
            for idx in range(N_tra):
                i = result_tra.fetchone()
                data_tra.append(i)
                self.signal.emit(['tradb', idx, N_tra])
                # self.signal.emit([idx, N_tra, N_pri, i])
            print('Complete the import of waveform!')
        if self.mode == 'Load both' or self.mode == 'Load features only':
            for idx in range(N_pri):
                i = result_pri.fetchone()
                if i[-2] is not None and i[-2] > self.counts and i[-1] > 0:
                    data_pri.append(i)
                    if i[2] == 1:
                        chan_1.append(i)
                    elif i[2] == 2:
                        chan_2.append(i)
                    elif i[2] == 3:
                        chan_3.append(i)
                    elif i[2] == 4:
                        chan_4.append(i)
                    self.signal.emit(['pridb', idx, N_pri])
                    # self.signal.emit([idx, N_tra, N_pri, i])
            print('Complete the import of feature!\nSorting ...')
        end = time.time()
        print("Finishing time: {}  |  Time consumption: {:.3f} min".
              format(time.asctime(time.localtime(time.time())), (end - start) / 60))
        self.signal.emit([sorted(data_tra, key=lambda x: x[-1]), np.array(data_pri), np.array(chan_1),
                          np.array(chan_2), np.array(chan_3), np.array(chan_4)])