"""
Unit 9: 自定义控件与 Dock 系统
==============================
学习目标:
  1. 使用 ParameterTree 创建可配置的参数面板
  2. Dock 系统: DockArea 和 Dock 实现可停靠面板
  3. 构建带参数控制 + 实时预览的交互界面
  4. 理解 pyqtgraph 的 dock 布局机制
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

app = pg.mkQApp("Unit 9: 自定义控件与 Dock 系统")


# ---------------------------------------------------------------------------
# 1. ParameterTree: 参数树
#    - 用于创建可交互的参数面板
#    - 支持 int, float, bool, list, color 等类型
#    - sigTreeStateChanged 信号监听参数变化
# ---------------------------------------------------------------------------
class ParamDemo:
    def __init__(self):
        self.win = pg.GraphicsLayoutWidget(
            title="1. ParameterTree 参数树", show=True)
        self.win.resize(1000, 600)

        self.plot = self.win.addPlot(title="参数控制绘图")
        self.x = np.linspace(0, 10, 500)
        self.curve = self.plot.plot(self.x, np.zeros(len(self.x)), pen='c')

        # 创建参数树
        params = [
            {'name': '信号参数', 'type': 'group', 'children': [
                {'name': '振幅', 'type': 'float', 'value': 5.0,
                 'limits': (0.1, 20), 'step': 0.1},
                {'name': '频率', 'type': 'float', 'value': 1.0,
                 'limits': (0.1, 10), 'step': 0.1},
                {'name': '偏移', 'type': 'float', 'value': 0.0,
                 'limits': (-10, 10), 'step': 0.1},
                {'name': '信号类型', 'type': 'list',
                 'values': ['sin', 'cos', 'sinc', 'chirp'],
                 'value': 'sin'},
            ]},
            {'name': '噪声', 'type': 'group', 'children': [
                {'name': '添加噪声', 'type': 'bool', 'value': False},
                {'name': '噪声幅度', 'type': 'float', 'value': 0.5,
                 'limits': (0, 5), 'step': 0.01},
            ]},
            {'name': '显示', 'type': 'group', 'children': [
                {'name': '线条颜色', 'type': 'color', 'value': '#00FFFF'},
                {'name': '线宽', 'type': 'int', 'value': 1,
                 'limits': (1, 5)},
                {'name': '显示散点', 'type': 'bool', 'value': False},
            ]},
        ]

        self.tree = pg.parametertree.ParameterTree()
        self.param = pg.parametertree.Parameter.create(
            name='参数', type='group', children=params)
        self.tree.setParameters(self.param, showTop=False)

        # 用 QSplitter 组合参数面板和绘图区
        splitter = QtWidgets.QSplitter()
        param_widget = QtWidgets.QWidget()
        param_layout = QtWidgets.QVBoxLayout()
        param_layout.addWidget(self.tree)
        param_widget.setLayout(param_layout)
        splitter.addWidget(param_widget)
        splitter.addWidget(self.win)

        self.main_win = QtWidgets.QMainWindow()
        self.main_win.setWindowTitle("Unit 9: 参数树演示")
        self.main_win.setCentralWidget(splitter)
        self.main_win.resize(1000, 600)
        self.main_win.show()

        self.param.sigTreeStateChanged.connect(self.update_plot)
        self.update_plot()

    def update_plot(self, param=None, changes=None):
        amp = self.param.child('信号参数', '振幅').value()
        freq = self.param.child('信号参数', '频率').value()
        offset = self.param.child('信号参数', '偏移').value()
        sig_type = self.param.child('信号参数', '信号类型').value()

        add_noise = self.param.child('噪声', '添加噪声').value()
        noise_amp = self.param.child('噪声', '噪声幅度').value()

        color = self.param.child('显示', '线条颜色').value()
        width = self.param.child('显示', '线宽').value()
        show_scatter = self.param.child('显示', '显示散点').value()

        if sig_type == 'sin':
            y = amp * np.sin(freq * self.x) + offset
        elif sig_type == 'cos':
            y = amp * np.cos(freq * self.x) + offset
        elif sig_type == 'sinc':
            xc = (self.x - 5) * freq
            xc[xc == 0] = 1e-10
            y = amp * np.sin(xc) / xc + offset
        else:  # chirp
            y = amp * np.sin(freq * self.x**1.3) + offset

        if add_noise:
            y += np.random.normal(0, noise_amp, size=len(y))

        if show_scatter:
            self.curve = self.plot.plot(
                self.x, y, pen=pg.mkPen(color, width=width),
                symbol='o', symbolSize=4,
                clear=True)
        else:
            self.curve = self.plot.plot(
                self.x, y, pen=pg.mkPen(color, width=width),
                clear=True)


# ---------------------------------------------------------------------------
# 2. Dock 系统: DockArea + Dock
#    - DockArea: 可停靠窗口的容器
#    - Dock: 单个可停靠面板
#    - 支持拖拽分离/重组
# ---------------------------------------------------------------------------
def demo_dock_system():
    area = pg.dockarea.DockArea()

    # 创建 Dock
    d1 = pg.dockarea.Dock("信号监视器", size=(400, 300))
    d2 = pg.dockarea.Dock("频谱分析", size=(400, 300))
    d3 = pg.dockarea.Dock("统计信息", size=(400, 200))
    d4 = pg.dockarea.Dock("参数控制", size=(300, 400))

    area.addDock(d1, 'left')
    area.addDock(d2, 'right')
    area.addDock(d3, 'bottom', d1)
    area.addDock(d4, 'bottom', d2)

    # 在 Dock 中添加内容
    pw1 = pg.PlotWidget(title="信号")
    x = np.linspace(0, 10, 500)
    signal = np.sin(x) * np.exp(-x / 5) + np.random.normal(0, 0.05, size=500)
    pw1.plot(x, signal, pen='c')
    d1.addWidget(pw1)

    pw2 = pg.PlotWidget(title="FFT 频谱")
    freq = np.fft.rfftfreq(len(signal), d=(10.0 / 500))
    fft = np.abs(np.fft.rfft(signal))
    pw2.plot(freq, fft, pen='m')
    pw2.setLogMode(x=False, y=True)
    d2.addWidget(pw2)

    pw3 = pg.PlotWidget(title="统计")
    hist_data = np.random.normal(0, 1, 1000)
    hist, bins = np.histogram(hist_data, bins=30)
    bar = pg.BarGraphItem(x=bins[:-1], height=hist,
                          width=bins[1] - bins[0], brush='y')
    pw3.addItem(bar)
    d3.addWidget(pw3)

    # 参数面板
    from pyqtgraph.parametertree import Parameter, ParameterTree
    params = [
        {'name': '阈值', 'type': 'float', 'value': 0.5},
        {'name': '窗口大小', 'type': 'int', 'value': 10},
        {'name': '启用滤波', 'type': 'bool', 'value': False},
    ]
    param_obj = Parameter.create(name='设置', type='group', children=params)
    tree = ParameterTree()
    tree.setParameters(param_obj, showTop=False)
    d4.addWidget(tree)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("2. Dock 系统演示")
    win.setCentralWidget(area)
    win.resize(1200, 800)
    win.show()
    return win


# ---------------------------------------------------------------------------
# 3. 综合: 自定义应用程序框架
# ---------------------------------------------------------------------------
def demo_custom_app():
    app_win = QtWidgets.QMainWindow()
    app_win.setWindowTitle("3. 自定义数据分析工具")
    app_win.resize(1200, 800)

    # 使用 Dock 布局
    area = pg.dockarea.DockArea()
    app_win.setCentralWidget(area)

    # 主绘图区
    plot_dock = pg.dockarea.Dock("主视图", size=(700, 500))
    pw_main = pg.PlotWidget(title="数据视图")
    plot_dock.addWidget(pw_main)

    # 历史记录
    history_dock = pg.dockarea.Dock("历史记录", size=(400, 400))

    from pyqtgraph.widgets.DataTreeWidget import DataTreeWidget
    tree = DataTreeWidget()
    history_dock.addWidget(tree)

    # 控制面板
    ctrl_dock = pg.dockarea.Dock("控制面板", size=(300, 300))

    ctrl_widget = QtWidgets.QWidget()
    ctrl_layout = QtWidgets.QVBoxLayout()
    ctrl_widget.setLayout(ctrl_layout)

    label = QtWidgets.QLabel("数据生成器")
    ctrl_layout.addWidget(label)

    btn_gen = QtWidgets.QPushButton("生成随机数据")
    ctrl_layout.addWidget(btn_gen)

    btn_clear = QtWidgets.QPushButton("清除所有")
    ctrl_layout.addWidget(btn_clear)

    ctrl_layout.addStretch()
    ctrl_dock.addWidget(ctrl_widget)

    area.addDock(plot_dock, 'left')
    area.addDock(history_dock, 'right')
    area.addDock(ctrl_dock, 'bottom', history_dock)

    def generate_data():
        pw_main.clear()
        for i in range(5):
            pw_main.plot(np.random.normal(i * 5, 1, 200),
                         pen=(i * 50, 200 - i * 40, 150),
                         name=f'Ch{i}')

    def clear_all():
        pw_main.clear()

    btn_gen.clicked.connect(generate_data)
    btn_clear.clicked.connect(clear_all)

    app_win.show()
    return app_win


# ---------------------------------------------------------------------------
# 运行所有演示
# ---------------------------------------------------------------------------
demo1 = ParamDemo()
demo2 = demo_dock_system()
demo3 = demo_custom_app()

pg.exec()
