"""
@version: 2.0
@author: Jonah
@file: __init__.py
@time: 2021/11/10 12:56
"""

from PyQt5 import QtWidgets, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import warnings
from matplotlib.pylab import mpl


warnings.filterwarnings("ignore")
mpl.rcParams['axes.unicode_minus'] = False
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'


class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, string, width=5, height=3):
        super(PlotWindow, self).__init__()
        # self.resize(560, 420)
        self.setWindowTitle(string)

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QHBoxLayout(self._main)

        self.static_canvas = FigureCanvas(Figure(figsize=(width, height), dpi=100))
        self.layout.addWidget(self.static_canvas)
        self.addToolBar(NavigationToolbar(self.static_canvas, self))