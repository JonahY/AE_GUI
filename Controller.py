# -*- coding: utf-8 -*-
from main import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import os
import time
from features import *
from kmeans import *
from plot_format import *
from utils import *
from wave_freq import Waveform, Frequency
from pac import *
from alone_auth import AuthorizeWindow
from about_info import AboutWindow
import numpy as np
import matplotlib.pyplot as plt
import warnings
from matplotlib.pylab import mpl


warnings.filterwarnings("ignore")
mpl.rcParams['axes.unicode_minus'] = False  #显示负号
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
      self.textWritten.emit(str(text))


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


class Convert_pac_data(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, tar, file_list, data_path, threshold, magnification, processor, load_wave, load_features, counts):
        super(Convert_pac_data, self).__init__()
        self.tar = tar
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path
        self.load_wave = load_wave
        self.load_features = load_features
        self.counts = counts

    def run(self):
        os.remove(self.tar)
        self.file_list = os.listdir(self.data_path)
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        result, data_tra, tmp_all = [], [], []
        data_pri, chan_1, chan_2, chan_3, chan_4 = [], [], [], [], []
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
                           sorted(obj.get_4(), key=lambda x: x[-1]), self.load_wave, self.load_features])


class Read_pac_data(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, tar, file_list, data_path, threshold, magnification, processor):
        super(Read_pac_data, self).__init__()
        self.tar = tar
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path

    def run(self):
        if self.tar in self.file_list:
            exist_idx = np.where(np.array(self.file_list) == self.tar)[0][0]
            self.file_list = self.file_list[0:exist_idx] + self.file_list[exist_idx + 1:]
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        result, tra_1, tra_2, tra_3, tra_4 = [], [], [], [], []
        data_tra = []
        print("=" * 27 + " Loading... " + "=" * 28)
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

        end = time.time()
        print('Complete the import of waveform!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (len(data_tra[0]), len(data_tra[1]), len(data_tra[2]), len(data_tra[3])))
        del result, tra_1, tra_2, tra_3, tra_4, tra
        self._signal.emit(data_tra)


class Read_pac_features(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, tar):
        super(Read_pac_features, self).__init__()
        self.tar = tar

    def run(self):
        with open(self.tar, 'r') as f:
            res = [i.strip("\n").strip(',') for i in f.readlines()[1:]]
        print("=" * 27 + " Loading... " + "=" * 28)
        start = time.time()

        pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in res])
        chan_1 = pri[np.where(pri[:, 2] == 1)[0]]
        chan_2 = pri[np.where(pri[:, 2] == 2)[0]]
        chan_3 = pri[np.where(pri[:, 2] == 3)[0]]
        chan_4 = pri[np.where(pri[:, 2] == 4)[0]]
        del res
        end = time.time()
        print('Complete the import of features!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))
        self._signal.emit([pri, chan_1, chan_2, chan_3, chan_4])


class Read_pac_data_features(Qt.QThread):
    _signal = QtCore.pyqtSignal(list)

    def __init__(self, tar, file_list, data_path, threshold, magnification, processor):
        super(Read_pac_data_features, self).__init__()
        self.tar = tar
        self.processor = processor
        self.file_list = file_list
        self.threshold = threshold
        self.magnification = magnification
        self.data_path = data_path

    def run(self):
        if self.tar in self.file_list:
            exist_idx = np.where(np.array(self.file_list) == self.tar)[0][0]
            self.file_list = self.file_list[0:exist_idx] + self.file_list[exist_idx + 1:]
        each_core = int(math.ceil(len(self.file_list) / float(self.processor)))
        result, tra_1, tra_2, tra_3, tra_4 = [], [], [], [], []
        data_tra = []
        print("=" * 27 + " Loading... " + "=" * 28)
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

        with open(self.tar, 'r') as f:
            res = [i.strip("\n").strip(',') for i in f.readlines()[1:]]
        pri = np.array([np.array(i.strip('\n').split(', ')).astype(np.float32) for i in res])
        chan_1 = pri[np.where(pri[:, 2] == 1)[0]]
        chan_2 = pri[np.where(pri[:, 2] == 2)[0]]
        chan_3 = pri[np.where(pri[:, 2] == 3)[0]]
        chan_4 = pri[np.where(pri[:, 2] == 4)[0]]
        del res
        end = time.time()
        print('Complete the import of features!')
        print("=" * 23 + " Loading information " + "=" * 24)
        print("Finishing time: {}  |  Time consumption: {:.3f} min".format(time.asctime(time.localtime(time.time())),
                                                                           (end - start) / 60))
        print("Waveform Info--Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (len(data_tra[0]), len(data_tra[1]), len(data_tra[2]), len(data_tra[3])))
        print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
              (pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))
        self._signal.emit([data_tra, pri, chan_1, chan_2, chan_3, chan_4])


class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    window = []

    def __init__(self, AuthorizeWindow, AboutWindow):
        super(MainForm, self).__init__()
        self.setupUi(self)
        self.xlabelz = ['Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)', 'Counts']
        self.color_1 = [255/255, 0/255, 102/255]
        self.color_2 = [0/255, 136/255, 204/255]
        self.chan = 'Chan 2'
        self.device = 'VALLEN'
        self.input = None
        self.output = None
        self.status = None
        self.stretcher = None
        self.lower = 2
        self.num = 1
        self.tmp = True
        self.processor = 4
        self.auth_win = AuthorizeWindow
        self.about_win = AboutWindow

        # Set TRAI to enter only integer
        self.show_trai.setValidator(QtGui.QIntValidator())
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())

        self.init_open_save()
        self.init_help()
        self.init_device()
        self.init_channel()
        self.init_load()
        self.init_plot()
        self.init_track()
        self.init_pac()

        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

    def init_open_save(self):
        # Open & Save
        self.actionload.triggered.connect(self.openMsg)
        self.actionOpen.triggered.connect(self.openMsg)
        self.actionSave.triggered.connect(self.ExportMsg)
        self.actionExport.triggered.connect(self.ExportMsg)
        self.actionQuit.triggered.connect(self.quit)

    def quit(self):
        self.close()

    def init_help(self):
        self.check_for_license.triggered.connect(self.show_auth)
        self.about.triggered.connect(self.show_info)

    def init_device(self):
        # Select device
        self.VALLEN.toggled.connect(lambda: self.check_device(self.VALLEN))
        self.PAC.toggled.connect(lambda: self.check_device(self.PAC))

    def init_channel(self):
        # Select channel
        self.chan1.toggled.connect(lambda: self.check_chan(self.chan1))
        self.chan2.toggled.connect(lambda: self.check_chan(self.chan2))
        self.chan3.toggled.connect(lambda: self.check_chan(self.chan3))
        self.chan4.toggled.connect(lambda: self.check_chan(self.chan4))
        self.chan1_2.toggled.connect(lambda: self.check_chan(self.chan1_2))
        self.chan2_2.toggled.connect(lambda: self.check_chan(self.chan2_2))
        self.chan3_2.toggled.connect(lambda: self.check_chan(self.chan3_2))
        self.chan4_2.toggled.connect(lambda: self.check_chan(self.chan4_2))

    def init_load(self):
        # Load data from files
        self.import_data.clicked.connect(lambda: self.load_data(self.import_data))
        self.import_data_2.clicked.connect(lambda: self.load_data(self.import_data_2))

    def init_plot(self):
        # Plot waveform with specific TRAI
        self.random_trai.clicked.connect(lambda: self.random_select(self.chan))
        self.plot_waveform.clicked.connect(lambda: self.show_wave(self.show_trai))
        self.plot_feature.clicked.connect(self.show_feature)

    def init_track(self):
        self.show_stretcher_data.clicked.connect(self.open_stretcher)
        self.pdf_fit.currentTextChanged.connect(lambda: self.check_fit(self.pdf_fit, self.pdf_start_fit, self.pdf_end_fit))
        self.ccdf_fit.currentTextChanged.connect(lambda: self.check_fit(self.ccdf_fit, self.ccdf_start_fit, self.ccdf_end_fit))

    def init_pac(self):
        self.Overwrite.clicked.connect(self.check_overwrite)
        self.mode.currentTextChanged.connect(self.check_mode)
        self.counts.valueChanged.connect(self.check_mode)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def check_device(self, btn):
        if btn.isChecked():
            self.device = btn.text()
            if self.device == 'VALLEN':
                self.mode.clear()
                self.mode.addItems(['Load both', 'Load waveforms only', 'Load features only'])
                self.Overwrite.setChecked(False)
                self.Overwrite.setEnabled(False)
                self.Threshold.setEnabled(False)
                self.threshold.setEnabled(False)
                self.Magnification.setEnabled(False)
                self.magnification.setEnabled(False)
                self.import_data.setEnabled(False)
            else:
                self.mode.clear()
                self.mode.addItems(['Convert only', 'Convert with waveforms loading', 'Convert with features loading',
                                    'Convert with both loading'])
                self.import_data.setEnabled(False)
                self.Threshold.setEnabled(True)
                self.threshold.setEnabled(True)
                self.Magnification.setEnabled(True)
                self.magnification.setEnabled(True)

    def openMsg(self):
        if self.device == 'VALLEN':
            files = QtWidgets.QFileDialog.getOpenFileNames(self, "Open",
                                                 "E:/data/vallen/Ni-tension test-electrolysis-1-0.01-AE-20201031/",
                                                 "VALLEN Files (*.pridb & *.tradb)")[0]
            self.input = files
            if len(self.input) == 2 and all(['pridb' in self.input[0] or 'pridb' in self.input[1], 'tradb' in self.input[0] or 'tradb' in self.input[1]]):
                self.show_input.setText(self.input[0].split('/')[-1][:-6])
                self.show_input_2.setText(self.input[0].split('/')[-1][:-6])
                self.import_data.setEnabled(True)
                self.import_data_2.setEnabled(True)
                self.textBrowser.setEnabled(True)
                self.statusbar.showMessage('Select loading path successfully!')
                print("=" * 25 + " Import message " + "=" * 25)
                print(self.input[0])
                print(self.input[1])
            else:
                self.statusbar.showMessage('Please select correct files!')
        else:
            file = QtWidgets.QFileDialog.getExistingDirectory(self, "Open", "D:/data/")
            self.input = file
            if self.input:
                self.tar = self.input.split('/')[-1] + '.txt'
                self.file_list = os.listdir(self.input)
                print(self.tar, self.input)
                if not len(self.file_list):
                    self.statusbar.showMessage('This file is empty!')
                    return
                self.show_input.setEnabled(True)
                self.show_input.setText(self.input)
                self.import_data.setEnabled(True)
                self.textBrowser.setEnabled(True)
                self.Overwrite.setChecked(False)
                if self.tar in os.listdir(self.input):
                    self.Overwrite.setEnabled(True)
                    self.mode.clear()
                    self.mode.addItems(['Load both', 'Load waveforms only', 'Load features only'])
                    self.statusbar.showMessage('Please be careful to press the Overwrite button, the original data may be lost.')
                    print("=" * 28 + " Warning " + "=" * 28)
                    print("Converted data file has been detected. Press button [Overwrite] to choose overwrite it or not.")
                else:
                    self.Overwrite.setEnabled(False)
                    self.mode.clear()
                    self.mode.addItems(['Convert only', 'Convert with waveforms loading',
                                        'Convert with features loading', 'Convert with both loading', 'Load waveforms only'])
                    self.statusbar.showMessage('Press [IMPORT] to continue.')
                    print("=" * 23 + " Convert information " + "=" * 23)
                print(self.input)
                print('Ready to convert data, remember to choose whether to read waveforms and features')
            else:
                self.statusbar.showMessage('Please select correct file!')

    def open_stretcher(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open", "E:/data/vallen/Ni-tension test-electrolysis-1-0.01-AE-20201031/Ni-tension test-electrolysis-1-0.01-20201031.is_tens_RawData", "csv Files (*.csv)")[0]
        self.stretcher = file
        if file:
            self.smooth.setEnabled(True)
            self.stress_color.setEnabled(True)
            self.statusbar.showMessage('Load stretcher data successfully!')
            print("=" * 25 + " Import message " + "=" * 25)
            print(self.stretcher)
        else:
            self.statusbar.showMessage("Please select correct stretcher's file!")

    def ExportMsg(self):
        file = QtWidgets.QFileDialog.getExistingDirectory(self, "Select File Directory to Save File", "")
        if file:
            self.output = file
            self.show_export.setText(self.output)
            self.textBrowser.setEnabled(True)
            self.statusbar.showMessage('Select save path successfully!')
            print("=" * 25 + " Export message " + "=" * 25)
            print(file)
        else:
            self.statusbar.showMessage('Please select correct save path!')

    def check_chan(self, btn):
        if btn.isChecked():
            self.chan = btn.text()

    def check_fit(self, btn, btn1, btn2):
        if btn.currentText() == str(True):
            btn1.setEnabled(True)
            btn2.setEnabled(True)
        else:
            btn1.setEnabled(False)
            btn2.setEnabled(False)

    def check_overwrite(self):
        if self.Overwrite.isChecked():
            self.mode.addItems(['Convert only', 'Convert with waveforms loading', 'Convert with features loading',
                                'Convert with both loading'])
        else:
            self.mode.clear()
            self.mode.addItems(['Load both', 'Load waveforms only', 'Load features only'])

    def check_mode(self):
        self.import_data.setEnabled(True)

    def btn_base(self, status):
        self.actionload.setEnabled(status)
        self.actionOpen.setEnabled(status)
        self.actionSave.setEnabled(status)
        self.actionExport.setEnabled(status)
        self.VALLEN.setEnabled(status)
        self.PAC.setEnabled(status)
        self.show_figurenote.setEnabled(status)
        self.Threshold.setEnabled(status)
        self.Magnification.setEnabled(status)
        self.threshold.setEnabled(status)
        self.magnification.setEnabled(status)
        self.Counts.setEnabled(status)
        self.counts.setEnabled(status)
        self.Mode.setEnabled(status)
        self.mode.setEnabled(status)
        self.Overwrite.setEnabled(status)

    def btn_wave(self, status):
        self.chan1.setEnabled(status)
        self.chan2.setEnabled(status)
        self.chan3.setEnabled(status)
        self.chan4.setEnabled(status)
        self.plot_waveform.setEnabled(status)
        self.show_trai.setEnabled(status)

    def btn_feature(self, status):
        self.chan1_2.setEnabled(status)
        self.chan2_2.setEnabled(status)
        self.chan3_2.setEnabled(status)
        self.chan4_2.setEnabled(status)
        self.plot_feature.setEnabled(status)
        self.min_cnts.setEnabled(status)
        self.max_cnts.setEnabled(status)
        self.min_time.setEnabled(status)
        self.max_time.setEnabled(status)
        self.min_x.setEnabled(status)
        self.max_x.setEnabled(status)
        self.min_xx.setEnabled(status)
        self.max_xx.setEnabled(status)
        self.min_xxx.setEnabled(status)
        self.max_xxx.setEnabled(status)
        self.E_A.setEnabled(status)
        self.E_D.setEnabled(status)
        self.A_D.setEnabled(status)
        self.PDF_E.setEnabled(status)
        self.PDF_A.setEnabled(status)
        self.PDF_D.setEnabled(status)
        self.CCDF_E.setEnabled(status)
        self.CCDF_A.setEnabled(status)
        self.CCDF_D.setEnabled(status)
        self.ML_E.setEnabled(status)
        self.ML_A.setEnabled(status)
        self.ML_D.setEnabled(status)
        self.contour_D_E.setEnabled(status)
        self.contour_E_A.setEnabled(status)
        self.contour_D_A.setEnabled(status)
        self.E_T.setEnabled(status)
        self.A_T.setEnabled(status)
        self.D_T.setEnabled(status)
        self.C_T.setEnabled(status)
        self.bathlaw.setEnabled(status)
        self.waitingtime.setEnabled(status)
        self.omorilaw.setEnabled(status)
        self.pdf_select_color.setEnabled(status)
        self.pdf_fit.setEnabled(status)
        self.pdf_interv_num.setEnabled(status)
        self.ml_select_color.setEnabled(status)
        self.correlation_select_color.setEnabled(status)
        self.ccdf_select_color.setEnabled(status)
        self.ccdf_fit.setEnabled(status)
        self.contour_method.setEnabled(status)
        self.contour_padding.setEnabled(status)
        self.contour_x_min.setEnabled(status)
        self.contour_x_max.setEnabled(status)
        self.contour_x_bin.setEnabled(status)
        self.contour_colorbar.setEnabled(status)
        self.contour_y_min.setEnabled(status)
        self.contour_y_max.setEnabled(status)
        self.contour_y_bin.setEnabled(status)
        self.bathlaw_color.setEnabled(status)
        self.bathlaw_interv_num.setEnabled(status)
        self.omorilaw_interv_num.setEnabled(status)
        self.waitingtime_color.setEnabled(status)
        self.waitingtime_interv_num.setEnabled(status)
        self.show_ending_time.setEnabled(status)
        self.show_stretcher_data.setEnabled(status)
        self.bar_width.setEnabled(status)
        self.feature_color.setEnabled(status)

    # def onTimeout(self):
    #     # while self.value < self.N_tra:
    #     for idx in range(self.N_tra):
    #         i = self.result_tra.fetchone()
    #         self.data_tra.append(i)
    #         self.progressBar.setValue(idx+1)
    #         # self.value += 1
    #         QtWidgets.QApplication.processEvents()
    #     # while self.value < self.N_pri + self.N_tra:
    #     for idx in range(self.N_tra, self.N_tra+self.N_pri):
    #         i = self.result_pri.fetchone()
    #         if i[-2] is not None and i[-2] > self.lower and i[-1] > 0:
    #             self.data_pri.append(i)
    #             if i[2] == 1:
    #                 self.chan_1.append(i)
    #             if i[2] == 2:
    #                 self.chan_2.append(i)
    #             elif i[2] == 3:
    #                 self.chan_3.append(i)
    #             elif i[2] == 4:
    #                 self.chan_4.append(i)
    #         self.progressBar.setValue(idx+1)
    #         # self.value += 1
    #         QtWidgets.QApplication.processEvents()
    #     self.timer.stop()
    #     self.timer.deleteLater()
    #     del self.timer
    #     self.data_tra = sorted(self.data_tra, key=lambda x: x[-1])
    #     self.data_pri = np.array(self.data_pri)
    #     self.chan_1 = np.array(self.chan_1)
    #     self.chan_2 = np.array(self.chan_2)
    #     self.chan_3 = np.array(self.chan_3)
    #     self.chan_4 = np.array(self.chan_4)
    #     self.end = time.time()
    #     self.statusbar.removeWidget(self.progressBar)
    #     self.statusbar.showMessage('Finishing time: {} | Time consumption: {:.3f} min | Waveforms: {} | Selected '
    #                                'features: {} | Channel 1: {} | Channel 2: {} | Channel 3: {} | Channel 4: {}'.
    #                                format(time.asctime(time.localtime(time.time())), (self.end - self.start) / 60,
    #                                       len(self.data_tra), self.data_pri.shape[0], self.chan_1.shape[0],
    #                                       self.chan_2.shape[0], self.chan_3.shape[0], self.chan_4.shape[0]))
    #     # Activate other buttons
    #     self.btn_status(True)
    #     return

    def load_data(self, btn):
        self.data_tra = []
        self.data_pri = []
        self.chan_1 = []
        self.chan_2 = []
        self.chan_3 = []
        self.chan_4 = []
        self.data_tra_1 = []
        self.data_tra_2 = []
        self.data_tra_3 = []
        self.data_tra_4 = []
        if self.device == 'VALLEN':
            if len(self.input) == 1:
                self.statusbar.showMessage('Please select correct files!')
                return
            try:
                os.chdir(self.output)
            except:
                self.statusbar.showMessage('Error: The save path is empty, please select a correct path!')
                return
            self.start = time.time()
            self.statusbar.clearMessage()
            self.statusbar.showMessage('Loading data...')
            print("=" * 27 + " Loading... " + "=" * 28)
            if 'pridb' in self.input[0]:
                self.path_pri = self.input[0]
                self.path_tra = self.input[1]
            else:
                self.path_pri = self.input[1]
                self.path_tra = self.input[0]

            self.num = 0
            self.value = 0
            self.btn_base(False)
            self.btn_wave(False)
            self.btn_feature(False)
            self.random_trai.setEnabled(False)
            self.import_data.setEnabled(False)
            self.import_data_2.setEnabled(False)
            self.smooth.setEnabled(False)
            self.stress_color.setEnabled(False)
            self.pdf_start_fit.setEnabled(False)
            self.pdf_end_fit.setEnabled(False)
            self.ccdf_start_fit.setEnabled(False)
            self.ccdf_end_fit.setEnabled(False)

            reload = Reload(self.path_pri, self.path_tra, self.input[0].split('/')[-1][:-6])
            conn_tra = sqlite3.connect(self.path_tra)
            conn_pri = sqlite3.connect(self.path_pri)
            self.result_tra = conn_tra.execute(
                "Select Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI FROM view_tr_data")
            self.result_pri = conn_pri.execute(
                "Select SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI FROM view_ae_data")
            self.N_pri = reload.sqlite_read(self.path_pri)
            self.N_tra = reload.sqlite_read(self.path_tra)
            show_tra = pow(10, len(str(self.N_tra)) - 2)
            show_pri = pow(10, len(str(self.N_pri)) - 2)
            if self.mode.currentText() == 'Load both' or self.mode.currentText() == 'Load waveforms only':
                for idx in range(self.N_tra):
                    i = self.result_tra.fetchone()
                    self.data_tra.append(i)
                    if idx % show_tra == 0:
                        self.statusbar.showMessage('Loading waveform... | Status: %d/%d' % (idx+1, self.N_tra))
                    QtWidgets.QApplication.processEvents()
                print('Complete the import of waveform!')
            if self.mode.currentText() == 'Load both' or self.mode.currentText() == 'Load features only':
                for idx in range(self.N_pri):
                    i = self.result_pri.fetchone()
                    if i[-2] is not None and i[-2] > self.counts.value() and i[-1] > 0:
                        self.data_pri.append(i)
                        if i[2] == 1:
                            self.chan_1.append(i)
                        elif i[2] == 2:
                            self.chan_2.append(i)
                        elif i[2] == 3:
                            self.chan_3.append(i)
                        elif i[2] == 4:
                            self.chan_4.append(i)
                    if idx % show_pri == 0:
                        self.statusbar.showMessage('Loading feature... | Status: %d/%d' % (idx+1, self.N_pri))
                    QtWidgets.QApplication.processEvents()
                print('Complete the import of feature!\nSorting ...')
            self.data_tra = sorted(self.data_tra, key=lambda x: x[-1])
            self.data_pri = np.array(self.data_pri)
            self.chan_1 = np.array(self.chan_1)
            self.chan_2 = np.array(self.chan_2)
            self.chan_3 = np.array(self.chan_3)
            self.chan_4 = np.array(self.chan_4)
            self.end = time.time()
            print("=" * 23 + " Loading information " + "=" * 24)
            print("Finishing time: {}  |  Time consumption: {:.3f} min".
                  format(time.asctime(time.localtime(time.time())), (self.end - self.start) / 60))
            if self.mode.currentText() == 'Load both' or self.mode.currentText() == 'Load waveforms only':
                print("Waveform Info--All channel: %d" % len(self.data_tra))
            if self.mode.currentText() == 'Load both' or self.mode.currentText() == 'Load features only':
                print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
                      (self.data_pri.shape[0], self.chan_1.shape[0], self.chan_2.shape[0], self.chan_3.shape[0],
                       self.chan_4.shape[0]))
            if self.mode.currentText() == 'Load both':
                self.btn_wave(True)
                self.btn_feature(True)
                self.random_trai.setEnabled(True)
                self.show_trai.setReadOnly(False)
                self.statusbar.showMessage('Finish loading both!')
            elif self.mode.currentText() == 'Load waveforms only':
                self.btn_wave(True)
                self.show_trai.setReadOnly(False)
                self.statusbar.showMessage('Finish loading waveforms!')
            elif self.mode.currentText() == 'Load features only':
                self.btn_feature(True)
                self.statusbar.showMessage('Finish loading features!')
            self.btn_base(True)
            self.show_figurenote.setReadOnly(False)
            self.Threshold.setEnabled(False)
            self.Magnification.setEnabled(False)
            self.threshold.setEnabled(False)
            self.magnification.setEnabled(False)
            self.Overwrite.setEnabled(False)

            # self.progressBar = QProgressBar()
            # self.progressBar.setRange(0, self.N_tra + self.N_pri)
            # self.statusbar.addPermanentWidget(self.progressBar)
            # self.statusbar.showMessage('Loading data...')
            # self.timer = QTimer(self, timeout=self.onTimeout)
            # self.start = time.time()
            # self.timer.start()
        else:
            if len(self.input) == 2:
                self.statusbar.showMessage('Please select correct files!')
                return
            os.chdir(self.input)
            self.btn_base(False)
            self.btn_wave(False)
            self.btn_feature(False)
            self.random_trai.setEnabled(False)
            self.import_data.setEnabled(False)
            self.import_data_2.setEnabled(False)
            self.smooth.setEnabled(False)
            self.stress_color.setEnabled(False)
            self.pdf_start_fit.setEnabled(False)
            self.pdf_end_fit.setEnabled(False)
            self.ccdf_start_fit.setEnabled(False)
            self.ccdf_end_fit.setEnabled(False)
            self.statusbar.clearMessage()
            self.statusbar.showMessage('Loading data...')
            if self.Overwrite.isChecked():
                if self.mode.currentText() == 'Convert only':
                    self.thread = Convert_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                   self.magnification.value(), self.processor, False, False, self.counts.value())
                    self.thread._signal.connect(self.convert_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Convert with waveforms loading':
                    self.thread = Convert_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                   self.magnification.value(), self.processor, True, False, self.counts.value())
                    self.thread._signal.connect(self.convert_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Convert with features loading':
                    self.thread = Convert_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                   self.magnification.value(), self.processor, False, True, self.counts.value())
                    self.thread._signal.connect(self.convert_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Convert with both loading':
                    self.thread = Convert_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                   self.magnification.value(), self.processor, True, True, self.counts.value())
                    self.thread._signal.connect(self.convert_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Load both':
                    self.thread = Read_pac_data_features(self.tar, self.file_list, self.input, self.threshold.value(),
                                                         self.magnification.value(), self.processor)
                    self.thread._signal.connect(self.read_pac_data_features)
                    self.thread.start()
                elif self.mode.currentText() == 'Load waveforms only':
                    self.thread = Read_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                self.magnification.value(), self.processor)
                    self.thread._signal.connect(self.return_read_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Load features only':
                    self.thread = Read_pac_features(self.tar)
                    self.thread._signal.connect(self.return_read_pac_features)
                    self.thread.start()
            else:
                if self.mode.currentText() == 'Load both':
                    self.thread = Read_pac_data_features(self.tar, self.file_list, self.input, self.threshold.value(),
                                                         self.magnification.value(), self.processor)
                    self.thread._signal.connect(self.read_pac_data_features)
                    self.thread.start()
                elif self.mode.currentText() == 'Load waveforms only':
                    self.thread = Read_pac_data(self.tar, self.file_list, self.input, self.threshold.value(),
                                                self.magnification.value(), self.processor)
                    self.thread._signal.connect(self.return_read_pac_data)
                    self.thread.start()
                elif self.mode.currentText() == 'Load features only':
                    self.thread = Read_pac_features(self.tar)
                    self.thread._signal.connect(self.return_read_pac_features)
                    self.thread.start()

    def random_select(self, btn):
        for channel, chan in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'], [self.chan_1, self.chan_2, self.chan_3, self.chan_4]):
            if btn == channel:
                cur_chan = chan
        try:
            if self.device == 'VALLEN':
                all_trai = cur_chan[:, -1].astype(int)
            else:
                all_trai = cur_chan[:, 0].astype(int)
            try:
                trai = np.random.choice(all_trai, 1)
                self.show_trai.setText(str(trai[0]))
            except ValueError:
                trai = None
                self.show_trai.setText('This channel has no data.')
        except IndexError:
            trai = None
            self.show_trai.setText('This channel has no data.')

    def return_read_pac_data(self, result):
        self.data_tra_1 = result[0]
        self.data_tra_2 = result[1]
        self.data_tra_3 = result[2]
        self.data_tra_4 = result[3]
        del result
        self.btn_base(True)
        self.btn_wave(True)
        self.show_trai.setReadOnly(False)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading waveforms!')

    def return_read_pac_features(self, result):
        self.data_pri = result[0]
        self.chan_1 = result[1]
        self.chan_2 = result[2]
        self.chan_3 = result[3]
        self.chan_4 = result[4]
        del result
        self.show_input_2.setText(self.tar)
        self.btn_base(True)
        self.btn_feature(True)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading features!')

    def convert_pac_data(self, result):
        self.data_pri = result[0]
        self.chan_1 = result[1]
        self.chan_2 = result[2]
        self.chan_3 = result[3]
        self.chan_4 = result[4]
        self.data_tra_1 = result[5]
        self.data_tra_2 = result[6]
        self.data_tra_3 = result[7]
        self.data_tra_4 = result[8]
        if result[-2] and not result[-1]:
            self.btn_wave(True)
            self.show_trai.setReadOnly(False)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading waveforms!')
        elif not result[-2] and result[-1]:
            self.show_input_2.setText(self.tar)
            self.btn_feature(True)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading features!')
        elif result[-2] and result[-1]:
            self.show_input_2.setText(self.tar)
            self.btn_wave(True)
            self.btn_feature(True)
            self.random_trai.setEnabled(True)
            self.show_trai.setReadOnly(False)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading both!')
        else:
            self.statusbar.showMessage('Finish converting!')
        self.btn_base(True)
        del result

    def read_pac_data_features(self, result):
        self.data_tra_1 = result[0][0]
        self.data_tra_2 = result[0][1]
        self.data_tra_3 = result[0][2]
        self.data_tra_4 = result[0][3]
        self.data_pri = result[1]
        self.chan_1 = result[2]
        self.chan_2 = result[3]
        self.chan_3 = result[4]
        self.chan_4 = result[5]
        self.show_input_2.setText(self.tar)
        self.btn_base(True)
        self.btn_wave(True)
        self.btn_feature(True)
        self.random_trai.setEnabled(True)
        self.show_trai.setReadOnly(False)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading waveforms and features!')

    def show_wave(self, btn):
        self.status = self.show_figurenote.text()
        if not btn.text() or btn.text() == 'This channel has no data.':
            self.statusbar.showMessage('Please enter a TRAI to continue.')
            return
        if self.device == 'VALLEN':
            waveform = Waveform(self.color_1, self.color_2, self.data_tra, self.input, self.output, self.status, 'vallen')
            plotWindow = waveform.plot_wave_TRAI(int(btn.text()), self.data_pri, len(self.data_pri) != 0, valid=False)
            try:
                self.window.append(plotWindow)
                plotWindow.show()
                self.statusbar.showMessage('Wavefrom %s has been shown in new window.' % btn.text())
            except AttributeError:
                self.statusbar.showMessage(plotWindow)
        else:
            try:
                os.chdir(self.output)
            except:
                self.statusbar.showMessage('Error: The save path is empty, please select a correct path!')
                return
            for channel, tra in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'],
                                         [self.data_tra_1, self.data_tra_2, self.data_tra_3, self.data_tra_4]):
                if self.chan == channel:
                    data_tra = tra
            waveform = Waveform(self.color_1, self.color_2, data_tra, self.input, self.output, self.status, 'pac',
                                self.threshold.value(), self.magnification.value())
            plotWindow = waveform.plot_wave_TRAI(int(btn.text()), self.data_pri, len(self.data_pri) != 0, valid=False)
            try:
                self.window.append(plotWindow)
                plotWindow.show()
                self.statusbar.showMessage('Wavefrom %s has been shown in new window.' % btn.text())
            except AttributeError:
                self.statusbar.showMessage(plotWindow)
            del data_tra

    def show_feature(self):
        self.status = self.show_figurenote.text()
        self.upper_time = self.max_time.value()
        self.upper_cnts = self.max_cnts.value()
        if self.max_time.value() == 0:
            self.upper_time = float('inf')
        if self.max_cnts.value() == 0:
            self.upper_cnts = float('inf')
        for name, chan in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'], [self.chan_1, self.chan_2, self.chan_3, self.chan_4]):
            if self.chan == name:
                valid_pri = chan
        if self.device == 'VALLEN':
            feature_idx = [4, 6, 7, 1, -2]
        else:
            feature_idx = [5, 8, 9, 1, -1]
        valid_pri = valid_pri[np.where((valid_pri[:, feature_idx[-2]] >= self.min_time.value()) & (valid_pri[:, feature_idx[-2]] < self.upper_time) &
                                       (valid_pri[:, feature_idx[-1]] >= self.min_cnts.value()) & (valid_pri[:, feature_idx[-1]] < self.upper_cnts))[0]]
        features = Features(self.color_1, self.color_2, valid_pri[:, 1], self.status, self.output)
        # Plot features' correlation
        if self.E_A.isChecked():
            plotWindow = features.plot_correlation(valid_pri[:, feature_idx[0]], valid_pri[:, feature_idx[2]],
                                                   self.xlabelz[0], self.xlabelz[2],
                                                   self.correlation_select_color.currentText())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.E_D.isChecked():
            plotWindow = features.plot_correlation(valid_pri[:, feature_idx[1]], valid_pri[:, feature_idx[2]],
                                                   self.xlabelz[1], self.xlabelz[2],
                                                   self.correlation_select_color.currentText())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.A_D.isChecked():
            plotWindow = features.plot_correlation(valid_pri[:, feature_idx[1]], valid_pri[:, feature_idx[0]],
                                                   self.xlabelz[1], self.xlabelz[0],
                                                   self.correlation_select_color.currentText())
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot PDF of features
        if self.PDF_E.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            plotWindow = features.cal_PDF(sorted(valid_pri[:, feature_idx[2]]), [], [], self.xlabelz[2], 'PDF (E)',
                                          [[self.pdf_start_fit.value(), pdf_end_fit], [], []],
                                          [self.pdf_interv_num.value(), [], []], self.pdf_select_color.currentText().lower(),
                                          self.pdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
            QtWidgets.QApplication.processEvents()
        if self.PDF_A.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            plotWindow = features.cal_PDF(sorted(valid_pri[:, feature_idx[0]]), [], [], self.xlabelz[0], 'PDF (A)',
                                          [[self.pdf_start_fit.value(), pdf_end_fit], [], []],
                                          [self.pdf_interv_num.value(), [], []],
                                          self.pdf_select_color.currentText().lower(),
                                          self.pdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.PDF_D.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            plotWindow = features.cal_PDF(sorted(valid_pri[:, feature_idx[1]]), [], [], self.xlabelz[1], 'PDF (D)',
                                          [[self.pdf_start_fit.value(), pdf_end_fit], [], []],
                                          [self.pdf_interv_num.value(), [], []],
                                          self.pdf_select_color.currentText().lower(),
                                          self.pdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot CCDF of features
        if self.CCDF_E.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            plotWindow = features.cal_CCDF(sorted(valid_pri[:, feature_idx[2]]), [], [], self.xlabelz[2], 'CCDF (E)',
                                           [[self.ccdf_start_fit.value(), ccdf_end_fit], [], []],
                                           self.ccdf_select_color.currentText().lower(),
                                           self.ccdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.CCDF_A.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            plotWindow = features.cal_CCDF(sorted(valid_pri[:, feature_idx[0]]), [], [], self.xlabelz[0], 'CCDF (A)',
                                           [[self.ccdf_start_fit.value(), ccdf_end_fit], [], []],
                                           self.ccdf_select_color.currentText().lower(),
                                           self.ccdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.CCDF_D.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            plotWindow = features.cal_CCDF(sorted(valid_pri[:, feature_idx[1]]), [], [], self.xlabelz[1], 'CCDF (D)',
                                           [[self.ccdf_start_fit.value(), ccdf_end_fit], [], []],
                                           self.ccdf_select_color.currentText().lower(),
                                           self.ccdf_fit.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot ML of features
        if self.ML_E.isChecked():
            plotWindow = features.cal_ML(sorted(valid_pri[:, feature_idx[2]]), [], [], self.xlabelz[2], 'ML (E)',
                                         self.ml_select_color.currentText().lower())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.ML_A.isChecked():
            plotWindow = features.cal_ML(sorted(valid_pri[:, feature_idx[0]]), [], [], self.xlabelz[0], 'ML (A)',
                                         self.ml_select_color.currentText().lower())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.ML_D.isChecked():
            plotWindow = features.cal_ML(sorted(valid_pri[:, feature_idx[1]]), [], [], self.xlabelz[1], 'ML (D)',
                                         self.ml_select_color.currentText().lower())
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot contour of features
        if self.contour_D_E.isChecked():
            plotWindow = features.cal_contour(valid_pri[:, feature_idx[2]], valid_pri[:, feature_idx[1]],
                                              '$20 \log_{10} E(aJ)$', '$20 \log_{10} D(\mu s)$',
                                              [self.contour_x_min.value(), self.contour_x_max.value()],
                                              [self.contour_y_min.value(), self.contour_y_max.value()],
                                              self.contour_x_bin.value(), self.contour_y_bin.value(),
                                              self.contour_method.currentText(),
                                              self.contour_padding.currentText() == str(True),
                                              self.contour_colorbar.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.contour_E_A.isChecked():
            plotWindow = features.cal_contour(valid_pri[:, feature_idx[0]], valid_pri[:, feature_idx[2]],
                                              '$20 \log_{10} A(\mu V)$', '$20 \log_{10} E(aJ)$',
                                              [self.contour_x_min.value(), self.contour_x_max.value()],
                                              [self.contour_y_min.value(), self.contour_y_max.value()],
                                              self.contour_x_bin.value(), self.contour_y_bin.value(),
                                              self.contour_method.currentText(),
                                              self.contour_padding.currentText() == str(True),
                                              self.contour_colorbar.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.contour_D_A.isChecked():
            plotWindow = features.cal_contour(valid_pri[:, feature_idx[0]], valid_pri[:, feature_idx[1]],
                                              '$20 \log_{10} A(\mu V)$', '$20 \log_{10} D(\mu s)$',
                                              [self.contour_x_min.value(), self.contour_x_max.value()],
                                              [self.contour_y_min.value(), self.contour_y_max.value()],
                                              self.contour_x_bin.value(), self.contour_y_bin.value(),
                                              self.contour_method.currentText(),
                                              self.contour_padding.currentText() == str(True),
                                              self.contour_colorbar.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot some laws of features
        if self.bathlaw.isChecked():
            plotWindow = features.cal_BathLaw(valid_pri[:, feature_idx[2]], [], [], 'Mainshock Energy (aJ)',
                                              r'$\mathbf{\Delta}$M', self.bathlaw_interv_num.value(),
                                              self.bathlaw_color.currentText().lower())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.waitingtime.isChecked():
            plotWindow = features.cal_WaitingTime(valid_pri[:, feature_idx[-2]], [], [], r'$\mathbf{\Delta}$t (s)',
                                                  r'P($\mathbf{\Delta}$t)', self.waitingtime_interv_num.value(),
                                                  self.waitingtime_color.currentText().lower())
            self.window.append(plotWindow)
            plotWindow.show()
        if self.omorilaw.isChecked():
            plotWindow = features.cal_OmoriLaw(valid_pri[:, feature_idx[2]], [], [], r'$\mathbf{t-t_{MS}\;(s)}$',
                                               r'$\mathbf{r_{AS}(t-t_{MS})\;(s^{-1})}$',
                                               self.omorilaw_interv_num.value())
            self.window.append(plotWindow)
            plotWindow.show()
        # Plot time domain curves
        if self.E_T.isChecked():
            plotWindow = features.plot_feature_time(valid_pri[:, feature_idx[2]], self.xlabelz[2],
                                                    self.show_ending_time.value(), self.feature_color.currentText(),
                                                    self.stress_color.currentText(), self.bar_width.value(),
                                                    self.stretcher, self.smooth.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.A_T.isChecked():
            plotWindow = features.plot_feature_time(valid_pri[:, feature_idx[0]], self.xlabelz[0],
                                                    self.show_ending_time.value(), self.feature_color.currentText(),
                                                    self.stress_color.currentText(), self.bar_width.value(),
                                                    self.stretcher, self.smooth.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.D_T.isChecked():
            plotWindow = features.plot_feature_time(valid_pri[:, feature_idx[1]], self.xlabelz[1],
                                                    self.show_ending_time.value(), self.feature_color.currentText(),
                                                    self.stress_color.currentText(), self.bar_width.value(),
                                                    self.stretcher, self.smooth.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()
        if self.C_T.isChecked():
            plotWindow = features.plot_feature_time(valid_pri[:, feature_idx[-1]], self.xlabelz[3],
                                                    self.show_ending_time.value(), self.feature_color.currentText(),
                                                    self.stress_color.currentText(), self.bar_width.value(),
                                                    self.stretcher, self.smooth.currentText() == str(True))
            self.window.append(plotWindow)
            plotWindow.show()

    def show_auth(self):
        self.auth_win.setWindowModality(Qt.Qt.ApplicationModal)
        self.auth_win.show()

    def show_info(self):
        self.auth_win.setWindowModality(Qt.Qt.ApplicationModal)
        self.about_win.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win_auth = AuthorizeWindow()
    win_about = AboutWindow()
    win = MainForm(AuthorizeWindow, AboutWindow)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # with open('main.qss', 'r') as f:
    #     style = f.read()
    # win.setStyleSheet(style)
    win.show()
    sys.exit(app.exec_())
