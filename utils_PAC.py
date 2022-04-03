"""
@version: 2.0
@author: Jonah
@file: __init__.py
@Created time: 2022/04/02 00:00
@Last Modified: 2022/04/04 00:28
"""

import math
import os
import time
import numpy as np
import multiprocessing
from multiprocessing.managers import BaseManager
from PyQt5 import QtCore, Qt
from pac import Preprocessing
from utils import catchError


class GlobalV():
    def __init__(self):
        self.tra_1 = []
        self.tra_2 = []
        self.tra_3 = []
        self.tra_4 = []

    def append_1(self, arg):
        self.tra_1.append(arg)

    def append_2(self, arg):
        self.tra_2.append(arg)

    def append_3(self, arg):
        self.tra_3.append(arg)

    def append_4(self, arg):
        self.tra_4.append(arg)

    def get_1(self):
        return self.tra_1

    def get_2(self):
        return self.tra_2

    def get_3(self):
        return self.tra_3

    def get_4(self):
        return self.tra_4


class ConvertPacData(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, featuresData, PACData, data_path, threshold, magnification, processor, load_wave,
                 load_features, counts):
        super(ConvertPacData, self).__init__()
        self.featuresData = featuresData
        self.PACData = PACData
        self.processor = processor
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path
        self.load_wave = load_wave
        self.load_features = load_features
        self.counts = counts
        self.file_list = None

    @catchError('Error In Converting PAC Data')
    def run(self):
        try:
            os.remove(self.featuresData)
        except FileNotFoundError:
            pass
        self.file_list = os.listdir(self.data_path)
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        result, data_tra = [], []
        data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], []
        PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4 = [], [], [], []
        print("=" * 27 + " Loading... " + "=" * 28)
        start = time.time()

        manager = BaseManager()
        # 一定要在start前注册，不然就注册无效
        manager.register('GlobalV', GlobalV)
        manager.start()
        obj = manager.GlobalV()

        # Multiprocessing acceleration
        pool = multiprocessing.Pool(processes=self.processor)
        for idx, i in enumerate(range(0, len(self.file_list), each_core)):
            process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
            result.append(pool.apply_async(process.main, (self.file_list[i:i + each_core], obj, self.load_wave, self.counts,)))

        pri = process.save_features(result)

        pool.close()
        pool.join()

        data_pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in pri])
        if self.load_features:
            chan_1 = data_pri[np.where(data_pri[:, 2] == 1)[0]]
            chan_2 = data_pri[np.where(data_pri[:, 2] == 2)[0]]
            chan_3 = data_pri[np.where(data_pri[:, 2] == 3)[0]]
            chan_4 = data_pri[np.where(data_pri[:, 2] == 4)[0]]
        del pri

        if self.PACData:
            with open(os.path.join('/'.join(self.data_path.split('/')[:-1]),
                                   '%s.TXT' % self.data_path.split('/')[-1]), 'r') as f:
                data_pac_origin = np.array([np.array(i.strip().split()) for i in f.readlines()[8:]])
            valid_pac_origin = np.where(data_pac_origin[:, 6].astype(int) > self.counts)[0]
            # time, chan, ristT, cnts, eny, dur, amp, rms, absEny
            PAC_data_pri = np.hstack((np.array([sum(np.array(list(map(lambda j: float(j), i.split(':')))) * [3600, 60, 1]) for i in data_pac_origin[valid_pac_origin][:, 2]]).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 4].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 5].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 6].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 7].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 8].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 9].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 11].astype(float).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, -2].astype(float).reshape(-1, 1)))
            del data_pac_origin, valid_pac_origin
            PAC_chan_1 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 1)[0]]
            PAC_chan_2 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 2)[0]]
            PAC_chan_3 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 3)[0]]
            PAC_chan_4 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 4)[0]]
            del PAC_data_pri

        end = time.time()

        print('Complete the converting of waveform!')
        print("=" * 22 + " Convertion information " + "=" * 22)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("Calculation Info--Quantity of valid data: %s" % data_pri.shape[0])
        if self.load_wave:
            print("Waveform Info--Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
                  (len(obj.get_1()), len(obj.get_2()), len(obj.get_3()), len(obj.get_4())))
        if self.load_features:
            print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (data_pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))
        else:
            data_pri = []
        self._signal.emit([data_pri, chan_1, chan_2, chan_3, chan_4, sorted(obj.get_1(), key=lambda x: x[-1]),
                           sorted(obj.get_2(), key=lambda x: x[-1]), sorted(obj.get_3(), key=lambda x: x[-1]),
                           sorted(obj.get_4(), key=lambda x: x[-1]), PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4,
                           self.load_wave, self.load_features])


class ReadPacData(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, featuresData, PACData, file_list, data_path, threshold, magnification, processor, counts,
                 overwrite):
        super(ReadPacData, self).__init__()
        self.featuresData = featuresData
        self.PACData = PACData
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path
        self.counts = counts
        self.overwrite = overwrite

    @catchError('Error In Loading PAC Data')
    def run(self):
        if self.featuresData in self.file_list:
            exist_idx = np.where(np.array(self.file_list) == self.featuresData)[0][0]
            self.file_list = self.file_list[0:exist_idx] + self.file_list[exist_idx + 1:]

        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        data_tra, data_pri = [], []
        result, tra_1, tra_2, tra_3, tra_4 = [], [], [], [], []
        PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4 = [], [], [], []

        print("=" * 27 + " Loading... " + "=" * 28)
        manager = BaseManager()
        # 一定要在start前注册，不然就注册无效
        manager.register('GlobalV', GlobalV)
        manager.start()
        obj = manager.GlobalV()

        if self.overwrite:
            start = time.time()
            # Multiprocessing acceleration
            pool = multiprocessing.Pool(processes=self.processor)
            for idx, i in enumerate(range(0, len(self.file_list), each_core)):
                process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
                result.append(
                    pool.apply_async(process.main, (self.file_list[i:i + each_core], obj, False, self.counts,)))

            pri = process.save_features(result)
            data_pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in pri])
            del pri

            pool.close()
            pool.join()

            end = time.time()
            result = []

            print('Complete the converting of waveform!')
            print("=" * 22 + " Convertion information " + "=" * 22)
            print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                               (end - start) / 60))
            print("Calculation Info--Quantity of valid data: %s" % data_pri.shape[0])

        start = time.time()
        # Multiprocessing acceleration
        pool = multiprocessing.Pool(processes=self.processor)
        for idx, i in enumerate(range(0, len(self.file_list), each_core)):
            process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
            result.append(pool.apply_async(process.read_pac_data, (self.file_list[i:i + each_core],)))

        for idx, i in enumerate(result):
            tmp_1, tmp_2, tmp_3, tmp_4 = i.get()
            tra_1.append(tmp_1)
            tra_2.append(tmp_2)
            tra_3.append(tmp_3)
            tra_4.append(tmp_4)

        pool.close()
        pool.join()

        for idx, tra in enumerate([tra_1, tra_2, tra_3, tra_4]):
            tra = [j for i in tra for j in i]
            try:
                data_tra.append(sorted(tra, key=lambda x: x[-1]))
            except IndexError:
                data_tra.append([])
                print('Warning: There is no data in channel %d!' % idx)

        if self.PACData:
            with open(os.path.join('/'.join(self.data_path.split('/')[:-1]),
                                   '%s.TXT' % self.data_path.split('/')[-1]), 'r') as f:
                data_pac_origin = np.array([np.array(i.strip().split()) for i in f.readlines()[8:]])
            valid_pac_origin = np.where(data_pac_origin[:, 6].astype(int) > self.counts)[0]
            # time, chan, ristT, cnts, eny, dur, amp, rms, absEny
            PAC_data_pri = np.hstack((np.array([sum(np.array(list(map(lambda j: float(j), i.split(':')))) * [3600, 60, 1]) for i in data_pac_origin[valid_pac_origin][:, 2]]).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 4].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 5].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 6].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 7].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 8].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 9].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 11].astype(float).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, -2].astype(float).reshape(-1, 1)))
            del data_pac_origin, valid_pac_origin
            PAC_chan_1 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 1)[0]]
            PAC_chan_2 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 2)[0]]
            PAC_chan_3 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 3)[0]]
            PAC_chan_4 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 4)[0]]
            del PAC_data_pri

        end = time.time()
        print('Complete the import of waveform!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (len(data_tra[0]), len(data_tra[1]), len(data_tra[2]), len(data_tra[3])))
        del result, tra_1, tra_2, tra_3, tra_4, tra
        self._signal.emit([data_tra, PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4])


class ReadPacFeatures(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, featuresData, PACData, file_list, data_path, threshold, magnification, processor, counts,
                 overwrite):
        super(ReadPacFeatures, self).__init__()
        self.featuresData = featuresData
        self.PACData = PACData
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path
        self.counts = counts
        self.overwrite = overwrite

    @catchError('Error In Loading PAC Features')
    def run(self):
        exist_idx = np.where(np.array(self.file_list) == self.featuresData)[0][0]
        self.file_list = self.file_list[0:exist_idx] + self.file_list[exist_idx + 1:]
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        data_pri, result, PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4 = [], [], [], [], [], []

        print("=" * 27 + " Loading... " + "=" * 28)

        if self.overwrite:
            manager = BaseManager()
            # 一定要在start前注册，不然就注册无效
            manager.register('GlobalV', GlobalV)
            manager.start()
            obj = manager.GlobalV()

            start = time.time()
            # Multiprocessing acceleration
            pool = multiprocessing.Pool(processes=self.processor)
            for idx, i in enumerate(range(0, len(self.file_list), each_core)):
                process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
                result.append(
                    pool.apply_async(process.main, (self.file_list[i:i + each_core], obj, False, self.counts,)))

            pri = process.save_features(result)
            data_pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in pri])
            del pri, result

            pool.close()
            pool.join()

            end = time.time()

            print('Complete the converting of waveform!')
            print("=" * 22 + " Convertion information " + "=" * 22)
            print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                               (end - start) / 60))
            print("Calculation Info--Quantity of valid data: %s" % data_pri.shape[0])

        with open(self.featuresData, 'r') as f:
            res = [i.strip("\n").strip(',') for i in f.readlines()[1:]]
        print("=" * 27 + " Loading... " + "=" * 28)
        start = time.time()

        pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in res])
        chan_1 = pri[np.where(pri[:, 2] == 1)[0]]
        chan_2 = pri[np.where(pri[:, 2] == 2)[0]]
        chan_3 = pri[np.where(pri[:, 2] == 3)[0]]
        chan_4 = pri[np.where(pri[:, 2] == 4)[0]]
        del res

        if self.PACData:
            with open(os.path.join('/'.join(self.data_path.split('/')[:-1]),
                                   '%s.TXT' % self.data_path.split('/')[-1]), 'r') as f:
                data_pac_origin = np.array([np.array(i.strip().split()) for i in f.readlines()[8:]])
            valid_pac_origin = np.where(data_pac_origin[:, 6].astype(int) > self.counts)[0]
            # time, chan, ristT, cnts, eny, dur, amp, rms, absEny
            PAC_data_pri = np.hstack((np.array([sum(np.array(list(map(lambda j: float(j), i.split(':')))) * [3600, 60, 1]) for i in data_pac_origin[valid_pac_origin][:, 2]]).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 4].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 5].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 6].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 7].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 8].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 9].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 11].astype(float).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, -2].astype(float).reshape(-1, 1)))
            del data_pac_origin, valid_pac_origin
            PAC_chan_1 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 1)[0]]
            PAC_chan_2 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 2)[0]]
            PAC_chan_3 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 3)[0]]
            PAC_chan_4 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 4)[0]]
            del PAC_data_pri

        end = time.time()
        print('Complete the import of features!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))
        self._signal.emit([pri, chan_1, chan_2, chan_3, chan_4, PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4])


class ReadPacDataFeatures(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, featuresData, PACData, file_list, data_path, threshold, magnification, processor, counts,
                 overwrite):
        super(ReadPacDataFeatures, self).__init__()
        self.featuresData = featuresData
        self.PACData = PACData
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path
        self.counts = counts
        self.overwrite = overwrite

    @catchError('Error In Loading PAC Data and Features')
    def run(self):
        if self.featuresData in self.file_list:
            exist_idx = np.where(np.array(self.file_list) == self.featuresData)[0][0]
            self.file_list = self.file_list[0:exist_idx] + self.file_list[exist_idx + 1:]
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        result, tra_1, tra_2, tra_3, tra_4 = [], [], [], [], []
        PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4 = [], [], [], []
        data_tra = []

        print("=" * 27 + " Loading... " + "=" * 28)

        if self.overwrite:
            manager = BaseManager()
            # 一定要在start前注册，不然就注册无效
            manager.register('GlobalV', GlobalV)
            manager.start()
            obj = manager.GlobalV()

            start = time.time()
            # Multiprocessing acceleration
            pool = multiprocessing.Pool(processes=self.processor)
            for idx, i in enumerate(range(0, len(self.file_list), each_core)):
                process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
                result.append(
                    pool.apply_async(process.main, (self.file_list[i:i + each_core], obj, False, self.counts,)))

            pri = process.save_features(result)
            data_pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in pri])
            del pri

            pool.close()
            pool.join()

            end = time.time()
            result = []

            print('Complete the converting of waveform!')
            print("=" * 22 + " Convertion information " + "=" * 22)
            print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                               (end - start) / 60))
            print("Calculation Info--Quantity of valid data: %s" % data_pri.shape[0])

        start = time.time()
        # Multiprocessing acceleration
        pool = multiprocessing.Pool(processes=self.processor)
        for idx, i in enumerate(range(0, len(self.file_list), each_core)):
            process = Preprocessing(idx, self.threshold, self.magnification, self.data_path, self.processor)
            result.append(pool.apply_async(process.read_pac_data, (self.file_list[i:i + each_core],)))

        for idx, i in enumerate(result):
            tmp_1, tmp_2, tmp_3, tmp_4 = i.get()
            tra_1.append(tmp_1)
            tra_2.append(tmp_2)
            tra_3.append(tmp_3)
            tra_4.append(tmp_4)

        pool.close()
        pool.join()

        for idx, tra in enumerate([tra_1, tra_2, tra_3, tra_4]):
            tra = [j for i in tra for j in i]
            try:
                data_tra.append(sorted(tra, key=lambda x: x[-1]))
            except IndexError:
                data_tra.append([])
                print('Warning: There is no data in channel %d!' % idx)

        print('Complete the import of waveform!')
        del result, tra_1, tra_2, tra_3, tra_4, tra

        with open(self.featuresData, 'r') as f:
            res = [i.strip("\n").strip(',') for i in f.readlines()[1:]]
        pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in res])
        chan_1 = pri[np.where(pri[:, 2] == 1)[0]]
        chan_2 = pri[np.where(pri[:, 2] == 2)[0]]
        chan_3 = pri[np.where(pri[:, 2] == 3)[0]]
        chan_4 = pri[np.where(pri[:, 2] == 4)[0]]
        del res

        if self.PACData:
            with open(os.path.join('/'.join(self.data_path.split('/')[:-1]),
                                   '%s.TXT' % self.data_path.split('/')[-1]), 'r') as f:
                data_pac_origin = np.array([np.array(i.strip().split()) for i in f.readlines()[8:]])
            valid_pac_origin = np.where(data_pac_origin[:, 6].astype(int) > self.counts)[0]
            # time, chan, ristT, cnts, eny, dur, amp, rms, absEny
            PAC_data_pri = np.hstack((np.array([sum(np.array(list(map(lambda j: float(j), i.split(':')))) * [3600, 60, 1]) for i in data_pac_origin[valid_pac_origin][:, 2]]).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 4].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 5].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 6].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 7].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 8].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 9].astype(int).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, 11].astype(float).reshape(-1, 1),
                                      data_pac_origin[valid_pac_origin][:, -2].astype(float).reshape(-1, 1)))
            del data_pac_origin, valid_pac_origin
            PAC_chan_1 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 1)[0]]
            PAC_chan_2 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 2)[0]]
            PAC_chan_3 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 3)[0]]
            PAC_chan_4 = PAC_data_pri[np.where(PAC_data_pri[:, 1] == 4)[0]]
            del PAC_data_pri

        end = time.time()
        print('Complete the import of features!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("Waveform Info--Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (len(data_tra[0]), len(data_tra[1]), len(data_tra[2]), len(data_tra[3])))
        print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))
        self._signal.emit([data_tra, pri, chan_1, chan_2, chan_3, chan_4,
                           PAC_chan_1, PAC_chan_2, PAC_chan_3, PAC_chan_4])
