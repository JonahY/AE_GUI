﻿"""
@version: 2.0
@author: Jonah
@file: __init__.py
@time: 2021/11/10 12:56
"""

# from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt


def formatnum(x, pos):
    return '$10^{}$'.format(int(x))


def plot_norm(ax, xlabel=None, ylabel=None, zlabel=None, title=None, x_lim=[], y_lim=[], z_lim=[], legend=True, grid=False,
              legend_loc='upper left', font_color='black', legendsize=11, labelsize=14, titlesize=15, ticksize=13, linewidth=2):
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    ax.spines['right'].set_linewidth(linewidth)
    ax.spines['top'].set_linewidth(linewidth)

    # 设置坐标刻度值的大小以及刻度值的字体 Arial
    ax.tick_params(which='both', width=linewidth, labelsize=ticksize, colors=font_color)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    [label.set_fontname('Arial') for label in labels]

    font_legend = {'family': 'Arial', 'weight': 'normal', 'size': legendsize}
    font_label = {'family': 'Arial', 'weight': 'bold', 'size': labelsize, 'color':font_color}
    font_title = {'family': 'Arial', 'weight': 'bold', 'size': titlesize, 'color':font_color}

    if x_lim:
        ax.set_xlim(x_lim[0], x_lim[1])
    if y_lim:
        ax.set_ylim(y_lim[0], y_lim[1])
    if z_lim:
        ax.set_zlim(z_lim[0], z_lim[1])
    if legend:
        ax.legend(loc=legend_loc, prop=font_legend, frameon=False)
    if grid:
        ax.grid(ls='-.')
    if xlabel:
        ax.set_xlabel(xlabel, font_label)
    if ylabel:
        ax.set_ylabel(ylabel, font_label)
    if zlabel:
        ax.set_zlabel(zlabel, font_label)
    if title:
        ax.set_title(title, font_title)
    plt.tight_layout()