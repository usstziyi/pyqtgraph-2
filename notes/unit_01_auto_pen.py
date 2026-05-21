import sys
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow


class SineWaveDemo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQtGraph 实时正弦波滚动 Demo")
        self.resize(900, 500)

        # -----------------------------
        # 基本参数
        # -----------------------------
        self.frequency = 1.0             # 正弦波频率：1 Hz
        self.sample_rate = 1000          # 采样率：1000 Hz
        self.window_seconds = 5.0        # 屏幕上始终显示最近 5 秒
        self.time_interval = 25         # 定时器间隔25ms
        self.chunk_size = int(self.sample_rate * self.time_interval / 1000)           # 定时器间隔时间应该新生多少个点

        self.sample_index = 0            # 当前已经生成到第几个采样点
        self.buff = np.zeros(int(self.sample_rate * self.window_seconds))        # 窗口能容纳的点数

        # -----------------------------
        # 创建 PlotWidget
        # -----------------------------
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        self.plot_widget.setBackground("k")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        self.plot_widget.setLabel("bottom", "Time", units="s")
        self.plot_widget.setLabel("left", "Amplitude")

        self.plot_widget.setYRange(-1.2, 1.2)

        # 禁止自动缩放，否则它会自己调整坐标范围
        self.plot_widget.enableAutoRange(axis="x", enable=False)
        self.plot_widget.enableAutoRange(axis="y", enable=False)

        self.plot_widget.setXRange(0,self.window_seconds)

        # 曲线
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen("#00FF41", width=2)
        )

        # -----------------------------
        # 定时器
        # -----------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(self.time_interval)   # 每 30 ms 更新一次

    def update_data(self):
        # 本次生成的采样编号
        new_index = np.arange(
            self.sample_index,
            self.sample_index + self.chunk_size
        )

        # 转成时间，单位秒
        t_new = new_index / self.sample_rate

        # 生成正弦波
        y_new = np.sin(2 * np.pi * self.frequency * t_new)

        # 推入buffer
        self.buff[:-self.chunk_size] = self.buff[self.chunk_size:]
        self.buff[-self.chunk_size:] = y_new

        # 更新 sample_index
        self.sample_index += self.chunk_size
        
        # 计算时间轴
        right_index = self.sample_index
        left_index = right_index - int(self.sample_rate * self.window_seconds)
        left_time = left_index/self.sample_rate
        right_time = right_index/self.sample_rate

        # 窗口时间
        t = np.arange(left_index, right_index) / self.sample_rate
        t0 = np.arange(0,self.window_seconds,1/self.sample_rate)

        # 更新曲线
        self.curve.setData(t0,self.buff)
        


        # # 关键：让 X 轴窗口跟着时间移动
        # self.plot_widget.setXRange(
        #     left_time,
        #     right_time,
        #     padding=0
        # )


def main():
    app = QApplication(sys.argv)
    # 启用抗锯齿，使曲线边缘更平滑
    pg.setConfigOptions(antialias=True)
    window = SineWaveDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()