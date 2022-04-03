"""
@version: 2.0
@author: Jonah
@file: wave_freq.py
@Created time: 2020/12/15 00:00
@Last Modified: 2022/04/04 00:28
"""

from plot_format import plot_norm
from ssqueezepy import ssq_cwt
from scipy.fftpack import fft
import array
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from pac import Preprocessing
from plotwindow import PlotWindow


class Waveform:
    def __init__(self, color_1, color_2, data_tra, input, output, status, device, thr_dB=25, magnification_dB=60):
        self.data_tra = data_tra
        self.input = input
        self.output = output
        self.color_1 = color_1
        self.color_2 = color_2
        self.status = status
        self.device = device
        self.thr_μV = pow(10, thr_dB / 20)
        self.process = Preprocessing(None, thr_dB, magnification_dB, input, None)

    def cal_wave(self, i, valid=True):
        if self.device == 'vallen':
            # Time, Chan, Thr, SampleRate, Samples, TR_mV, Data, TRAI
            sig = np.multiply(array.array('h', bytes(i[-2])), i[-3] * 1000)
            time = np.linspace(0, pow(i[-5], -1) * (i[-4] - 1) * pow(10, 6), i[-4])
            thr = i[2]
            if valid:
                valid_wave_idx = np.where(abs(sig) >= thr)[0]
                start = time[valid_wave_idx[0]]
                end = time[valid_wave_idx[-1]]
                duration = end - start
                sig = sig[valid_wave_idx[0]:(valid_wave_idx[-1] + 1)]
                time = np.linspace(0, duration, sig.shape[0])
        elif self.device == 'pac':
            sig = i[-2]
            time = np.linspace(0, i[2] * (i[-3] - 1) * pow(10, 6), i[-3])
            if valid:
                valid_wave_idx = np.where(abs(sig) >= self.thr_μV)[0]
                start = time[valid_wave_idx[0]]
                end = time[valid_wave_idx[-1]]
                duration = end - start
                sig = sig[valid_wave_idx[0]:(valid_wave_idx[-1] + 1)]
                time = np.linspace(0, duration, sig.shape[0])
        return time, sig

    def plot_wave_TRAI(self, fig, k, data_pri, show_features=False, valid=False, cwt=False):
        # Waveform with specific TRAI
        try:
            if self.device == 'VALLEN':
                i = self.data_tra[k - 1]
            else:
                i = self.data_tra[k - self.data_tra[0][-1]]
        except IndexError:
            return str('Error: TRAI %d can not be found in data!' % k)
        if i[-1] != k:
            return str('Error: TRAI %d in data_tra is inconsistent with %d by input!' % (i[-1], k))
        time, sig = self.cal_wave(i, valid=valid)
        for tmp_tail, s in enumerate(sig[::-1]):
            if s != 0:
                tail = -tmp_tail if tmp_tail > 0 else None
                break
        time, sig = time[:tail], sig[:tail]

        if cwt:
            fig.subplots_adjust(left=0.076, bottom=0.205, right=0.984, top=0.927, hspace=0.2, wspace=0.26)
            fig.text(0.47, 0.25, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
            ax = fig.add_subplot(1, 2, 2)
            ax.cla()
            Twxo, Wxo, ssq_freqs, *_ = ssq_cwt(sig, wavelet='morlet', scales='log-piecewise', fs=i[3], t=time)
            ax.contourf(time, ssq_freqs * 1000, pow(abs(Twxo), 0.5), cmap='cubehelix_r')
            plot_norm(ax, 'Time (μs)', 'Frequency (kHz)', y_lim=[min(ssq_freqs * 1000), 1000], legend=False)
            ax = fig.add_subplot(1, 2, 1)
            ax.cla()
            ax.plot(time, sig, lw=1)
        else:
            fig.subplots_adjust(left=0.115, bottom=0.17, right=0.975, top=0.95)
            fig.text(0.96, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
            ax = fig.add_subplot()
            ax.cla()
            ax.plot(time, sig, lw=1)

        if self.device == 'vallen':
            if show_features:
                try:
                    string = data_pri[np.where(data_pri[:, -1] == i[-1])][0]
                except IndexError:
                    return str('Error: TRAI %d can not be found in data!' % k)
                print("=" * 23 + " Waveform information " + "=" * 23)
                for info, value, r in zip(
                        ['SetID', 'Time', 'Chan', 'Thr', 'Amp', 'RiseT', 'Dur', 'Eny', 'RMS', 'Counts', 'TRAI'],
                        [j for j in string], [0, 8, 0, 8, 8, 2, 2, 8, 8, 0, 0]):
                    if r == 0:
                        print('%s: %d' % (info, int(value)))
                    else:
                        print('%s: %s' % (info, round(value, r)))
            ax.axhline(abs(i[2]), 0, sig.shape[0], linewidth=1, color="black")
            ax.axhline(-abs(i[2]), 0, sig.shape[0], linewidth=1, color="black")
        elif self.device == 'pac':
            if show_features:
                # time, channel_num, sample_interval, points_num, dataset, hit_num
                # ID, Time(s), Chan, Thr(μV), Thr(dB), Amp(μV), Amp(dB), RiseT(s), Dur(s), Eny(aJ), RMS(μV), Frequency(Hz), Counts
                string = data_pri[np.where(data_pri[:, 0] == i[-1])][0]
                print("=" * 23 + " Waveform information " + "=" * 23)
                for info, value, r in zip(
                        ['Hit number', 'Time', 'Chan', 'Thr', 'Amp', 'RiseT', 'Dur', 'Eny', 'RMS', 'Counts'],
                        [j for j in string[np.array([0, 1, 2, 3, 5, 7, 8, 9, 10, 12])]], [0, 7, 0, 8, 8, 7, 7, 8, 8, 0]):
                    if r == 0:
                        print('%s: %d' % (info, int(value)))
                    else:
                        print('%s: %s' % (info, round(value, r)))
            ax.axhline(abs(self.thr_μV), 0, sig.shape[0], linewidth=1, color="black")
            ax.axhline(-abs(self.thr_μV), 0, sig.shape[0], linewidth=1, color="black")
        plot_norm(ax, 'Time (μs)', 'Amplitude (μV)', legend=False, grid=True)

        # ================================================= 画图重绘与刷新 ================================================
        fig.canvas.draw()
        fig.canvas.flush_events()

        with open('/'.join([self.output, self.status]) + '-%d' % i[-1] + '.txt', 'w') as f:
            f.write('Time, Signal\n')
            for k in range(sig.shape[0]):
                f.write("{}, {}\n".format(time[k], sig[k]))


class Frequency:
    def __init__(self, color_1, color_2, data_tra, path, path_pri, status, device, thr_dB=25, size=500):
        self.data_tra = data_tra
        self.waveform = Waveform(color_1, color_2, data_tra, path, path_pri, status, device, thr_dB)
        self.size = size
        self.grid = np.linspace(0, pow(10, 6), self.size)
        self.status = status
        self.device = device
        self.thr = pow(10, thr_dB / 20)

    def cal_frequency(self, k, valid=True):
        if self.device == 'vallen':
            i = self.data_tra[k]
            sig = np.multiply(array.array('h', bytes(i[-2])), i[-3] * 1000)
            thr, Fs = i[2], i[3]
            # Ts = 1 / Fs
            if valid:
                valid_wave_idx = np.where(abs(sig) >= thr)[0]
                sig = sig[valid_wave_idx[0]:(valid_wave_idx[-1] + 1)]
        elif self.device == 'pac':
            i = self.data_tra[k]
            Fs = 1 / i[2]
            sig = i[-2]
            if valid:
                valid_wave_idx = np.where(abs(sig) >= self.thr)[0]
                sig = sig[valid_wave_idx[0]:(valid_wave_idx[-1] + 1)]
        N = sig.shape[0]
        fft_y = fft(sig)
        abs_y = np.abs(fft_y)
        normalization = abs_y / N
        normalization_half = normalization[range(int(N / 2))]
        frq = (np.arange(N) / N) * Fs
        half_frq = frq[range(int(N / 2))]
        return half_frq, normalization_half

    def cal_ave_freq(self, TRAI):
        Res = np.array([0 for _ in range(self.size)]).astype('float64')

        for j in TRAI:
            half_frq, normalization_half = self.cal_frequency(j - 1, valid=False)
            valid_idx = int((pow(10, 6) / max(half_frq)) * half_frq.shape[0])
            tmp = [0 for _ in range(self.size)]
            i = 1
            for j, k in zip(half_frq[:valid_idx], normalization_half[:valid_idx]):
                while True:
                    if self.grid[i - 1] <= j < self.grid[i]:
                        tmp[i - 1] += k
                        break
                    i += 1
            Res += np.array(tmp)
        return Res

    def plot_wave_frequency(self, TRAI_select, pop):
        fig = plt.figure(figsize=(6.5, 10), num='Waveform & Frequency--pop%s' % pop)
        for idx, j in enumerate(TRAI_select):
            i = self.data_tra[j - 1]
            valid_time, valid_data = self.waveform.cal_wave(i, valid=False)
            half_frq, normalization_half = self.cal_frequency(j - 1, valid=False)

            ax = fig.add_subplot(5, 2, 1 + idx * 2)
            ax.plot(valid_time, valid_data)
            ax.axhline(abs(i[2]), 0, valid_data.shape[0], linewidth=1, color="black")
            ax.axhline(-abs(i[2]), 0, valid_data.shape[0], linewidth=1, color="black")
            plot_norm(ax, 'Time (μs)', 'Amplitude (μV)', legend=False, grid=True)

            ax = fig.add_subplot(5, 2, 2 + idx * 2)
            ax.plot(half_frq, normalization_half)
            plot_norm(ax, 'Freq (Hz)', '|Y(freq)|', x_lim=[0, pow(10, 6)], legend=False)

    def plot_ave_freq(self, Res, N, title):
        fig = plt.figure(figsize=(6, 4.1), num='Average Frequency--%s' % title)
        ax = fig.add_subplot()
        ax.plot(self.grid, Res / N)
        plot_norm(ax, xlabel='Freq (Hz)', ylabel='|Y(freq)|', title='Average Frequency', legend=False)

    def plot_freq_TRAI(self, k, valid=False):
        # Frequency with specific TRAI
        half_frq, normalization_half = self.cal_frequency(k-1, valid=valid)

        fig = plt.figure(figsize=(6, 4.1), num='Frequency--TRAI:%d (%s)' % (k, valid))
        ax = plt.subplot()
        ax.plot(half_frq, normalization_half)
        plot_norm(ax, 'Freq (Hz)', '|Y(freq)|', x_lim=[0, pow(10, 6)], title='TRAI:%d' % k, legend=False)

    def plot_2cls_freq(self, TRAI_1, TRAI_2, same):
        fig = plt.figure(figsize=(6.5, 10), num='Frequency with same %s' % same)
        for idx, k in enumerate(TRAI_1):
            half_frq, normalization_half = self.cal_frequency(k - 1)
            ax = fig.add_subplot(5, 2, 1 + idx * 2)
            ax.plot(half_frq, normalization_half)
            plot_norm(ax, 'Freq (Hz)', '|Y(freq)|', x_lim=[0, pow(10, 6)], legend=False)

            half_frq, normalization_half = self.cal_frequency(TRAI_2[idx] - 1)
            ax2 = fig.add_subplot(5, 2, 2 + idx * 2)
            ax2.plot(half_frq, normalization_half)
            plot_norm(ax2, 'Freq (Hz)', '|Y(freq)|', x_lim=[0, pow(10, 6)], legend=False)