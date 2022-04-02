"""
@version: 2.0
@author: Jonah
@file: utils.py
@time: 2021/11/10 12:56
"""

import sqlite3
from tqdm.auto import tqdm
import numpy as np
import array
import os
import pandas as pd
from scipy.signal import savgol_filter
import traceback
import multiprocessing
from multiprocessing.managers import BaseManager
import threading
share_lock = threading.Lock()


class GlobalV():
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


class Reload:
    def __init__(self, path_pri, path_tra, fold):
        self.path_pri = path_pri
        self.path_tra = path_tra
        self.fold = fold

    def sqlite_read(self, path):
        """
        python读取sqlite数据库文件
        """
        mydb = sqlite3.connect(path)  # 链接数据库
        mydb.text_factory = lambda x: str(x, 'gbk', 'ignore')
        cur = mydb.cursor()  # 创建游标cur来执行SQL语句

        # 获取表名
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        Tables = cur.fetchall()  # Tables 为元组列表

        # 获取表结构的所有信息
        if path[-5:] == 'pridb':
            cur.execute("SELECT * FROM {}".format(Tables[3][0]))
            res = cur.fetchall()[-2][1]
        elif path[-5:] == 'tradb':
            cur.execute("SELECT * FROM {}".format(Tables[1][0]))
            res = cur.fetchall()[-3][1]
        return int(res)

    def read_with_time(self, time):
        conn_pri = sqlite3.connect(self.path_pri)
        result_pri = conn_pri.execute(
            "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
        chan_1, chan_2, chan_3, chan_4 = [], [], [], []
        t = [[] for _ in range(len(time) - 1)]
        N_pri = self.sqlite_read(self.path_pri)
        for _ in tqdm(range(N_pri)):
            i = result_pri.fetchone()
            if i[-2] is not None and i[-2] >= 6 and i[-1] > 0:
                for idx, chan in zip(np.arange(1, 5), [chan_1, chan_2, chan_3, chan_4]):
                    if i[2] == idx:
                        chan.append(i)
                        for j in range(len(t)):
                            if time[j] <= i[1] < time[j + 1]:
                                t[j].append(i)
                                break
                        break
        chan_1 = np.array(chan_1)
        chan_2 = np.array(chan_2)
        chan_3 = np.array(chan_3)
        chan_4 = np.array(chan_4)
        return t, chan_1, chan_2, chan_3, chan_4

    def read_vallen_data(self, lower=2):
        conn_tra = sqlite3.connect(self.path_tra)
        conn_pri = sqlite3.connect(self.path_pri)
        result_tra = conn_tra.execute(
            "Select Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI FROM view_tr_data")
        result_pri = conn_pri.execute(
            "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
        data_tra, data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], [], []
        N_pri = self.sqlite_read(self.path_pri)
        N_tra = self.sqlite_read(self.path_tra)
        for _ in tqdm(range(N_tra), ncols=80):
            i = result_tra.fetchone()
            data_tra.append(i)
        for _ in tqdm(range(N_pri), ncols=80):
            i = result_pri.fetchone()
            if i[-2] is not None and i[-2] > lower and i[-1] > 0:
                data_pri.append(i)
                if i[2] == 1:
                    chan_1.append(i)
                if i[2] == 2:
                    chan_2.append(i)
                elif i[2] == 3:
                    chan_3.append(i)
                elif i[2] == 4:
                    chan_4.append(i)
        data_tra = sorted(data_tra, key=lambda x: x[-1])
        data_pri = np.array(data_pri)
        chan_1 = np.array(chan_1)
        chan_2 = np.array(chan_2)
        chan_3 = np.array(chan_3)
        chan_4 = np.array(chan_4)
        return data_tra, data_pri, chan_1, chan_2, chan_3, chan_4

    def read_pac_data(self, path, lower=2):
        os.chdir(path)
        dir_features = os.listdir(path)[0]
        data_tra, data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], [], []
        with open(dir_features, 'r') as f:
            data_pri = np.array([j.strip(', ') for i in f.readlines()[1:] for j in i.strip("\n")])
        for _ in tqdm(range(N_tra), ncols=80):
            i = result_tra.fetchone()
            data_tra.append(i)
        for _ in tqdm(range(N_pri), ncols=80):
            i = result_pri.fetchone()
            if i[-2] is not None and i[-2] > lower and i[-1] > 0:
                data_pri.append(i)
                if i[2] == 1:
                    chan_1.append(i)
                if i[2] == 2:
                    chan_2.append(i)
                elif i[2] == 3:
                    chan_3.append(i)
                elif i[2] == 4:
                    chan_4.append(i)
        data_tra = sorted(data_tra, key=lambda x: x[-1])
        data_pri = np.array(data_pri)
        chan_1 = np.array(chan_1)
        chan_2 = np.array(chan_2)
        chan_3 = np.array(chan_3)
        chan_4 = np.array(chan_4)
        return data_tra, data_pri, chan_1, chan_2, chan_3, chan_4

    def read_vallen(self, mode, counts, obj):
        conn_tra = sqlite3.connect(self.path_tra)
        conn_pri = sqlite3.connect(self.path_pri)
        result_tra = conn_tra.execute(
            "Select Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI FROM view_tr_data")
        result_pri = conn_pri.execute(
            "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
        N_pri = self.sqlite_read(self.path_pri)
        N_tra = self.sqlite_read(self.path_tra)
        global share_lock
        if mode == 'Load both' or mode == 'Load waveforms only':
            tqdm_tra = tqdm(range(N_tra), unit_scale=True, dynamic_ncols=True)
            tqdm_tra.set_description("Waveform extraction progress")
            for _ in tqdm_tra:
                i = result_tra.fetchone()
                obj.append_tra(i)
            print('Complete the import of waveform!')
        if mode == 'Load both' or mode == 'Load features only':
            tqdm_pri = tqdm(range(N_pri), unit_scale=True, dynamic_ncols=True)
            tqdm_pri.set_description("Feature extraction progress")
            for _ in tqdm_pri:
                i = result_pri.fetchone()
                if i[-2] is not None and i[-2] > counts and i[-1] > 0:
                    obj.append_pri(i)
                    if i[2] == 1:
                        obj.append_1(i)
                    elif i[2] == 2:
                        obj.append_2(i)
                    elif i[2] == 3:
                        obj.append_3(i)
                    elif i[2] == 4:
                        obj.append_4(i)
            print('Complete the import of feature!\nSorting ...')
        share_lock.release()


def load_stress(path_curve):
    data = pd.read_csv(path_curve, encoding='gbk').drop(index=[0]).astype('float32')
    data_drop = data.drop_duplicates(['拉伸应变 (应变 1)'])
    time = np.array(data_drop.iloc[:, 0])
    displace = np.array(data_drop.iloc[:, 1])
    load = np.array(data_drop.iloc[:, 2])
    strain = np.array(data_drop.iloc[:, 3])
    stress = np.array(data_drop.iloc[:, 4])
    sort_idx = np.argsort(strain)
    strain = strain[sort_idx]
    stress = stress[sort_idx]
    return time, displace, load, strain, stress


def smooth_curve(time, stress, window_length=99, polyorder=1, epoch=200, curoff=[2500, 25000]):
    y_smooth = savgol_filter(stress, window_length, polyorder, mode='nearest')
    for i in range(epoch):
        if i == 5:
            front = y_smooth
        y_smooth = savgol_filter(y_smooth, window_length, polyorder, mode='nearest')

    front_idx = np.where(time < curoff[0])[0][-1]
    rest_idx = np.where(time > curoff[1])[0][0]
    res = np.concatenate((stress[:40], front[40:front_idx], y_smooth[front_idx:rest_idx], stress[rest_idx:]))
    return res


def catchError(info):
    def outwrapper(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (Exception, BaseException) as e:
                exstr = traceback.format_exc()
                print('=' * ((67 - len(info)) // 2) + ' %s ' % info + '=' * ((67 - len(info)) // 2))
                print(exstr)

        return wrapper

    return outwrapper
