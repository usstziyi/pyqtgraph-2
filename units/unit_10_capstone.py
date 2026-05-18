"""
Unit 10: 实战项目 —— 多通道信号采集与实时分析器
==============================================
综合运用本教程所学知识:
  - Unit 1:  QApplication, PlotWidget, pg.plot()
  - Unit 2:  PlotDataItem, 线图/散点图, fillLevel
  - Unit 3:  mkPen/mkBrush, 坐标轴定制, 图例, BarGraphItem
  - Unit 4:  GraphicsLayoutWidget, 网格布局, X/Y 轴联动
  - Unit 5:  LinearRegionItem, InfiniteLine, TextItem 标注
  - Unit 6:  ImageItem, ColorBarItem
  - Unit 7:  信号与事件处理
  - Unit 8:  实时数据更新, 环形缓冲区, downsampling
  - Unit 9:  ParameterTree, Dock 系统

项目功能:
  1. 模拟 4 通道信号采集 (可调节频率、振幅、噪声)
  2. 实时波形滚动显示
  3. 频谱分析 (FFT)
  4. 统计面板 (均值、标准差、峰峰值)
  5. 参数可调 (ParameterTree)
  6. Dock 可停靠面板布局

运行方式:
  python unit_10_capstone.py
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore


class SignalGenerator:
    def __init__(self, num_channels=4, buffer_size=1000):
        self.num_channels = num_channels
        self.buffer_size = buffer_size
        self.step = 0

        # 每个通道独立的参数
        self.freqs = [1.0, 2.5, 5.0, 0.5]
        self.amps = [1.0, 0.8, 0.6, 0.4]
        self.noise_levels = [0.1, 0.1, 0.1, 0.1]
        self.wave_types = ['sin', 'sin', 'cos', 'sinc']

        # 环形缓冲区
        self.buffers = [np.zeros(buffer_size) for _ in range(num_channels)]

    def set_channel_params(self, ch, freq=None, amp=None,
                           noise=None, wave_type=None):
        if freq is not None:
            self.freqs[ch] = freq
        if amp is not None:
            self.amps[ch] = amp
        if noise is not None:
            self.noise_levels[ch] = noise
        if wave_type is not None:
            self.wave_types[ch] = wave_type

    def update(self):
        self.step += 1
        for ch in range(self.num_channels):
            freq = self.freqs[ch]
            amp = self.amps[ch]
            noise = self.noise_levels[ch]
            wtype = self.wave_types[ch]

            t = self.step * 0.01
            if wtype == 'sin':
                val = amp * np.sin(2 * np.pi * freq * t)
            elif wtype == 'cos':
                val = amp * np.cos(2 * np.pi * freq * t)
            elif wtype == 'square':
                val = amp * np.sign(np.sin(2 * np.pi * freq * t))
            elif wtype == 'sawtooth':
                val = amp * (2 * (freq * t % 1) - 1)
            elif wtype == 'sinc':
                x = (t - self.step * 0.005) * freq * 5
                if abs(x) < 1e-10:
                    val = amp
                else:
                    val = amp * np.sin(x) / x
            else:
                val = amp * np.sin(2 * np.pi * freq * t)

            val += np.random.normal(0, noise)

            # 滚动缓冲区
            self.buffers[ch][:-1] = self.buffers[ch][1:]
            self.buffers[ch][-1] = val

        return self.buffers


class CapstoneApp:
    def __init__(self):
        self.app = pg.mkQApp("实战: 多通道信号采集分析器")
        pg.setConfigOptions(antialias=True)

        self.num_channels = 4
        self.buffer_size = 1000
        self.sample_rate = 100  # Hz

        self.generator = SignalGenerator(
            num_channels=self.num_channels,
            buffer_size=self.buffer_size
        )

        self.build_ui()
        self.start_timer()

    def build_ui(self):
        self.main_win = QtWidgets.QMainWindow()
        self.main_win.setWindowTitle(
            "pyqtgraph 实战: 多通道信号采集与实时分析器")
        self.main_win.resize(1400, 900)

        area = pg.dockarea.DockArea()
        self.main_win.setCentralWidget(area)

        # ---- Dock 1: 波形显示 (4通道) ----
        self.wave_dock = pg.dockarea.Dock(
            "实时波形 (4通道)", size=(900, 500))

        self.wave_widget = pg.GraphicsLayoutWidget()
        self.wave_widget.ci.layout.setSpacing(0)

        self.wave_plots = []
        self.wave_curves = []
        self.threshold_lines = []

        channel_colors = ['#00FFFF', '#FF8800', '#00FF00', '#FF00FF']
        self.x_axis = np.arange(self.buffer_size)

        for ch in range(self.num_channels):
            row = ch // 2
            col = ch % 2

            p = self.wave_widget.addPlot(
                title=f"通道 {ch + 1}", row=row, col=col)
            p.setLabel('left', 'V')
            p.setYRange(-3, 3)

            # 隐藏坐标轴标签减少视觉干扰
            if row == 0:
                p.hideAxis('bottom')

            curve = p.plot(
                self.x_axis,
                np.zeros(self.buffer_size),
                pen=pg.mkPen(channel_colors[ch], width=1)
            )

            # 阈值线
            thr_line = pg.InfiniteLine(
                pos=0, angle=0, movable=False,
                pen=pg.mkPen('r',
                             style=pg.QtCore.Qt.PenStyle.DashLine))
            p.addItem(thr_line)

            self.wave_plots.append(p)
            self.wave_curves.append(curve)
            self.threshold_lines.append(thr_line)

        self.wave_dock.addWidget(self.wave_widget)

        # ---- Dock 2: FFT 频谱分析 ----
        self.fft_dock = pg.dockarea.Dock("频谱分析", size=(350, 500))

        self.fft_widget = pg.GraphicsLayoutWidget()

        self.fft_plots = []
        self.fft_curves = []

        freq_axis = np.fft.rfftfreq(
            self.buffer_size, d=1.0 / self.sample_rate)

        for ch in range(self.num_channels):
            p = self.fft_widget.addPlot(
                title=f"Ch{ch + 1} FFT", row=ch, col=0)
            p.setLabel('left', '|X|')
            p.setLogMode(x=False, y=True)

            if ch < self.num_channels - 1:
                p.hideAxis('bottom')

            curve = p.plot(freq_axis, np.zeros(len(freq_axis)),
                           pen=pg.mkPen(channel_colors[ch], width=1))
            p.setXRange(0, self.sample_rate / 2)

            self.fft_plots.append(p)
            self.fft_curves.append(curve)

        self.fft_dock.addWidget(self.fft_widget)

        # ---- Dock 3: 统计面板 ----
        self.stat_dock = pg.dockarea.Dock("统计信息", size=(350, 300))

        self.stat_table = QtWidgets.QTableWidget()
        self.stat_table.setColumnCount(5)
        self.stat_table.setHorizontalHeaderLabels(
            ['通道', '均值', '标准差', '峰峰值', '过零点数'])
        self.stat_table.setRowCount(self.num_channels)
        for ch in range(self.num_channels):
            self.stat_table.setItem(
                ch, 0, QtWidgets.QTableWidgetItem(f"Ch{ch + 1}"))
        self.stat_dock.addWidget(self.stat_table)

        # ---- Dock 4: 参数控制 ----
        self.ctrl_dock = pg.dockarea.Dock("参数控制", size=(350, 400))

        ctrl_widget = QtWidgets.QWidget()
        ctrl_layout = QtWidgets.QVBoxLayout()
        ctrl_widget.setLayout(ctrl_layout)

        # 通道选择
        ch_label = QtWidgets.QLabel("选择通道:")
        ctrl_layout.addWidget(ch_label)
        self.ch_selector = QtWidgets.QComboBox()
        self.ch_selector.addItems([f"通道 {i + 1}" for i in range(
            self.num_channels)])
        ctrl_layout.addWidget(self.ch_selector)

        # 使用参数树
        from pyqtgraph.parametertree import Parameter, ParameterTree

        params = [
            {'name': '信号参数', 'type': 'group', 'children': [
                {'name': '幅值', 'type': 'float', 'value': 1.0,
                 'limits': (0.1, 3.0), 'step': 0.1},
                {'name': '频率 (Hz)', 'type': 'float', 'value': 1.0,
                 'limits': (0.1, 20.0), 'step': 0.1},
                {'name': '波形类型', 'type': 'list',
                 'values': ['sin', 'cos', 'square', 'sawtooth', 'sinc'],
                 'value': 'sin'},
                {'name': '噪声水平', 'type': 'float', 'value': 0.1,
                 'limits': (0.0, 1.0), 'step': 0.01},
            ]},
            {'name': '触发设置', 'type': 'group', 'children': [
                {'name': '启用触发', 'type': 'bool', 'value': True},
                {'name': '触发电平', 'type': 'float', 'value': 0.0,
                 'limits': (-3, 3), 'step': 0.1},
            ]},
        ]

        self.param_obj = Parameter.create(
            name='设置', type='group', children=params)
        self.param_tree = ParameterTree()
        self.param_tree.setParameters(self.param_obj, showTop=False)
        ctrl_layout.addWidget(self.param_tree)

        # 信号连接: 通道选择改变时更新参数树的值
        self.ch_selector.currentIndexChanged.connect(self.on_channel_changed)
        self.param_obj.sigTreeStateChanged.connect(self.on_params_changed)

        # 保存按钮
        btn_save = QtWidgets.QPushButton("导出当前快照数据")
        ctrl_layout.addWidget(btn_save)
        btn_save.clicked.connect(self.export_data)

        # 暂停按钮
        self.btn_pause = QtWidgets.QPushButton("暂停")
        self.btn_pause.setCheckable(True)
        ctrl_layout.addWidget(self.btn_pause)

        ctrl_layout.addStretch()
        self.ctrl_dock.addWidget(ctrl_widget)

        # ---- 布局 ----
        area.addDock(self.wave_dock, 'left')
        area.addDock(self.fft_dock, 'right', self.wave_dock)
        area.addDock(self.ctrl_dock, 'bottom', self.fft_dock)
        area.addDock(self.stat_dock, 'above', self.ctrl_dock)

        self.main_win.show()

    def start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

    def on_channel_changed(self, idx):
        gen = self.generator
        self.param_obj.sigTreeStateChanged.disconnect(
            self.on_params_changed)

        sig_group = self.param_obj.child('信号参数')
        sig_group.child('幅值').setValue(gen.amps[idx])
        sig_group.child('频率 (Hz)').setValue(gen.freqs[idx])
        sig_group.child('波形类型').setValue(gen.wave_types[idx])
        sig_group.child('噪声水平').setValue(gen.noise_levels[idx])

        self.param_obj.sigTreeStateChanged.connect(
            self.on_params_changed)

    def on_params_changed(self, param, changes):
        idx = self.ch_selector.currentIndex()

        amp = self.param_obj.child('信号参数', '幅值').value()
        freq = self.param_obj.child('信号参数', '频率 (Hz)').value()
        wtype = self.param_obj.child('信号参数', '波形类型').value()
        noise = self.param_obj.child('信号参数', '噪声水平').value()

        self.generator.set_channel_params(
            idx, freq=freq, amp=amp, noise=noise, wave_type=wtype
        )

        trigger = self.param_obj.child('触发设置', '启用触发').value()
        level = self.param_obj.child('触发设置', '触发电平').value()
        if trigger:
            self.threshold_lines[idx].setPos(level)
            self.threshold_lines[idx].setVisible(True)
        else:
            self.threshold_lines[idx].setVisible(False)

    def update(self):
        if self.btn_pause.isChecked():
            return

        buffers = self.generator.update()

        # 更新波形显示
        for ch in range(self.num_channels):
            self.wave_curves[ch].setData(self.x_axis, buffers[ch])

        # 更新 FFT (每 5 帧更新一次以节省 CPU)
        if self.generator.step % 5 == 0:
            for ch in range(self.num_channels):
                window = np.hanning(self.buffer_size)
                signal = buffers[ch] * window
                fft = np.abs(np.fft.rfft(signal))
                self.fft_curves[ch].setData(
                    np.fft.rfftfreq(self.buffer_size,
                                    d=1.0 / self.sample_rate),
                    fft
                )

        # 更新统计 (每 10 帧)
        if self.generator.step % 10 == 0:
            for ch in range(self.num_channels):
                data = buffers[ch]
                mean_val = data.mean()
                std_val = data.std()
                pk_pk = data.max() - data.min()

                zero_crossings = np.sum(
                    np.diff(np.signbit(data - np.mean(data))))

                self.stat_table.setItem(
                    ch, 1, QtWidgets.QTableWidgetItem(f"{mean_val:.4f}"))
                self.stat_table.setItem(
                    ch, 2, QtWidgets.QTableWidgetItem(f"{std_val:.4f}"))
                self.stat_table.setItem(
                    ch, 3, QtWidgets.QTableWidgetItem(f"{pk_pk:.4f}"))
                self.stat_table.setItem(
                    ch, 4, QtWidgets.QTableWidgetItem(
                        f"{zero_crossings}"))

    def export_data(self):
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self.main_win, "保存数据", "", "CSV (*.csv);;NumPy (*.npy)")

        if fname[0]:
            data = np.column_stack([
                np.arange(self.buffer_size)
            ] + self.generator.buffers)
            if fname[0].endswith('.npy'):
                np.save(fname[0], data)
            else:
                header = 'sample,' + ','.join(
                    [f'ch{i + 1}' for i in range(self.num_channels)])
                np.savetxt(fname[0], data, delimiter=',',
                           header=header, comments='')

    def run(self):
        pg.exec()


if __name__ == '__main__':
    capstone = CapstoneApp()
    capstone.run()
