# -*- coding: utf-8 -*-
"""
@version: 2.0
@author: Jonah
@file: __init__.py
@Created time: 2020/12/15 00:00
@Last Modified: 2022/04/04 00:28
"""

from main_auto_progress import Ui_MainWindow
from alone_auth import AuthorizeWindow
from about_info import AboutWindow
from features import *
from utils import Reload, load_stress, smooth_curve, catchError, ShowWaveform
from utils_PAC import ConvertPacData, ReadPacData, ReadPacFeatures, ReadPacDataFeatures
from utils_vallen import ConvertVallenData
from config import config_dict, STDOUT_WRITE_STREAM_CONFIG, STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER
import output_redirection_tools

from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer, QThread, QTime, pyqtSlot
from multiprocessing import freeze_support
from multiprocessing import cpu_count


class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    _startThread = pyqtSignal()
    window = []

    def __init__(self, AuthorizeWindow, AboutWindow):
        super(MainForm, self).__init__()
        self.setupUi(self)
        self.xlabelz = ['Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)', 'Counts']
        self.color_1 = [255 / 255, 0 / 255, 102 / 255]
        self.color_2 = [0 / 255, 136 / 255, 204 / 255]
        self.chan = 'Chan 2'
        self.device = 'VALLEN'
        self.input = None
        self.output = None
        self.status = None
        self.stretcher = None
        self.lower = 2
        self.num = 1
        self.tmp = True
        self.processor = cpu_count()
        self.auth_win = AuthorizeWindow
        self.about_win = AboutWindow

        # Set TRAI to enter only integer
        self.show_trai.setValidator(QtGui.QIntValidator())
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        # self.setFixedSize(self.width(), self.height())

        self.__init_open_save()
        self.__init_help()
        self.__init_device()
        self.__init_channel()
        self.__init_load()
        self.__init_plot()
        self.__init_track()
        self.__init_pac()
        self.__init_filter()

        # std out stream management
        # create console text read thread + receiver object
        self.thread_std_out_queue_listener = QThread()
        self.std_out_text_receiver = config_dict[STDOUT_WRITE_STREAM_CONFIG][STREAM_CONFIG_KEY_QT_QUEUE_RECEIVER]
        # connect receiver object to widget for text update
        self.std_out_text_receiver.queue_std_out_element_received_signal.connect(self.__catch_stdout)
        # attach console text receiver to console text thread
        self.std_out_text_receiver.moveToThread(self.thread_std_out_queue_listener)
        # attach to start / stop methods
        self.thread_std_out_queue_listener.started.connect(self.std_out_text_receiver.run)
        self.thread_std_out_queue_listener.start()

    def __init_open_save(self):
        # Open & Save
        self.actionload.triggered.connect(self.openMsg)
        self.actionOpen.triggered.connect(self.openMsg)
        self.actionSave.triggered.connect(self.ExportMsg)
        self.actionExport.triggered.connect(self.ExportMsg)
        self.actionQuit.triggered.connect(self.quit)

    def quit(self):
        self.close()

    def __init_help(self):
        self.check_for_license.triggered.connect(self.show_auth)
        self.about.triggered.connect(self.show_info)

    def __init_device(self):
        # Select device
        self.feature_idx = [4, 6, 7, 1, -2]
        self.trai_idx = -1
        self.PACData = False
        self.VALLEN.toggled.connect(lambda: self.check_device(self.VALLEN))
        self.PAC.toggled.connect(lambda: self.check_device(self.PAC))

    def __init_channel(self):
        # Select channel
        self.chan1.toggled.connect(lambda: self.check_chan(self.chan1))
        self.chan2.toggled.connect(lambda: self.check_chan(self.chan2))
        self.chan3.toggled.connect(lambda: self.check_chan(self.chan3))
        self.chan4.toggled.connect(lambda: self.check_chan(self.chan4))
        self.chan1_2.toggled.connect(lambda: self.check_chan(self.chan1_2))
        self.chan2_2.toggled.connect(lambda: self.check_chan(self.chan2_2))
        self.chan3_2.toggled.connect(lambda: self.check_chan(self.chan3_2))
        self.chan4_2.toggled.connect(lambda: self.check_chan(self.chan4_2))

    def __init_load(self):
        # Load data from files
        self.import_data.clicked.connect(lambda: self.load_data(self.import_data))
        self.import_data_2.clicked.connect(lambda: self.load_data(self.import_data_2))

    def __init_plot(self):
        # Plot waveform with specific TRAI
        self.random_trai.clicked.connect(lambda: self.random_select(self.chan))
        self.plot_waveform.clicked.connect(lambda: self.show_wave(self.show_trai))
        self.plot_feature.clicked.connect(self.show_feature)

    def __init_track(self):
        self.show_stretcher_data.clicked.connect(self.load_stretcher)
        self.pdf_fit.currentTextChanged.connect(
            lambda: self.check_fit(self.pdf_fit, self.pdf_start_fit, self.pdf_end_fit))
        self.ccdf_fit.currentTextChanged.connect(
            lambda: self.check_fit(self.ccdf_fit, self.ccdf_start_fit, self.ccdf_end_fit))
        self.waitingtime_fit.currentTextChanged.connect(
            lambda: self.check_fit(self.waitingtime_fit, self.waitingtime_start_fit, self.waitingtime_end_fit))

    def __init_pac(self):
        self.threshold.valueChanged.connect(self.check_mode)
        self.magnification.valueChanged.connect(self.check_mode)
        self.counts.valueChanged.connect(self.check_mode)
        self.mode.currentTextChanged.connect(self.check_mode)
        self.Overwrite.clicked.connect(self.check_overwrite)

    def __init_filter(self):
        self.filter.clicked.connect(lambda: self.check_parameter(self.filter))
        self.set_default.clicked.connect(lambda: self.check_parameter(self.set_default))

    def __catch_stdout(self, text: str):
        self.textBrowser.moveCursor(QTextCursor.End)
        self.textBrowser.insertPlainText(text)

    def openMsg(self):
        if self.device == 'VALLEN':
            files = QtWidgets.QFileDialog.getOpenFileNames(self, "Open",
                                                           r"F:\VALLEN\Ni\Ni-tension test-electrolysis-1-0.01-AE-20201031",
                                                           "VALLEN Files (*.pridb & *.tradb)")[0]
            self.input = files
            if len(self.input) == 2 and all(['pridb' in self.input[0] or 'pridb' in self.input[1],
                                             'tradb' in self.input[0] or 'tradb' in self.input[1]]):
                self.show_input.setText(self.input[0].split('/')[-1][:-6])
                self.show_input_2.setText(self.input[0].split('/')[-1][:-6])
                self.import_data.setEnabled(True)
                self.import_data_2.setEnabled(True)
                self.textBrowser.setEnabled(True)
                self.progressBar.setEnabled(True)
                self.statusbar.showMessage('Select loading path successfully!')
                print("=" * 22 + " VALLEN Import Message " + "=" * 22)
                print(self.input[0])
                print(self.input[1])
            else:
                self.statusbar.showMessage('Please select correct files!')
        else:
            file = QtWidgets.QFileDialog.getExistingDirectory(self, "Open",
                                                              "F:/PAC/316L-1.5-z8-0.01-AE-3 sensor-Vallen&PAC-20210302")
            self.input = file
            self.PACData = True if '%s.TXT' % self.input.split('/')[-1] in \
                                   os.listdir(os.path.abspath('/'.join(self.input.split('/')[:-1]))) else False
            print("=" * 23 + " PAC Import Message " + "=" * 23)
            print(self.input)
            print('Load PAC features: %s' % str(self.PACData))
            if self.input:
                self.featuresData = self.input.split('/')[-1] + '.txt'
                self.file_list = os.listdir(self.input)
                if not len(self.file_list):
                    self.statusbar.showMessage('This file is empty!')
                    return
                self.show_input.setEnabled(True)
                self.show_input.setText(self.input)
                self.import_data.setEnabled(True)
                self.import_data_2.setEnabled(True)
                self.textBrowser.setEnabled(True)
                self.progressBar.setEnabled(True)
                self.Overwrite.setChecked(False)
                if self.featuresData in os.listdir(self.input):
                    self.Overwrite.setEnabled(True)
                    self.mode.clear()
                    self.mode.addItems(['Load both', 'Load waveforms only', 'Load features only'])
                    self.statusbar.showMessage(
                        'Please be careful to press the Overwrite button, the original data may be lost.')
                    print("=" * 28 + " Warning " + "=" * 28)
                    print(
                        "Converted data file has been detected. Press button [Overwrite] to choose overwrite it or not.")
                else:
                    self.Overwrite.setEnabled(False)
                    self.mode.clear()
                    self.mode.addItems(['Convert only', 'Convert with waveforms loading',
                                        'Convert with features loading', 'Convert with both loading',
                                        'Load waveforms only'])
                    self.statusbar.showMessage('Press [IMPORT] to continue.')
                    print("=" * 23 + " Convert information " + "=" * 23)
                print(self.input)
                print('Ready to convert data, remember to choose whether to read waveforms and features')
            else:
                self.statusbar.showMessage('Please select correct file!')

    def load_stretcher(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open",
                                                     "F:/VALLEN/Ni-tension test-electrolysis-1-0.01-AE-20201031/Ni-tension test-electrolysis-1-0.01-20201031.is_tens_RawData",
                                                     "csv Files (*.csv)")[0]
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
        if self.input and self.output:
            self.import_data.setEnabled(True)
            self.import_data_2.setEnabled(True)
        else:
            self.statusbar.showMessage('Please select a path to load or save!')
        self.min_cnts.setValue(self.counts.value())

    @catchError('Error In Checking Device')
    def check_device(self, btn):
        if btn.isChecked():
            self.device = btn.objectName()
            if self.device == 'VALLEN':
                self.feature_idx = [4, 6, 7, 1, -2]  # Amp, Dur, Eny, Time, Counts
                self.trai_idx = -1
                self.mode.clear()
                self.mode.addItems(['Load both', 'Load waveforms only', 'Load features only'])
                self.Overwrite.setChecked(False)
                self.Overwrite.setEnabled(False)
                self.Threshold.setEnabled(False)
                self.threshold.setEnabled(False)
                self.Magnification.setEnabled(False)
                self.magnification.setEnabled(False)
            else:
                self.feature_idx = [5, 8, 9, 1, -1]  # Amp, Dur, Eny, Time, Counts
                self.PAC_feature_idx = [6, 5, 4, -1, 0, 3]  # Amp, Dur, Eny, AbsEny, Time, Counts
                self.trai_idx = 0
                self.mode.clear()
                self.mode.addItems(['Convert only', 'Convert with waveforms loading', 'Convert with features loading',
                                    'Convert with both loading'])
                self.Threshold.setEnabled(True)
                self.threshold.setEnabled(True)
                self.Magnification.setEnabled(True)
                self.magnification.setEnabled(True)

            self.import_data.setEnabled(False)
            self.import_data_2.setEnabled(False)

    @catchError('Error In Filtering Data')
    def check_parameter(self, btn):
        self.btn_plot(False)
        for name, chan, pac_chan in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'],
                                        [self.chan_1, self.chan_2, self.chan_3, self.chan_4],
                                        [self.PAC_chan_1, self.PAC_chan_2, self.PAC_chan_3, self.PAC_chan_4]):
            if self.chan == name:
                valid_pri = chan
                PAC_valid_pri = pac_chan
        if not valid_pri.shape[0]:
            self.statusbar.showMessage('Warning: There is no valid wave! Please rectify your filter parameters.')
            return
        if btn.text() == 'Filter':
            self.upper_time = self.max_time.value()
            self.upper_cnts = self.max_cnts.value()
            self.upper_eny = self.max_energy.value()
            self.upper_amp = self.max_amplitude.value()
            self.upper_dur = self.max_duration.value()
            if self.max_time.value() == 0:
                self.upper_time = float('inf')
            if self.max_cnts.value() == 0:
                self.upper_cnts = float('inf')
            if self.max_energy.value() == 0:
                self.upper_eny = float('inf')
            if self.max_amplitude.value() == 0:
                self.upper_amp = float('inf')
            if self.max_duration.value() == 0:
                self.upper_dur = float('inf')
            self.filter_pri = valid_pri[np.where((valid_pri[:, self.feature_idx[-2]] >= self.min_time.value()) &
                                                 (valid_pri[:, self.feature_idx[-2]] < self.upper_time) &
                                                 (valid_pri[:, self.feature_idx[-1]] > self.min_cnts.value()) &
                                                 (valid_pri[:, self.feature_idx[-1]] < self.upper_cnts) &
                                                 (valid_pri[:, self.feature_idx[2]] >= self.min_energy.value()) &
                                                 (valid_pri[:, self.feature_idx[2]] < self.upper_eny) &
                                                 (valid_pri[:, self.feature_idx[0]] >= self.min_amplitude.value()) &
                                                 (valid_pri[:, self.feature_idx[0]] < self.upper_amp) &
                                                 (valid_pri[:, self.feature_idx[1]] >= self.min_duration.value()) &
                                                 (valid_pri[:, self.feature_idx[1]] < self.upper_dur))[0]]
            if self.PACData and self.device == 'PAC':
                self.PAC_filter_pri = PAC_valid_pri[np.where(
                    (PAC_valid_pri[:, self.PAC_feature_idx[-2]] >= self.min_time.value()) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[-2]] < self.upper_time) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[-1]] > self.min_cnts.value()) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[-1]] < self.upper_cnts) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[3]] >= self.min_energy.value()) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[3]] < self.upper_eny) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[0]] >= 20 * np.log10(self.min_amplitude.value())) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[0]] < 20 * np.log10(self.upper_amp)) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[1]] >= self.min_duration.value()) &
                    (PAC_valid_pri[:, self.PAC_feature_idx[1]] < self.upper_dur))[0]]
            self.statusbar.showMessage('Filtering Done! Valid waves: %d' % self.filter_pri.shape[0])
        else:
            self.min_time.setValue(0)
            self.min_cnts.setValue(self.counts.value())
            self.min_energy.setValue(0)
            self.min_amplitude.setValue(0)
            self.min_duration.setValue(0)
            self.max_time.setValue(0)
            self.max_cnts.setValue(0)
            self.max_energy.setValue(0)
            self.max_amplitude.setValue(0)
            self.max_duration.setValue(0)
            self.filter_pri = valid_pri
            self.statusbar.showMessage('Filtering Reset! Valid waves: %d' % self.filter_pri.shape[0])
        del chan, pac_chan, valid_pri, PAC_valid_pri
        self.btn_plot(True)

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
        self.random_trai.setEnabled(status)
        self.chan1.setEnabled(status)
        self.chan2.setEnabled(status)
        self.chan3.setEnabled(status)
        self.chan4.setEnabled(status)
        self.cwt.setEnabled(status)
        self.plot_waveform.setEnabled(status)
        self.show_trai.setEnabled(status)

    def btn_feature(self, status):
        self.chan1_2.setEnabled(status)
        self.chan2_2.setEnabled(status)
        self.chan3_2.setEnabled(status)
        self.chan4_2.setEnabled(status)
        self.min_cnts.setEnabled(status)
        self.max_cnts.setEnabled(status)
        self.min_time.setEnabled(status)
        self.max_time.setEnabled(status)
        self.min_energy.setEnabled(status)
        self.max_energy.setEnabled(status)
        self.min_amplitude.setEnabled(status)
        self.max_amplitude.setEnabled(status)
        self.min_duration.setEnabled(status)
        self.max_duration.setEnabled(status)
        self.filter.setEnabled(status)
        self.set_default.setEnabled(status)

    def btn_plot(self, status):
        # ============================ Plot Button ============================
        self.plot_feature.setEnabled(status)

        # =========================== Feature Curve ===========================
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

        # ================================ PAC ================================
        if (self.device == 'PAC' and self.PACData) or not status:
            self.PAC_E_A.setEnabled(status)
            self.PAC_E_D.setEnabled(status)
            self.PAC_A_D.setEnabled(status)
            self.PAC_AbsE_A.setEnabled(status)
            self.PAC_AbsE_D.setEnabled(status)
            self.PAC_E_T.setEnabled(status)
            self.PAC_AbsE_T.setEnabled(status)
            self.PAC_A_T.setEnabled(status)
            self.PAC_D_T.setEnabled(status)
            self.PAC_C_T.setEnabled(status)

        # ============================= Fitting 1 =============================
        # PDF
        self.pdf_bin_method.setEnabled(status)
        self.pdf_select_color.setEnabled(status)
        self.pdf_fit.setEnabled(status)
        self.pdf_interv_num.setEnabled(status)
        # CCDF
        self.ccdf_select_color.setEnabled(status)
        self.ccdf_fit.setEnabled(status)
        # ML
        self.ml_select_color.setEnabled(status)
        self.ml_select_ecolor.setEnabled(status)
        # Correlation
        self.correlation_select_color.setEnabled(status)

        # ============================= Fitting 2 =============================
        # Waiting Time
        self.waitingtime_bin_method.setEnabled(status)
        self.waitingtime_color.setEnabled(status)
        self.waitingtime_fit.setEnabled(status)
        self.waitingtime_interv_num.setEnabled(status)
        # Omori's Law
        self.omorilaw_bin_method.setEnabled(status)
        self.omorilaw_color.setEnabled(status)
        self.omorilaw_fit.setEnabled(status)
        self.omorilaw_interv_num.setEnabled(status)
        # Bath Law
        self.bathlaw_bin_method.setEnabled(status)
        self.bathlaw_color.setEnabled(status)
        self.bathlaw_interv_num.setEnabled(status)

        # ============================== Others ==============================
        # Contour
        self.contour_method.setEnabled(status)
        self.contour_padding.setEnabled(status)
        self.contour_clabel.setEnabled(status)
        self.contour_colorbar.setEnabled(status)
        self.contour_x_min.setEnabled(status)
        self.contour_x_max.setEnabled(status)
        self.contour_x_bin.setEnabled(status)
        self.contour_y_min.setEnabled(status)
        self.contour_y_max.setEnabled(status)
        self.contour_y_bin.setEnabled(status)
        # Time Domain Curve
        self.bar_width.setEnabled(status)
        self.feature_color.setEnabled(status)
        self.show_ending_time.setEnabled(status)
        self.show_stretcher_data.setEnabled(status)

    @catchError('Error In Loading Data')
    def load_data(self, btn):
        try:
            os.chdir(self.output)
        except:
            self.statusbar.showMessage('Error: The save path is empty, please select a correct path!')
            return

        self.PAC_chan_1, self.PAC_chan_2, self.PAC_chan_3, self.PAC_chan_4 = [], [], [], []
        self.stretcher = None
        if self.device == 'VALLEN':
            if len(self.input) == 1:
                self.statusbar.showMessage('Please select correct files!')
                return
            self.statusbar.clearMessage()
            self.statusbar.showMessage('Loading data...')
            if 'pridb' in self.input[0]:
                self.path_pri = self.input[0]
                self.path_tra = self.input[1]
            else:
                self.path_pri = self.input[1]
                self.path_tra = self.input[0]

            self.btn_base(False)
            self.btn_wave(False)
            self.btn_feature(False)
            self.btn_plot(False)
            self.random_trai.setEnabled(False)
            self.import_data.setEnabled(False)
            self.import_data_2.setEnabled(False)
            self.pdf_start_fit.setEnabled(False)
            self.pdf_end_fit.setEnabled(False)
            self.ccdf_start_fit.setEnabled(False)
            self.ccdf_end_fit.setEnabled(False)
            self.waitingtime_start_fit.setEnabled(False)
            self.waitingtime_end_fit.setEnabled(False)
            self.smooth.setEnabled(False)
            self.stress_color.setEnabled(False)

            self.convertVallen = ConvertVallenData(self.path_pri, self.path_tra, self.input[0].split('/')[-1][:-6],
                                                   self.mode.currentText(), self.counts.value())
            self.thread = QThread(self)  # 初始化QThread子线程

            # 把自定义线程加入到QThread子线程中
            self.convertVallen.moveToThread(self.thread)

            self._startThread.connect(self.convertVallen.run)  # 只能通过信号-槽启动线程处理函数
            self.convertVallen.signal.connect(self.call_vallen_backlog)

            if self.thread.isRunning():  # 如果该线程正在运行，则不再重新启动
                return

            # 先启动QThread子线程
            self.thread.start()
            # 发送信号，启动线程处理函数
            # 不能直接调用，否则会导致线程处理函数和主线程是在同一个线程，同样操作不了主界面
            self._startThread.emit()
        else:
            if len(self.input) == 2:
                self.statusbar.showMessage('Please select correct files!')
                return
            os.chdir(self.input)
            self.btn_base(False)
            self.btn_wave(False)
            self.btn_feature(False)
            self.btn_plot(False)
            self.random_trai.setEnabled(False)
            self.import_data.setEnabled(False)
            self.import_data_2.setEnabled(False)
            self.pdf_start_fit.setEnabled(False)
            self.pdf_end_fit.setEnabled(False)
            self.ccdf_start_fit.setEnabled(False)
            self.ccdf_end_fit.setEnabled(False)
            self.waitingtime_start_fit.setEnabled(False)
            self.waitingtime_end_fit.setEnabled(False)
            self.smooth.setEnabled(False)
            self.stress_color.setEnabled(False)
            self.statusbar.clearMessage()
            self.statusbar.showMessage('Loading data...')
            if self.mode.currentText() == 'Convert only':
                self.thread = ConvertPacData(self.featuresData, self.PACData, self.input, self.threshold.value(),
                                             self.magnification.value(), self.processor, False, False,
                                             self.counts.value())
                self.thread._signal.connect(self.convert_pac_data)
                self.thread.start()
            elif self.mode.currentText() == 'Convert with waveforms loading':
                self.thread = ConvertPacData(self.featuresData, self.PACData, self.input, self.threshold.value(),
                                             self.magnification.value(), self.processor, True, False,
                                             self.counts.value())
                self.thread._signal.connect(self.convert_pac_data)
                self.thread.start()
            elif self.mode.currentText() == 'Convert with features loading':
                self.thread = ConvertPacData(self.featuresData, self.PACData, self.input, self.threshold.value(),
                                             self.magnification.value(), self.processor, False, True,
                                             self.counts.value())
                self.thread._signal.connect(self.convert_pac_data)
                self.thread.start()
            elif self.mode.currentText() == 'Convert with both loading':
                self.thread = ConvertPacData(self.featuresData, self.PACData, self.input, self.threshold.value(),
                                             self.magnification.value(), self.processor, True, True,
                                             self.counts.value())
                self.thread._signal.connect(self.convert_pac_data)
                self.thread.start()
            elif self.mode.currentText() == 'Load both':
                self.thread = ReadPacDataFeatures(self.featuresData, self.PACData, self.file_list, self.input,
                                                  self.threshold.value(), self.magnification.value(), self.processor,
                                                  self.counts.value(), False)
                self.thread._signal.connect(self.read_pac_data_features)
                self.thread.start()
            elif self.mode.currentText() == 'Load waveforms only':
                self.thread = ReadPacData(self.featuresData, self.PACData, self.file_list, self.input,
                                          self.threshold.value(), self.magnification.value(), self.processor,
                                          self.counts.value(), False)
                self.thread._signal.connect(self.return_read_pac_data)
                self.thread.start()
            elif self.mode.currentText() == 'Load features only':
                self.thread = ReadPacFeatures(self.featuresData, self.PACData, self.file_list, self.input,
                                              self.threshold.value(), self.magnification.value(), self.processor,
                                              self.counts.value(), False)
                self.thread._signal.connect(self.return_read_pac_features)
                self.thread.start()

    @catchError('Error In Catching vallen data')
    def call_vallen_backlog(self, result):
        if result[0] in ['tradb', 'pridb']:
            self.progressBar.setValue(int(100 * result[1] / result[2]))
        else:
            self.progressBar.setValue(100)
            self.data_tra = result[0]
            self.data_pri = result[1]
            self.chan_1 = result[2]
            self.chan_2 = result[3]
            self.chan_3 = result[4]
            self.chan_4 = result[5]
            if self.mode == 'Load both' or self.mode == 'Load waveforms only':
                print("Waveform Info--All channel: %d" % len(self.data_tra))
            if self.mode == 'Load both' or self.mode == 'Load features only':
                # print("Features Info--All channel: %d" % self.data_pri.shape[0])
                print("Features Info--All channel: %d | Channel 1: %d | Channel 2: %d | Channel 3: %d | Channel 4: %d" %
                      (self.data_pri.shape[0], chan_1.shape[0], chan_2.shape[0], chan_3.shape[0], chan_4.shape[0]))

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
            self.progressBar.setEnabled(False)
            self.thread.terminate()
            self.thread.quit()

    @catchError('Error in Random Selection')
    def random_select(self, btn):
        for channel, chan in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'],
                                 [self.chan_1, self.chan_2, self.chan_3, self.chan_4]):
            if btn == channel:
                cur_chan = chan
            QtWidgets.QApplication.processEvents()
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

    @catchError('Error In Reading Vallen Data')
    def return_read_vallen_data(self, result):
        self.data_tra = result[0]
        self.data_pri = result[1]
        self.chan_1 = result[2]
        self.chan_2 = result[3]
        self.chan_3 = result[4]
        self.chan_4 = result[5]
        del result

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

    @catchError('Error In Reading PAC Data')
    def return_read_pac_data(self, result):
        self.data_tra_1 = result[0]
        self.data_tra_2 = result[1]
        self.data_tra_3 = result[2]
        self.data_tra_4 = result[3]
        self.PAC_chan_1 = result[-4]
        self.PAC_chan_2 = result[-3]
        self.PAC_chan_3 = result[-2]
        self.PAC_chan_4 = result[-1]
        del result
        self.btn_base(True)
        self.btn_wave(True)
        self.show_trai.setReadOnly(False)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading waveforms!')

    @catchError('Error In Reading PAC Features')
    def return_read_pac_features(self, result):
        self.data_pri = result[0]
        self.chan_1 = result[1]
        self.chan_2 = result[2]
        self.chan_3 = result[3]
        self.chan_4 = result[4]
        self.PAC_chan_1 = result[-4]
        self.PAC_chan_2 = result[-3]
        self.PAC_chan_3 = result[-2]
        self.PAC_chan_4 = result[-1]
        del result
        self.show_input_2.setText(self.featuresData)
        self.btn_base(True)
        self.btn_feature(True)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading features!')

    @catchError('Error In Converting PAC Data')
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
        self.PAC_chan_1 = result[-6]
        self.PAC_chan_2 = result[-5]
        self.PAC_chan_3 = result[-4]
        self.PAC_chan_4 = result[-3]
        if result[-2] and not result[-1]:
            self.btn_wave(True)
            self.show_trai.setReadOnly(False)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading waveforms!')
        elif not result[-2] and result[-1]:
            self.show_input_2.setText(self.featuresData)
            self.btn_feature(True)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading features!')
        elif result[-2] and result[-1]:
            self.show_input_2.setText(self.featuresData)
            self.btn_wave(True)
            self.btn_feature(True)
            self.random_trai.setEnabled(True)
            self.show_trai.setReadOnly(False)
            self.show_figurenote.setReadOnly(False)
            self.statusbar.showMessage('Finish converting and loading both!')
        else:
            self.show_figurenote.setEnabled(False)
            self.statusbar.showMessage('Finish converting!')
        self.btn_base(True)
        del result

    @catchError('Error In Reading PAC Data and Features')
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
        self.PAC_chan_1 = result[-4]
        self.PAC_chan_2 = result[-3]
        self.PAC_chan_3 = result[-2]
        self.PAC_chan_4 = result[-1]
        self.show_input_2.setText(self.featuresData)
        self.btn_base(True)
        self.btn_wave(True)
        self.btn_feature(True)
        self.random_trai.setEnabled(True)
        self.show_trai.setReadOnly(False)
        self.show_figurenote.setReadOnly(False)
        self.statusbar.showMessage('Finish loading waveforms and features!')

    @catchError('Error In Showing plotWindow')
    def return_trai(self, result):
        trai = result
        self.statusbar.showMessage('Wavefrom %i has been shown in new window.' % trai)

    @catchError('Error In Ploting Waveform')
    def show_wave(self, btn):
        self.status = self.show_figurenote.text()
        if not btn.text() or btn.text() == 'This channel has no data.':
            self.statusbar.showMessage('Please enter a TRAI to continue.')
            return

        # ===================================== 新建窗口变量需转换为类变量，否则闪退 ======================================
        self.plotWindow = PlotWindow(f'Waveform--TRAI: {int(btn.text())}',
                                     [9.2, 3] if self.cwt.isChecked() else [6, 3.6])
        self.fig = self.plotWindow.static_canvas.figure

        # ========================== 此行代码用于存储已经展示的窗口，若注释掉则会使用上一次的窗口绘图 ==========================
        self.window.append(self.plotWindow)
        self.plotWindow.show()

        if self.device == 'VALLEN':
            self.showWaveform = ShowWaveform(self.fig, int(btn.text()), self.data_pri, False,
                                             self.cwt.isChecked(), self.color_1, self.color_2, self.data_tra,
                                             self.input, self.output, self.status, 'vallen')
        else:
            for channel, tra in zip(['Chan 1', 'Chan 2', 'Chan 3', 'Chan 4'],
                                    [self.data_tra_1, self.data_tra_2, self.data_tra_3, self.data_tra_4]):
                if self.chan == channel:
                    data_tra = tra

            self.showWaveform = ShowWaveform(self.fig, int(btn.text()), self.data_pri, False, self.cwt.isChecked(),
                                             self.color_1, self.color_2, data_tra, self.input, self.output, self.status,
                                             'pac', self.threshold.value(), self.magnification.value())

        self.showWaveform._signal.connect(self.return_trai)
        self.showWaveform.start()

    @catchError('Error In Ploting Features')
    def show_feature(self, useless=False):
        self.status = self.show_figurenote.text()
        features = Features(self.color_1, self.color_2, self.filter_pri[:, self.feature_idx[-2]],
                            self.filter_pri[:, self.trai_idx], self.status, self.output, self.device)
        # ----------------------------------------- Plot features' correlation -----------------------------------------
        if self.E_A.isChecked():
            self.plotWindow = PlotWindow(f'Correlation--{self.xlabelz[2]} & {self.xlabelz[0]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_E_A = ShowFeaturesCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[0]],
                                                    self.filter_pri[:, self.feature_idx[2]], self.xlabelz[0],
                                                    self.xlabelz[2], self.correlation_select_color.currentText())
            self.show_E_A.start()
        if self.E_D.isChecked():
            self.plotWindow = PlotWindow(f'Correlation--{self.xlabelz[2]} & {self.xlabelz[1]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_E_D = ShowFeaturesCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[1]],
                                                    self.filter_pri[:, self.feature_idx[2]], self.xlabelz[1],
                                                    self.xlabelz[2], self.correlation_select_color.currentText())
            self.show_E_D.start()
        if self.A_D.isChecked():
            self.plotWindow = PlotWindow(f'Correlation--{self.xlabelz[0]} & {self.xlabelz[1]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_A_D = ShowFeaturesCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[1]],
                                                    self.filter_pri[:, self.feature_idx[0]], self.xlabelz[1],
                                                    self.xlabelz[0], self.correlation_select_color.currentText())
            self.show_A_D.start()

        # -------------------------------------------- Plot PDF of features --------------------------------------------
        if self.PDF_E.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            self.plotWindow = PlotWindow(f'PDF--{self.xlabelz[2]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_PDF_E = ShowPDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[2]]),
                                      self.xlabelz[2], 'PDF (E)', [self.pdf_start_fit.value(), pdf_end_fit],
                                      self.pdf_interv_num.value(), self.pdf_select_color.currentText().lower(),
                                      self.pdf_fit.currentText() == str(True),
                                      self.pdf_bin_method.currentText().lower())
            self.show_PDF_E.start()
        if self.PDF_A.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            self.plotWindow = PlotWindow(f'PDF--{self.xlabelz[0]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_PDF_A = ShowPDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[0]]),
                                      self.xlabelz[0], 'PDF (A)', [self.pdf_start_fit.value(), pdf_end_fit],
                                      self.pdf_interv_num.value(), self.pdf_select_color.currentText().lower(),
                                      self.pdf_fit.currentText() == str(True),
                                      self.pdf_bin_method.currentText().lower())
            self.show_PDF_A.start()
        if self.PDF_D.isChecked():
            pdf_end_fit = self.pdf_end_fit.value()
            if self.pdf_end_fit.value() == -100:
                pdf_end_fit = None
            self.plotWindow = PlotWindow(f'PDF--{self.xlabelz[1]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_PDF_A = ShowPDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[1]]),
                                      self.xlabelz[1], 'PDF (D)', [self.pdf_start_fit.value(), pdf_end_fit],
                                      self.pdf_interv_num.value(), self.pdf_select_color.currentText().lower(),
                                      self.pdf_fit.currentText() == str(True),
                                      self.pdf_bin_method.currentText().lower())
            self.show_PDF_A.start()

        # -------------------------------------------- Plot CCDF of features -------------------------------------------
        if self.CCDF_E.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            self.plotWindow = PlotWindow(f'CCDF--{self.xlabelz[2]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_CCDF_E = ShowCCDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[2]]),
                                        self.xlabelz[2], 'CCDF (E)', [self.ccdf_start_fit.value(), ccdf_end_fit],
                                        self.ccdf_select_color.currentText().lower(),
                                        self.ccdf_fit.currentText() == str(True))
            self.show_CCDF_E.start()
        if self.CCDF_A.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            self.plotWindow = PlotWindow(f'CCDF--{self.xlabelz[0]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_CCDF_A = ShowCCDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[0]]),
                                        self.xlabelz[0], 'CCDF (A)', [self.ccdf_start_fit.value(), ccdf_end_fit],
                                        self.ccdf_select_color.currentText().lower(),
                                        self.ccdf_fit.currentText() == str(True))
            self.show_CCDF_A.start()
        if self.CCDF_D.isChecked():
            ccdf_end_fit = self.ccdf_end_fit.value()
            if self.ccdf_end_fit.value() == 0:
                ccdf_end_fit = float('inf')
            self.plotWindow = PlotWindow(f'CCDF--{self.xlabelz[1]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_CCDF_D = ShowCCDF(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[1]]),
                                        self.xlabelz[1], 'CCDF (D)', [self.ccdf_start_fit.value(), ccdf_end_fit],
                                        self.ccdf_select_color.currentText().lower(),
                                        self.ccdf_fit.currentText() == str(True))
            self.show_CCDF_D.start()

        # --------------------------------------------- Plot ML of features --------------------------------------------
        if self.ML_E.isChecked():
            self.plotWindow = PlotWindow(f'ML--{self.xlabelz[2]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_ML_E = ShowML(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[2]]),
                                      self.xlabelz[2], 'ML (E)', self.ml_select_color.currentText().lower(),
                                      self.ml_select_ecolor.currentText().lower())
            self.show_ML_E.start()
        if self.ML_A.isChecked():
            self.plotWindow = PlotWindow(f'ML--{self.xlabelz[0]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_ML_E = ShowML(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[0]]),
                                      self.xlabelz[0], 'ML (A)', self.ml_select_color.currentText().lower(),
                                      self.ml_select_ecolor.currentText().lower())
            self.show_ML_E.start()
        if self.ML_D.isChecked():
            self.plotWindow = PlotWindow(f'ML--{self.xlabelz[1]}', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_ML_E = ShowML(self.fig, features, sorted(self.filter_pri[:, self.feature_idx[1]]),
                                      self.xlabelz[1], 'ML (D)', self.ml_select_color.currentText().lower(),
                                      self.ml_select_ecolor.currentText().lower())
            self.show_ML_E.start()

        # ------------------------------------------ Plot contour of features ------------------------------------------
        if self.contour_D_E.isChecked():
            self.plotWindow = PlotWindow(f'Contour--Duration & Energy', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_contour_D_E = ShowContour(self.fig, features, self.filter_pri[:, self.feature_idx[2]],
                                                self.filter_pri[:, self.feature_idx[1]],
                                                '$20 \log_{10} E(aJ)$', '$20 \log_{10} D(\mu s)$',
                                                [self.contour_x_min.value(), self.contour_x_max.value()],
                                                [self.contour_y_min.value(), self.contour_y_max.value()],
                                                self.contour_x_bin.value(), self.contour_y_bin.value(),
                                                self.contour_method.currentText(),
                                                self.contour_padding.currentText() == str(True),
                                                self.contour_colorbar.currentText() == str(True),
                                                self.contour_clabel.currentText() == str(True))
            self.show_contour_D_E.start()
        if self.contour_E_A.isChecked():
            self.plotWindow = PlotWindow(f'Contour--Energy & Amplitude', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_contour_E_A = ShowContour(self.fig, features, self.filter_pri[:, self.feature_idx[0]],
                                                self.filter_pri[:, self.feature_idx[2]],
                                                '$20 \log_{10} A(\mu V)$', '$20 \log_{10} E(aJ)$',
                                                [self.contour_x_min.value(), self.contour_x_max.value()],
                                                [self.contour_y_min.value(), self.contour_y_max.value()],
                                                self.contour_x_bin.value(), self.contour_y_bin.value(),
                                                self.contour_method.currentText(),
                                                self.contour_padding.currentText() == str(True),
                                                self.contour_colorbar.currentText() == str(True),
                                                self.contour_clabel.currentText() == str(True))
            self.show_contour_E_A.start()
        if self.contour_D_A.isChecked():
            self.plotWindow = PlotWindow(f'Contour--Duration & Amplitude', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_contour_D_A = ShowContour(self.fig, features, self.filter_pri[:, self.feature_idx[0]],
                                                self.filter_pri[:, self.feature_idx[1]],
                                                '$20 \log_{10} A(\mu V)$', '$20 \log_{10} D(\mu s)$',
                                                [self.contour_x_min.value(), self.contour_x_max.value()],
                                                [self.contour_y_min.value(), self.contour_y_max.value()],
                                                self.contour_x_bin.value(), self.contour_y_bin.value(),
                                                self.contour_method.currentText(),
                                                self.contour_padding.currentText() == str(True),
                                                self.contour_colorbar.currentText() == str(True),
                                                self.contour_clabel.currentText() == str(True))
            self.show_contour_D_A.start()

        # ----------------------------------------------- Plot bath law ------------------------------------------------
        # Plot some laws of features
        if self.bathlaw.isChecked():
            self.plotWindow = PlotWindow('Bath law', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_bathlaw = ShowBathLaw(self.fig, features, self.filter_pri[:, self.feature_idx[2]],
                                            'Mainshock Energy (aJ)', r'$\mathbf{\Delta}$M',
                                            self.bathlaw_interv_num.value(), self.bathlaw_color.currentText().lower(),
                                            self.bathlaw_bin_method.currentText().lower())
            self.show_bathlaw.start()

        # --------------------------------------------- Plot waiting time ----------------------------------------------
        if self.waitingtime.isChecked():
            waitingTime_end_fit = self.waitingtime_end_fit.value()
            if self.waitingtime_end_fit.value() == -100:
                waitingTime_end_fit = None
            self.plotWindow = PlotWindow('Distribution of waiting time', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_waitingtime = ShowWaitingTime(self.fig, features, self.filter_pri[:, self.feature_idx[-2]],
                                                    r'$\mathbf{\Delta}$t (s)', r'P($\mathbf{\Delta}$t)',
                                                    self.waitingtime_interv_num.value(),
                                                    self.waitingtime_color.currentText().lower(),
                                                    self.waitingtime_fit.currentText() == str(True),
                                                    [self.waitingtime_start_fit.value(), waitingTime_end_fit],
                                                    self.waitingtime_bin_method.currentText().lower())
            self.show_waitingtime.start()

        # ---------------------------------------------- Plot omori's law ----------------------------------------------
        if self.omorilaw.isChecked():
            self.plotWindow = PlotWindow("Omori's law", [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_omorilaw = ShowOmoriLaw(self.fig, features, self.filter_pri[:, self.feature_idx[2]],
                                              r'$\mathbf{t-t_{MS}\;(s)}$', r'$\mathbf{r_{AS}(t-t_{MS})\;(s^{-1})}$',
                                              self.omorilaw_interv_num.value(),
                                              self.omorilaw_fit.currentText() == str(True),
                                              self.omorilaw_bin_method.currentText().lower())
            self.show_omorilaw.start()

        # ------------------------------------------ Plot time domain curves -------------------------------------------
        if self.E_T.isChecked():
            self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_E_T = ShowTimeCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[2]],
                                                self.xlabelz[2], self.show_ending_time.value(),
                                                self.feature_color.currentText(), self.stress_color.currentText(),
                                                self.bar_width.value(), self.stretcher,
                                                self.smooth.currentText() == str(True))
            self.show_E_T.start()
        if self.A_T.isChecked():
            self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_A_T = ShowTimeCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[0]],
                                                self.xlabelz[0], self.show_ending_time.value(),
                                                self.feature_color.currentText(), self.stress_color.currentText(),
                                                self.bar_width.value(), self.stretcher,
                                                self.smooth.currentText() == str(True))
            self.show_A_T.start()
        if self.D_T.isChecked():
            self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_D_T = ShowTimeCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[1]],
                                                self.xlabelz[1], self.show_ending_time.value(),
                                                self.feature_color.currentText(), self.stress_color.currentText(),
                                                self.bar_width.value(), self.stretcher,
                                                self.smooth.currentText() == str(True))
            self.show_D_T.start()
        if self.C_T.isChecked():
            self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
            self.fig = self.plotWindow.static_canvas.figure
            self.window.append(self.plotWindow)
            self.plotWindow.show()
            self.show_C_T = ShowTimeCorrelation(self.fig, features, self.filter_pri[:, self.feature_idx[-1]],
                                                self.xlabelz[3], self.show_ending_time.value(),
                                                self.feature_color.currentText(), self.stress_color.currentText(),
                                                self.bar_width.value(), self.stretcher,
                                                self.smooth.currentText() == str(True))
            self.show_C_T.start()

        # ==================================================== PAC =====================================================
        if self.device == 'PAC':
            features = Features(self.color_1, self.color_2, self.PAC_filter_pri[:, self.PAC_feature_idx[-2]],
                                self.PAC_filter_pri[:, self.trai_idx], self.status, self.output, 'PAC-self')

            # -------------------------------------- Plot features' correlation ----------------------------------------
            if self.PAC_E_A.isChecked():
                self.plotWindow = PlotWindow('Correlation--20log(Eny) & 20log(Amp)', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_E_A = ShowFeaturesCorrelation(self.fig, features,
                                                            self.PAC_filter_pri[:, self.PAC_feature_idx[0]],
                                                            self.PAC_filter_pri[:, self.PAC_feature_idx[2]],
                                                            '20log(Amp)', '20log(Eny)',
                                                            self.correlation_select_color.currentText())
                self.show_PAC_E_A.start()
            if self.PAC_E_D.isChecked():
                self.plotWindow = PlotWindow('Correlation--20log(Eny) & 20log(Dur)', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_E_D = ShowFeaturesCorrelation(self.fig, features,
                                                            20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[1]]),
                                                            self.PAC_filter_pri[:, self.PAC_feature_idx[2]],
                                                            '20log(Dur)', '20log(Eny)',
                                                            self.correlation_select_color.currentText())
                self.show_PAC_E_D.start()
            if self.PAC_A_D.isChecked():
                self.plotWindow = PlotWindow('Correlation--20log(Amp) & 20log(Dur)', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_A_D = ShowFeaturesCorrelation(self.fig, features,
                                                            20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[1]]),
                                                            self.PAC_filter_pri[:, self.PAC_feature_idx[0]],
                                                            '20log(Dur)', '20log(Amp)',
                                                            self.correlation_select_color.currentText())
                self.show_PAC_A_D.start()
            if self.PAC_AbsE_A.isChecked():
                self.plotWindow = PlotWindow('Correlation--20log(AbsEny) & 20log(Amp)', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_AbsE_A = ShowFeaturesCorrelation(self.fig, features,
                                                               self.PAC_filter_pri[:, self.PAC_feature_idx[0]],
                                                               20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[3]]),
                                                               '20log(Amp)', '20log(AbsEny)',
                                                               self.correlation_select_color.currentText())
                self.show_PAC_AbsE_A.start()
            if self.PAC_AbsE_D.isChecked():
                self.plotWindow = PlotWindow('Correlation--20log(AbsEny) & 20log(Dur)', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_AbsE_D = ShowFeaturesCorrelation(self.fig, features,
                                                               20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[1]]),
                                                               20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[3]]),
                                                               '20log(Dur)', '20log(AbsEny)',
                                                               self.correlation_select_color.currentText())
                self.show_PAC_AbsE_D.start()

            # --------------------------------------- Plot time domain curves ------------------------------------------
            if self.PAC_E_T.isChecked():
                self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_E_T = ShowTimeCorrelation(self.fig, features,
                                                        self.PAC_filter_pri[:, self.PAC_feature_idx[2]], '20log(Eny)',
                                                        self.show_ending_time.value(), self.feature_color.currentText(),
                                                        self.stress_color.currentText(), self.bar_width.value(),
                                                        self.stretcher, self.smooth.currentText() == str(True))
                self.show_PAC_E_T.start()
            if self.PAC_AbsE_T.isChecked():
                self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_AbsE_T = ShowTimeCorrelation(self.fig, features,
                                                           20*np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[3]]),
                                                           '20log(AbsEny)', self.show_ending_time.value(),
                                                           self.feature_color.currentText(),
                                                           self.stress_color.currentText(),
                                                           self.bar_width.value(), self.stretcher,
                                                           self.smooth.currentText() == str(True))
                self.show_PAC_AbsE_T.start()
            if self.PAC_A_T.isChecked():
                self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_A_T = ShowTimeCorrelation(self.fig, features,
                                                        self.PAC_filter_pri[:, self.PAC_feature_idx[0]], '20log(Amp)',
                                                        self.show_ending_time.value(), self.feature_color.currentText(),
                                                        self.stress_color.currentText(), self.bar_width.value(),
                                                        self.stretcher, self.smooth.currentText() == str(True))
                self.show_PAC_A_T.start()
            if self.PAC_D_T.isChecked():
                self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_D_T = ShowTimeCorrelation(self.fig, features,
                                                        20 * np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[1]]),
                                                        '20log(Dur)', self.show_ending_time.value(),
                                                        self.feature_color.currentText(),
                                                        self.stress_color.currentText(),
                                                        self.bar_width.value(), self.stretcher,
                                                        self.smooth.currentText() == str(True))
                self.show_PAC_D_T.start()
            if self.PAC_C_T.isChecked():
                self.plotWindow = PlotWindow('Time Domain Curve', [6, 3.9])
                self.fig = self.plotWindow.static_canvas.figure
                self.window.append(self.plotWindow)
                self.plotWindow.show()
                self.show_PAC_C_T = ShowTimeCorrelation(self.fig, features,
                                                        20 * np.log10(self.PAC_filter_pri[:, self.PAC_feature_idx[-1]]),
                                                        '20log(Counts)', self.show_ending_time.value(),
                                                        self.feature_color.currentText(),
                                                        self.stress_color.currentText(),
                                                        self.bar_width.value(), self.stretcher,
                                                        self.smooth.currentText() == str(True))
                self.show_PAC_C_T.start()

    @catchError('Error In Showing Authorization Window')
    def show_auth(self):
        self.auth_win.setWindowModality(Qt.Qt.ApplicationModal)
        self.auth_win.show()

    @catchError('Error In Showing Information Window')
    def show_info(self):
        self.auth_win.setWindowModality(Qt.Qt.ApplicationModal)
        self.about_win.show()


if __name__ == "__main__":
    import sys

    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    win_auth = AuthorizeWindow()
    win_about = AboutWindow()
    win_main = MainForm(win_auth, win_about)
    # win = AuthWindow(win_main)
    win_main.show()
    sys.exit(app.exec_())
