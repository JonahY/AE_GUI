"""
@version: 2.0
@author: Jonah
@file: __init__.py
@Created time: 2020/12/15 00:00
@Last Modified: 2022/04/04 00:28
"""

import sqlite3
from tqdm.auto import tqdm
import numpy as np
import array
import pandas as pd
from scipy.signal import savgol_filter
import traceback
from PyQt5 import QtCore, Qt
from wave_freq import Waveform


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

    def read_vallen(self, mode, counts):
        conn_tra = sqlite3.connect(self.path_tra)
        conn_pri = sqlite3.connect(self.path_pri)
        result_tra = conn_tra.execute(
            "Select Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI FROM view_tr_data")
        result_pri = conn_pri.execute(
            "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
        data_tra, data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], [], []
        N_pri = self.sqlite_read(self.path_pri)
        N_tra = self.sqlite_read(self.path_tra)
        if mode == 'Load both' or mode == 'Load waveforms only':
            tqdm_tra = tqdm(range(N_tra), unit_scale=True, dynamic_ncols=True)
            tqdm_tra.set_description("Waveform extraction progress")
            for _ in tqdm_tra:
                i = result_tra.fetchone()
                data_tra.append(i)
            print('Complete the import of waveform!')
        if mode == 'Load both' or mode == 'Load features only':
            tqdm_pri = tqdm(range(N_pri), unit_scale=True, dynamic_ncols=True)
            tqdm_pri.set_description("Feature extraction progress")
            for _ in tqdm_pri:
                i = result_pri.fetchone()
                if i[-2] is not None and i[-2] > counts and i[-1] > 0:
                    data_pri.append(i)
                    if i[2] == 1:
                        chan_1.append(i)
                    elif i[2] == 2:
                        chan_2.append(i)
                    elif i[2] == 3:
                        chan_3.append(i)
                    elif i[2] == 4:
                        chan_4.append(i)
            print('Complete the import of feature!\nSorting ...')
        return sorted(data_tra, key=lambda x: x[-1]), np.array(data_pri), np.array(chan_1), np.array(chan_2), \
               np.array(chan_3), np.array(chan_4)


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


class ShowWaveform(Qt.QThread):
    _signal = QtCore.pyqtSignal(int)

    def __init__(self, fig, trai, data_pri, valid, cwt, color_1, color_2, data_tra, input, output, status,
                 device, thr_dB=25, magnification_dB=60):
        super(ShowWaveform, self).__init__()
        self.fig = fig
        self.trai = trai
        self.data_pri = data_pri
        self.valid = valid
        self.cwt = cwt
        self.color_1 = color_1
        self.color_2 = color_2
        self.data_tra = data_tra
        self.input = input
        self.output = output
        self.status = status
        self.device = device
        self.thr_dB = thr_dB
        self.magnification_dB = magnification_dB

    @catchError('Error In Showing Waveform')
    def run(self):
        waveform = Waveform(self.color_1, self.color_2, self.data_tra, self.input, self.output, self.status,
                            self.device, self.thr_dB, self.magnification_dB)
        waveform.plot_wave_TRAI(self.fig, self.trai, self.data_pri, len(self.data_pri) != 0, self.valid, self.cwt)
        self._signal.emit(self.trai)


class ShowFeaturesCorrelation(Qt.QThread):
    def __init__(self, fig, features, tmp_1, tmp_2, xlabel, ylabel, color):
        super(ShowFeaturesCorrelation, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp_1 = tmp_1
        self.tmp_2 = tmp_2
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.color = color

    @catchError('Error In Showing Features correlation')
    def run(self):
        self.features.plot_correlation(self.fig, self.tmp_1, self.tmp_2, self.xlabel, self.ylabel, self.color)


class ShowPDF(Qt.QThread):
    def __init__(self, fig, features, tmp, xlabel, ylabel, lim, interval_num, color, fit, bin_method):
        super(ShowPDF, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.lim = lim
        self.interval_num = interval_num
        self.color = color
        self.fit = fit
        self.bin_method = bin_method

    @catchError('Error In Showing PDF')
    def run(self):
        self.features.cal_PDF(self.fig, self.tmp, self.xlabel, self.ylabel, self.lim, self.interval_num, self.color,
                              self.fit, self.bin_method)


class ShowCCDF(Qt.QThread):
    def __init__(self, fig, features, tmp, xlabel, ylabel, lim, color, fit):
        super(ShowCCDF, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.lim = lim
        self.color = color
        self.fit = fit

    @catchError('Error In Showing CCDF')
    def run(self):
        self.features.cal_CCDF(self.fig, self.tmp, self.xlabel, self.ylabel, self.lim, self.color, self.fit)


class ShowML(Qt.QThread):
    def __init__(self, fig, features, tmp, xlabel, ylabel, color, ecolor):
        super(ShowML, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.color = color
        self.ecolor = ecolor

    @catchError('Error In Showing ML')
    def run(self):
        self.features.cal_ML(self.fig, self.tmp, self.xlabel, self.ylabel, self.color, self.ecolor)


class ShowContour(Qt.QThread):
    def __init__(self, fig, features, tmp_1, tmp_2, xlabel, ylabel, x_lim, y_lim, size_x, size_y, method, padding,
                 colorbar, clabel):
        super(ShowContour, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp_1 = tmp_1
        self.tmp_2 = tmp_2
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.size_x = size_x
        self.size_y = size_y
        self.method = method
        self.padding = padding
        self.colorbar = colorbar
        self.clabel = clabel

    @catchError('Error In Showing Contour of Features')
    def run(self):
        self.features.cal_contour(self.fig, self.tmp_1, self.tmp_2, self.xlabel, self.ylabel, self.x_lim, self.y_lim,
                                  self.size_x, self.size_y, self.method, self.padding, self.colorbar, self.clabel)


class ShowBathLaw(Qt.QThread):
    def __init__(self, fig, features, tmp, xlabel, ylabel, interval_num, color, bin_method):
        super(ShowBathLaw, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.interval_num = interval_num
        self.color = color
        self.bin_method = bin_method

    @catchError('Error In Showing Bath Law')
    def run(self):
        self.features.cal_BathLaw(self.fig, self.tmp, self.xlabel, self.ylabel, self.interval_num, self.color,
                                  self.bin_method)


class ShowWaitingTime(Qt.QThread):
    def __init__(self, fig, features, time, xlabel, ylabel, interval_num, color, fit, lim, bin_method):
        super(ShowWaitingTime, self).__init__()
        self.fig = fig
        self.features = features
        self.time = time
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.interval_num = interval_num
        self.color = color
        self.fit = fit
        self.lim = lim
        self.bin_method = bin_method

    @catchError('Error In Showing Waiting Time')
    def run(self):
        self.features.cal_WaitingTime(self.fig, self.time, self.xlabel, self.ylabel, self.interval_num, self.color,
                                      self.fit, self.lim, self.bin_method)


class ShowOmoriLaw(Qt.QThread):
    def __init__(self, fig, features, tmp, xlabel, ylabel, interval_num, fit, bin_method):
        super(ShowOmoriLaw, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.interval_num = interval_num
        self.fit = fit
        self.bin_method = bin_method

    @catchError("Error In Showing Omori's Law")
    def run(self):
        self.features.cal_OmoriLaw(self.fig, self.tmp, self.xlabel, self.ylabel, self.interval_num, self.fit,
                                   self.bin_method)


class ShowTimeCorrelation(Qt.QThread):
    def __init__(self, fig, features, tmp, ylabel, x_max, color_tmp, color_stretcher, width, stretcher_data, smooth):
        super(ShowTimeCorrelation, self).__init__()
        self.fig = fig
        self.features = features
        self.tmp = tmp
        self.ylabel = ylabel
        self.x_max = x_max
        self.color_tmp = color_tmp
        self.color_stretcher = color_stretcher
        self.width = width
        self.stretcher_data = stretcher_data
        self.smooth = smooth

    @catchError('Error In Showing Time correlation')
    def run(self):
        self.features.plot_feature_time(self.fig, self.tmp, self.ylabel, self.x_max, self.color_tmp,
                                        self.color_stretcher, self.width, self.stretcher_data, self.smooth)
