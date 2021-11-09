# -*- coding: UTF-8 -*-
from plot_format import plot_norm
from collections import Counter
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from tqdm import tqdm
import array
import csv
import sqlite3
from kmeans import KernelKMeans, ICA
from utils import *
from wave_freq import *
import warnings
from matplotlib.pylab import mpl
from plotwindow import PlotWindow
from scipy.signal import savgol_filter


warnings.filterwarnings("ignore")
mpl.rcParams['axes.unicode_minus'] = False  #显示负号
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'


class Features:
    def __init__(self, color_1, color_2, time, status, output):
        self.color_1 = color_1
        self.color_2 = color_2
        self.Time = time
        self.convert = lambda x, a, b: pow(x, a) * pow(10, b)
        self.status = status
        self.output = output

    def __cal_linear_interval(self, tmp, interval):
        """
        Take the linear interval to get the first number in each order and the interval between grids
        :param tmp: Energy/Amplitude/Duration in order of magnitude
        :param interval: Number of bins in each order of magnitude
        :return:
        """
        tmp_max = int(max(tmp))
        tmp_min = int(min(tmp))
        mid = []
        if tmp_min <= 0:
            inter = [0] + [pow(10, i) for i in range(len(str(tmp_max)))]
        else:
            inter = [pow(10, i) for i in range(len(str(tmp_min)) - 1, len(str(tmp_max)))]
        for idx in range(len(inter)):
            try:
                mid.extend([(inter[idx + 1] - inter[idx]) / interval])
            except IndexError:
                mid.extend([9 * inter[idx] / interval])
        return inter, mid

    def __cal_log_interval(self, tmp):
        """
        Take the logarithmic interval to get the first number in each order
        :param tmp: Energy/Amplitude/Duration in order of magnitude
        :return:
        """
        tmp_min = math.floor(np.log10(min(tmp)))
        tmp_max = math.ceil(np.log10(max(tmp)))
        inter = [i for i in range(tmp_min, tmp_max + 1)]
        return inter

    def __cal_negtive_interval(self, res, interval):
        """

        :param res:
        :param interval:
        :return:
        """
        tmp = sorted(np.array(res))
        tmp_min, tmp_max = math.floor(np.log10(min(tmp))), math.ceil(np.log10(max(tmp)))
        inter = [pow(10, i) for i in range(tmp_min, tmp_max + 1)]
        mid = [interval * pow(10, i) for i in range(tmp_min + 1, tmp_max + 2)]
        return inter, mid

    def __cal_linear(self, tmp, inter, mid, interval_num, idx=0):
        """
        Calculate the probability density value at linear interval
        :param tmp: Energy/Amplitude/Duration in order of magnitude
        :param inter: The first number of each order of magnitude
        :param mid: Bin spacing per order of magnitude
        :param interval_num: Number of bins divided in each order of magnitude
        :param idx:
        :return:
        """
        # 初始化横坐标
        x = np.array([])
        for i in inter:
            if i != 0:
                x = np.append(x, np.linspace(i, i * 10, interval_num, endpoint=False))
            else:
                x = np.append(x, np.linspace(i, 1, interval_num, endpoint=False))
        # 初始化纵坐标
        y = np.zeros(x.shape[0])
        for i, n in Counter(tmp).items():
            while True:
                try:
                    if x[idx] <= i < x[idx + 1]:
                        y[idx] += n
                        break
                except IndexError:
                    if x[idx] <= i:
                        y[idx] += n
                        break
                idx += 1
        # 对横坐标作进一步筛选，计算概率分布值
        x, y = x[y != 0], y[y != 0]
        xx = np.zeros(x.shape[0])
        yy = y / sum(y)
        # 取区间终点作为该段的横坐标
        for idx in range(len(x) - 1):
            xx[idx] = (x[idx] + x[idx + 1]) / 2
        xx[-1] = x[-1] + pow(10, len(str(int(x[-1])))) * (0.9 / interval_num) / 2
        # 计算分段区间长度，从而求得概率密度值
        interval = []
        for i, j in enumerate(mid):
            try:
                # num = len(np.intersect1d(np.where(inter[i] <= xx)[0],
                #                          np.where(xx < inter[i + 1])[0]))
                num = len(np.where((inter[i] <= xx) & (xx < inter[i + 1]))[0])
                interval.extend([j] * num)
            except IndexError:
                num = len(np.where(inter[i] <= xx)[0])
                interval.extend([j] * num)
        yy = yy / np.array(interval)
        #     # 取对数变换为线性关系
        #     log_xx = np.log10(xx)
        #     log_yy = np.log10(yy)
        #     fit = np.polyfit(log_xx, log_yy, 1)
        #     alpha = abs(fit[0])
        #     fit_x = np.linspace(min(log_xx), max(log_xx), 100)
        #     fit_y = np.polyval(fit, fit_x)
        return xx, yy

    def __cal_log(self, tmp, inter, interval_num, idx=0):
        """
        Calculate the probability density value at logarithmic interval
        :param tmp: Energy/Amplitude/Duration in order of magnitude
        :param inter: The first number of each order of magnitude
        :param interval_num: Number of bins divided in each order of magnitude
        :param idx:
        :return:
        """
        x, xx, interval = np.array([]), np.array([]), np.array([])
        for i in inter:
            logspace = np.logspace(i, i + 1, interval_num, endpoint=False)
            tmp_inter = [logspace[i + 1] - logspace[i] for i in range(len(logspace) - 1)]
            tmp_xx = [(logspace[i + 1] + logspace[i]) / 2 for i in range(len(logspace) - 1)]
            tmp_inter.append(10 * logspace[0] - logspace[-1])
            tmp_xx.append((10 * logspace[0] + logspace[-1]) / 2)
            x = np.append(x, logspace)
            interval = np.append(interval, np.array(tmp_inter))
            xx = np.append(xx, np.array(tmp_xx))

        y = np.zeros(x.shape[0])
        for i, n in Counter(tmp).items():
            while True:
                try:
                    if x[idx] <= i < x[idx + 1]:
                        y[idx] += n
                        break
                except IndexError:
                    if x[idx] <= i:
                        y[idx] += n
                        break
                idx += 1

        xx, y, interval = xx[y != 0], y[y != 0], interval[y != 0]
        yy = y / (sum(y) * interval)
        return xx, yy

    def __cal_N_Naft(self, tmp, eny_lim):
        N_ms, N_as = 0, 0
        main_peak = np.where(eny_lim[0] < tmp)[0]
        if len(main_peak):
            for i in range(main_peak.shape[0] - 1):
                if main_peak[i] >= eny_lim[1]:
                    continue
                elif main_peak[i + 1] - main_peak[i] == 1:
                    N_ms += tmp[main_peak[i]]
                    continue
                N_ms += tmp[main_peak[i]]
                N_as += np.max(tmp[main_peak[i] + 1:main_peak[i + 1]])
            if main_peak[-1] < tmp.shape[0] - 1:
                N_as += np.max(tmp[main_peak[-1] + 1:])
            N_ms += tmp[main_peak[-1]]
        return N_ms + N_as, N_as

    def __cal_OmiroLaw_helper(self, tmp, eny_lim):
        res = [[] for _ in range(len(eny_lim))]
        for idx in range(len(eny_lim)):
            main_peak = np.where((eny_lim[idx][0] < tmp) & (tmp < eny_lim[idx][1]))[0]
            if len(main_peak):
                for i in range(main_peak.shape[0] - 1):
                    for j in range(main_peak[i] + 1, main_peak[i + 1] + 1):
                        if tmp[j] < eny_lim[idx][1]:
                            k = self.Time[j] - self.Time[main_peak[i]]
                            res[idx].append(k)
                        else:
                            break
                if main_peak[-1] < tmp.shape[0] - 1:
                    for j in range(main_peak[-1] + 1, tmp.shape[0]):
                        k = self.Time[j] - self.Time[main_peak[-1]]
                        res[idx].append(k)
        return res

    def cal_PDF(self, tmp, xlabel, ylabel, LIM=None, INTERVAL_NUM=None, COLOR='black', FIT=False, bin_method='log'):
        """
        Calculate Probability Density Distribution Function
        :param tmp: Energy/Amplitude/Duration in order of magnitude of original data
        :param xlabel: 'Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)'
        :param ylabel: 'PDF (A)', 'PDF (D)', 'PDF (E)'
        :param LIM: Use in function fitting, support specific values or indexes,
                    value: [0, float('inf')], [100, 900], ...
                    index: [0, None], [11, -2], ...
        :param INTERVAL_NUM: Number of bins divided in each order of magnitude
        :param bin_method: Method to divide the bin, Support linear partition and logarithmic partition
        :param FIT: Whether to fit parameters, support True or False
        :param COLOR: Color when drawing with original data, population I and population II respectively
        :return:
        """
        if INTERVAL_NUM is None:
            INTERVAL_NUM = 6
        if LIM is None:
            LIM = [0, None]

        plotWindow = PlotWindow('PDF--%s' % xlabel, 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.133, bottom=0.179, right=0.975, top=0.962)
        fig.text(0.15, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12})
        ax = fig.add_subplot()

        if bin_method == 'linear':
            inter, mid = self.__cal_linear_interval(tmp, INTERVAL_NUM)
            xx, yy = self.__cal_linear(tmp, inter, mid, INTERVAL_NUM)
        elif bin_method == 'log':
            inter = self.__cal_log_interval(tmp)
            xx, yy = self.__cal_log(tmp, inter, INTERVAL_NUM)
        if FIT:
            fit = np.polyfit(np.log10(xx[LIM[0]:LIM[1]]), np.log10(yy[LIM[0]:LIM[1]]), 1)
            alpha, b = fit[0], fit[1]
            fit_x = np.linspace(xx[LIM[0]], xx[-1], 100)
            fit_y = self.convert(fit_x, alpha, b)
            ax.plot(fit_x, fit_y, '-.', lw=1, color=COLOR)
            ax.loglog(xx, yy, '.', marker='.', markersize=8, color=COLOR, label='slope-{:.2f}'.format(abs(alpha)))
            plot_norm(ax, xlabel, ylabel, legend_loc='upper right', legend=True)
        else:
            ax.loglog(xx, yy, '.', marker='.', markersize=8, color=COLOR)
            plot_norm(ax, xlabel, ylabel, legend=False)

        with open('/'.join([self.output, self.status]) + '_%s.txt' % ylabel, 'w') as f:
            f.write('{}, {}\n'.format(xlabel, ylabel))
            for i, j in zip(xx, yy):
                f.write('{}, {}\n'.format(i, j))

        return plotWindow

    def cal_CCDF(self, tmp, xlabel, ylabel, LIM=None, COLOR='black', FIT=False):
        """
        Calculate Complementary Cumulative Distribution Function
        :param tmp: Energy/Amplitude/Duration in order of magnitude of original data
        :param xlabel: 'Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)'
        :param ylabel: 'CCDF (A)', 'CCDF (D)', 'CCDF (E)'
        :param LIM: Use in function fitting, support specific values or indexes,
                    value: [0, float('inf')], [100, 900], ...
                    index: [0, None], [11, -2], ...
        :param FIT: Whether to fit parameters, support True or False
        :param COLOR: Color when drawing with original data, population I and population II respectively
        :return:
        """
        if LIM is None:
            LIM = [0, float('inf')]
        N = len(tmp)

        plotWindow = PlotWindow('CCDF--%s' % xlabel, 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.133, bottom=0.179, right=0.975, top=0.962)
        fig.text(0.15, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12})
        ax = fig.add_subplot()

        xx, yy = [], []
        for i in range(N - 1):
            xx.append(np.mean([tmp[i], tmp[i + 1]]))
            yy.append((N - i + 1) / N)
        if FIT:
            xx, yy = np.array(xx), np.array(yy)
            fit_lim = np.where((xx > LIM[0]) & (xx < LIM[1]))[0]
            fit = np.polyfit(np.log10(xx[fit_lim[0]:fit_lim[-1]]), np.log10(yy[fit_lim[0]:fit_lim[-1]]), 1)
            alpha, b = fit[0], fit[1]
            fit_x = np.linspace(xx[fit_lim[0]], xx[fit_lim[-1]], 100)
            fit_y = self.convert(fit_x, alpha, b)
            ax.plot(fit_x, fit_y, '-.', lw=1, color=COLOR)
            ax.loglog(xx, yy, color=COLOR, label='slope-{:.2f}'.format(abs(alpha)))
            plot_norm(ax, xlabel, ylabel, legend_loc='upper right')
        else:
            ax.loglog(xx, yy, color=COLOR)
            plot_norm(ax, xlabel, ylabel, legend=False)

        with open('/'.join([self.output, self.status]) + '_CCDF(%s).txt' % xlabel[0], 'w') as f:
            f.write('{}, {}\n'.format(xlabel, ylabel))
            for i, j in zip(xx, yy):
                f.write('{}, {}\n'.format(i, j))

        return plotWindow

    def cal_ML(self, tmp, xlabel, ylabel, COLOR='black', ECOLOR=None):
        """
        Calculate the maximum likelihood function distribution
        :param tmp: Energy/Amplitude/Duration in order of magnitude of original data
        :param xlabel: 'Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)'
        :param ylabel: 'ML (A)', 'ML (D)', 'ML (E)'
        :param COLOR: Color when drawing with original data, population I and population II respectively
        :param ECOLOR: Line color of error bar, corresponding parameter COLOR
        :return:
        """
        if not ECOLOR:
            ECOLOR = [0.7, 0.7, 0.7]

        N = len(tmp)
        plotWindow = PlotWindow('ML--%s' % xlabel, 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.131, bottom=0.179, right=0.975, top=0.944)
        fig.text(0.96, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                 horizontalalignment="right")
        ax = fig.add_subplot()
        ax.set_xscale("log", nonposx='clip')
        ML_y, Error_bar = [], []
        for j in range(N):
            valid_x = sorted(tmp)[j:]
            E0 = valid_x[0]
            Sum = np.sum(np.log(valid_x / E0))
            N_prime = N - j
            alpha = 1 + N_prime / Sum
            error_bar = (alpha - 1) / pow(N_prime, 0.5)
            ML_y.append(alpha)
            Error_bar.append(error_bar)
        ax.errorbar(sorted(tmp), ML_y, yerr=Error_bar, fmt='o', ecolor=ECOLOR, color=COLOR, elinewidth=1, capsize=2, ms=3)
        plot_norm(ax, xlabel, ylabel, y_lim=[1.25, 3], legend=False)

        with open('/'.join([self.output, self.status]) + '_ML(%s).txt' % xlabel[0], 'w') as f:
            f.write('{}, {}, Error bar\n'.format(xlabel, ylabel))
            for i, j, k in zip(tmp, ML_y, Error_bar):
                f.write('{}, {}, {}\n'.format(i, j, k))

        return plotWindow

    def cal_contour(self, tmp_1, tmp_2, xlabel, ylabel, x_lim, y_lim, size_x=40, size_y=40, method='linear_bin', padding=False, colorbar=False):
        tmp_1, tmp_2 = 20 * np.log10(tmp_1), 20 * np.log10(tmp_2)
        if method == 'Log bin':
            sum_x, sum_y = x_lim[1] - x_lim[0], y_lim[1] - y_lim[0]
            arry_x = np.logspace(np.log10(sum_x + 10), 1, size_x) / (
                    sum(np.logspace(np.log10(sum_x + 10), 1, size_x)) / sum_x)
            arry_y = np.logspace(np.log10(sum_y + 10), 1, size_y) / (
                    sum(np.logspace(np.log10(sum_y + 10), 1, size_y)) / sum_y)
            x, y = [], []
            for tmp, res, arry in zip([x_lim[0], y_lim[0]], [x, y], [arry_x, arry_y]):
                for i in arry:
                    res.append(tmp)
                    tmp += i
            x, y = np.array(x), np.array(y)
        elif method == 'Linear bin':
            x, y = np.linspace(x_lim[0], x_lim[1], size_x), np.linspace(y_lim[0], y_lim[1], size_y)
        X, Y = np.meshgrid(x, y)
        height = np.zeros([X.shape[0], Y.shape[1]])
        linestyles = ['solid'] * 8 + ['--'] * 4
        levels = [1, 2, 3, 6, 12, 24, 48, 96, 192, 384, 768, 1536]
        colors = [[1, 0, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0], [0.5, 0.5, 0.5],
                  [1, 0.3, 0], [0, 0, 0], [0, 1, 1], [1, 0, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0]]

        for i in range(X.shape[1] - 1):
            valid_x = np.where((tmp_1 < X[0, i + 1]) & (tmp_1 >= X[0, i]))[0]
            for j in range(Y.shape[0] - 1):
                valid_y = np.where((tmp_2 < Y[j + 1, 0]) & (tmp_2 >= Y[j, 0]))[0]
                height[j, i] = np.intersect1d(valid_x, valid_y).shape[0]

        plotWindow = PlotWindow('Contour--%s & %s' % (ylabel, xlabel), 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.115, bottom=0.17, right=0.975, top=0.95)
        if colorbar:
            fig.text(0.78, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
        else:
            fig.text(0.96, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
        ax = fig.add_subplot()
        if padding:
            ct = ax.contourf(X, Y, height, levels, colors=colors, extend='max')
            if colorbar:
                cbar = fig.colorbar(ct)
        else:
            ct = ax.contour(X, Y, height, levels, colors=colors, linewidths=1, linestyles=linestyles)
            if colorbar:
                cbar = fig.colorbar(ct)
        plot_norm(ax, xlabel, ylabel, legend=False)

        return plotWindow

    def plot_correlation(self, tmp_1, tmp_2, xlabel, ylabel, COLOR='black'):
        plotWindow = PlotWindow('Correlation--%s & %s' % (ylabel, xlabel), 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.115, bottom=0.17, right=0.975, top=0.95)
        fig.text(0.96, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                 horizontalalignment="right")
        ax = fig.add_subplot()
        ax.loglog(tmp_1, tmp_2, '.', Marker='.', markersize=8, color=COLOR)
        plot_norm(ax, xlabel, ylabel, legend=False)

        with open('/'.join([self.output, self.status]) + '_%s-%s.txt' % (ylabel[0], xlabel[0]), 'w') as f:
            f.write('{}, {}\n'.format(xlabel, ylabel))
            for i, j in zip(tmp_1, tmp_2):
                f.write('{}, {}\n'.format(i, j))

        return plotWindow

    def plot_3D_correlation(self, tmp_1, tmp_2, tmp_3, xlabel, ylabel, zlabel, COLOR='black'):
        plotWindow = PlotWindow('3D Correlation--%s & %s' % (ylabel, xlabel), 6, 3.9)
        fig = plotWindow.static_canvas.figure
        ax = plt.subplot(projection='3d')
        ax.scatter3D(np.log10(tmp_1), np.log10(tmp_2), np.log10(tmp_3), s=15, color=COLOR)
        ax.xaxis.set_major_formatter(plt.FuncFormatter('$10^{:.0f}$'.format))
        ax.yaxis.set_major_formatter(plt.FuncFormatter('$10^{:.0f}$'.format))
        ax.zaxis.set_major_formatter(plt.FuncFormatter('$10^{:.0f}$'.format))
        plot_norm(ax, xlabel, ylabel, zlabel, legend=False)

        return plotWindow

    def plot_feature_time(self, tmp, ylabel, x_max=29000, color_tmp='black', color_stretcher='r', width=55,
                          stretcher_data=None, smooth=False):
        plotWindow = PlotWindow('Time Domain Curve', 6, 3.9)
        fig = plotWindow.static_canvas.figure
        if stretcher_data:
            fig.subplots_adjust(left=0.12, bottom=0.157, right=0.877, top=0.853)
            fig.text(0.86, 0.18, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
        else:
            fig.subplots_adjust(left=0.115, bottom=0.17, right=0.975, top=0.95)
            fig.text(0.96, 0.19, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12},
                     horizontalalignment="right")
        ax = fig.add_subplot()
        if stretcher_data:
            time, displace, load, strain, stress = load_stress(stretcher_data)
            if smooth:
                stress = smooth_curve(time, stress)
            strain_max = strain[-1] * x_max / self.Time[-1]

            ax.bar(self.Time, tmp, color=color_tmp, width=width, log=True)
            plot_norm(ax, 'Time (s)', ylabel, x_lim=[0, x_max], y_lim=[0, 15000], legend=False)

            ax2 = ax.twinx()
            # ax2.plot(time, stress, color_stretcher, lw=3)
            plot_norm(ax2, 'Time (s)', 'Stress (MPa)', x_lim=[0, x_max], y_lim=[0, 700], legend=False, font_color=color_stretcher)

            ax3 = ax2.twiny()
            for key in ['right', 'top']:
                ax3.spines[key].set_color(color_stretcher)
            ax3.plot(strain, stress, color_stretcher, lw=3)
            plot_norm(ax3, 'Strain (%)', x_lim=[0, strain_max], y_lim=[0, 700], legend=False, font_color=color_stretcher)
        else:
            ax.bar(self.Time, tmp, color=color_tmp, width=width, log=True)
            plot_norm(ax, 'Time (s)', ylabel, x_lim=[0, x_max], y_lim=[0, 15000], legend=False)

        return plotWindow

    def cal_BathLaw(self, tmp, xlabel, ylabel, INTERVAL_NUM=None, COLOR='black', bin_method='log'):
        if INTERVAL_NUM is None:
            INTERVAL_NUM = 8

        plotWindow = PlotWindow('Bath law', 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.145, bottom=0.19, right=0.975, top=0.962)
        fig.text(0.12, 0.2, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12})
        ax = fig.add_subplot()
        tmp_max = int(max(tmp))
        if bin_method == 'linear':
            x = np.array([])
            inter = [pow(10, i) for i in range(0, len(str(tmp_max)))]
            for i in inter:
                x = np.append(x, np.linspace(i, i * 10, INTERVAL_NUM, endpoint=False))
        elif bin_method == 'log':
            x, x_eny = np.array([]), np.array([])
            inter = self.__cal_log_interval(tmp)
            for i in inter:
                if i < 0:
                    continue
                logspace = np.logspace(i, i + 1, INTERVAL_NUM, endpoint=False)
                x = np.append(x, logspace)
                tmp_xx = [(logspace[i + 1] + logspace[i]) / 2 for i in range(len(logspace) - 1)]
                tmp_xx.append((10 * logspace[0] + logspace[-1]) / 2)
                x_eny = np.append(x_eny, np.array(tmp_xx))
        y = []
        for k in range(x.shape[0]):
            N, Naft = self.__cal_N_Naft(tmp, [x[k], x[k + 1]]) if k != x.shape[0] - 1 else self.__cal_N_Naft(tmp, [x[k], float('inf')])
            if Naft != 0 and N != 0:
                y.append(np.log10(N / Naft))
            else:
                y.append(float('inf'))
        y = np.array(y)
        if bin_method == 'linear':
            x, y = x[y != float('inf')], y[y != float('inf')]
            x_eny = np.zeros(x.shape[0])
            for idx in range(len(x) - 1):
                x_eny[idx] = (x[idx] + x[idx + 1]) / 2
            x_eny[-1] = x[-1] + pow(10, len(str(int(x[-1])))) * (0.9 / INTERVAL_NUM) / 2
        elif bin_method == 'log':
            x_eny, y = x_eny[y != float('inf')], y[y != float('inf')]
        ax.semilogx(x_eny, y, color=COLOR, marker='o', markersize=8, mec=COLOR, mfc='none')
        ax.axhline(1.2, ls='-.', linewidth=1, color="black")
        plot_norm(ax, xlabel, ylabel, y_lim=[-1, 4], legend=False)

        with open('/'.join([self.output, self.status]) + '_BathLaw(%s).txt' % xlabel[0], 'w') as f:
            f.write('{}, {}\n'.format(xlabel, ylabel))
            for i, j in zip(x_eny, y):
                f.write('{}, {}\n'.format(i, j))

        return plotWindow

    def cal_WaitingTime(self, time, xlabel, ylabel, INTERVAL_NUM=None, COLOR='black', FIT=False, LIM=None, bin_method='log'):
        if INTERVAL_NUM is None:
            INTERVAL_NUM = 8
        if LIM is None:
            LIM = [0, None]

        plotWindow = PlotWindow('Distribution of waiting time', 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.139, bottom=0.189, right=0.975, top=0.962)
        fig.text(0.16, 0.22, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12})
        ax = fig.add_subplot()
        res = time[1:] - time[:-1]
        res = res[np.where(res != 0)[0]]
        if bin_method == 'linear':
            inter, mid = self.__cal_negtive_interval(res, 0.9 / INTERVAL_NUM)
            xx, yy = self.__cal_linear(sorted(np.array(res)), inter, mid, INTERVAL_NUM)
        elif bin_method == 'log':
            inter = self.__cal_log_interval(res)
            xx, yy = self.__cal_log(sorted(np.array(res)), inter, INTERVAL_NUM)
        if FIT:
            xx, yy = np.array(xx), np.array(yy)
            fit = np.polyfit(np.log10(xx[LIM[0]:LIM[1]]), np.log10(yy[LIM[0]:LIM[1]]), 1)
            alpha, b = fit[0], fit[1]
            fit_x = np.linspace(xx[0], xx[-1], 100)
            fit_y = self.convert(fit_x, alpha, b)
            ax.plot(fit_x, fit_y, '-.', lw=1, color=COLOR)
            ax.loglog(xx, yy, '.', markersize=8, marker='o', mec=COLOR, mfc='none', color=COLOR, label='slope-{:.2f}'.format(abs(alpha)))
            plot_norm(ax, xlabel, ylabel, legend_loc='upper right')
        else:
            ax.loglog(xx, yy, '.', markersize=8, marker='o', mec=COLOR, mfc='none', color=COLOR)
            plot_norm(ax, xlabel, ylabel, legend=False)

        with open('/'.join([self.output, self.status]) + '_WaitingTime.txt', 'w') as f:
            f.write('{}, {}\n'.format(xlabel, ylabel))
            for i, j in zip(xx, yy):
                f.write('{}, {}\n'.format(i, j))

        return plotWindow

    def cal_OmoriLaw(self, tmp, xlabel, ylabel, INTERVAL_NUM=None, FIT=False, bin_method='log'):
        if INTERVAL_NUM is None:
            INTERVAL_NUM = 8
        eny_lim = [[0.01, 0.1], [0.1, 1], [1, 10], [10, 1000], [1000, 10000]]
        tmp = self.__cal_OmiroLaw_helper(tmp, eny_lim)

        plotWindow = PlotWindow("Omori's law", 6, 3.9)
        fig = plotWindow.static_canvas.figure
        fig.subplots_adjust(left=0.115, bottom=0.17, right=0.975, top=0.95)
        fig.text(0.16, 0.21, self.status, fontdict={'family': 'Arial', 'fontweight': 'bold', 'fontsize': 12})
        ax = fig.add_subplot()
        for i, [marker, color, label] in enumerate(zip(['>', 'o', 'p', 'h', 'H'],
                                                       [[1, 0, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0],
                                                        [0.5, 0.5, 0.5]],
                                                       ['$10^{-2}aJ<E_{MS}<10^{-1}aJ$',
                                                        '$10^{-1}aJ<E_{MS}<10^{0}aJ$',
                                                        '$10^{0}aJ<E_{MS}<10^{1}aJ$', '$10^{1}aJ<E_{MS}<10^{3}aJ$',
                                                        '$10^{3}aJ<E_{MS}<10^{4}aJ$'])):
            if len(tmp[i]):
                tmp[i] = np.array(tmp[i])
                tmp[i] = tmp[i][np.where(tmp[i] != 0)[0]]
                if bin_method == 'linear':
                    inter, mid = self.__cal_negtive_interval(tmp[i], 0.9 / INTERVAL_NUM)
                    xx, yy = self.__cal_linear(sorted(np.array(tmp[i])), inter, mid, INTERVAL_NUM)
                elif bin_method == 'log':
                    inter = self.__cal_log_interval(tmp[i])
                    xx, yy = self.__cal_log(sorted(np.array(tmp[i])), inter, INTERVAL_NUM)
                if FIT:
                    xx, yy = np.array(xx), np.array(yy)
                    fit = np.polyfit(np.log10(xx), np.log10(yy), 1)
                    alpha, b = fit[0], fit[1]
                    fit_x = np.linspace(xx[0], xx[-1], 100)
                    fit_y = self.convert(fit_x, alpha, b)
                    ax.plot(fit_x, fit_y, '-.', lw=1, color=color)
                    ax.loglog(xx, yy, markersize=8, marker=marker, mec=color, mfc='none', color=color,
                              label='{}--{:.2f}'.format(label, abs(alpha)))
                else:
                    ax.loglog(xx, yy, markersize=8, marker=marker, mec=color, mfc='none', color=color, label=label)
                plot_norm(ax, xlabel, ylabel, legend_loc='upper right')

                with open('/'.join([self.output, self.status]) + '_OmoriLaw_(%s).txt' % label[1:-1].replace('<', ' ').replace('>', ' '), 'w') as f:
                    f.write('t-t_{MS} (s), r_{AS}(t-t_{MS})(s^{-1})\n')
                    for i, j in zip(xx, yy):
                        f.write('{}, {}\n'.format(i, j))

        return plotWindow


# if __name__ == "__main__":
#     path = r'E:\data\vallen'
#     fold = 'Ni-tension test-electrolysis-1-0.01-AE-20201031'
#     path_pri = fold + '.pridb'
#     path_tra = fold + '.tradb'
#     features_path = fold + '.txt'
#     os.chdir('/'.join([path, fold]))
#     # 2020.11.10-PM-self
#     # 6016_CR_1
#     # 316L-1.5-z3-AE-3 sensor-20200530
#     # Ni-tension test-electrolysis-1-0.01-AE-20201031
#     # Ni-tension test-pure-1-0.01-AE-20201030
#     # 2020.11.10-PM-self
#
#     reload = Reload(path_pri, path_tra, fold)
#     data_tra, data_pri, chan_1, chan_2, chan_3, chan_4 = reload.read_vallen_data(lower=2)
#     print('Channel 1: {} | Channel 2: {} | Channel 3: {} | Channel 4: {}'.format(chan_1.shape[0], chan_2.shape[0],
#                                                                                  chan_3.shape[0], chan_4.shape[0]))
#     # SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI
#     chan = chan_2
#     Time, Amp, RiseT, Dur, Eny, RMS, Counts = chan[:, 1], chan[:, 4], chan[:, 5], \
#                                               chan[:, 6], chan[:, 7], chan[:, 8], chan[:, 9]
#
#     # SetID, Time, Chan, Thr, Amp, RiseT, Dur, Eny, RMS, Counts, TRAI
#     feature_idx = [Amp, Dur, Eny]
#     xlabelz = ['Amplitude (μV)', 'Duration (μs)', 'Energy (aJ)']
#     ylabelz = ['PDF(A)', 'PDF(D)', 'PDF(E)']
#     color_1 = [255 / 255, 0 / 255, 102 / 255]  # red
#     color_2 = [0 / 255, 136 / 255, 204 / 255]  # blue
#     status = fold.split('-')[0] + ' ' + fold.split('-')[2]
#     features = Features(color_1, color_2, Time, feature_idx, status)
#
#     # ICA and Kernel K-Means
#     S_, A_ = ICA(2, np.log10(Amp), np.log10(Eny), np.log10(Dur))
#     km = KernelKMeans(n_clusters=2, max_iter=100, random_state=100, verbose=1, kernel="rbf")
#     pred = km.fit_predict(S_)
#     cls_KKM = []
#     for i in range(2):
#         cls_KKM.append(pred == i)
#     # cls_KKM[0], cls_KKM[1] = pred == 1, pred == 0

