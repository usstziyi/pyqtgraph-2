import sys
import time
from threading import Event

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QApplication, QMainWindow


class SineWaveWorker(QObject):
    chunk_ready = Signal(object)
    finished = Signal()

    def __init__(self, frequency, sample_rate, time_interval, parent=None):
        super().__init__(parent)
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.time_interval = time_interval
        self.chunk_size = int(sample_rate * time_interval / 1000)
        self.sample_index = 0
        self._stop_requested = Event()

    @Slot()
    def start(self):
        self._stop_requested.clear()
        interval_seconds = self.time_interval / 1000

        try:
            while not self._stop_requested.is_set():
                started_at = time.perf_counter()
                # 业务逻辑
                self.chunk_ready.emit(self.generate_chunk())

                
                elapsed = time.perf_counter() - started_at
                sleep_seconds = max(0, interval_seconds - elapsed)
                # 使用 threading.Event.wait() 进行可中断的睡眠
                # 与 time.sleep() 不同，wait() 可以在收到 stop() 信号时立即被唤醒
                # 这样既能保持精确的定时周期，又能实现快速响应停止请求
                
                self._stop_requested.wait(sleep_seconds)
                # 半睡眠机制：超时自醒+外部提前唤醒
                # 当 sleep_seconds 时间耗尽后， wait() 自然返回， 返回值为 False （表示未被 set）。
                # 当 self._stop_requested.set() 被调用时， wait() 立即 返回， 返回值为 True 。
        finally:
            # 通知代理人线程
            self.finished.emit()

    @Slot()
    def stop(self):
        self._stop_requested.set()

    def generate_chunk(self):
        new_index = np.arange(
            self.sample_index,
            self.sample_index + self.chunk_size,
        )
        t_new = new_index / self.sample_rate
        y_new = np.sin(2 * np.pi * self.frequency * t_new)

        self.sample_index += self.chunk_size
        return y_new


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

        self.buff = np.zeros(int(self.sample_rate * self.window_seconds))        # 窗口能容纳的点数
        self.t_axis = np.arange(0, self.window_seconds, 1 / self.sample_rate)

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

        self.plot_widget.setXRange(0, self.window_seconds)

        # 曲线
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen("#00FF41", width=2)
        )

        # -----------------------------
        # 后台采样线程
        # -----------------------------
        # 代理人线程
        self.worker_thread = QThread(self)

        self.worker = SineWaveWorker(
            self.frequency,
            self.sample_rate,
            self.time_interval,
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.start)

        self.worker.chunk_ready.connect(self.update_data)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        
        self.worker_thread.start()
        """
        退出方式 谁来处理？ 
        点击窗口关闭按钮 closeEvent → stop_worker() （第 136 行） 
        Cmd+Q / 菜单退出 / 外部终止 aboutToQuit 信号 → stop_worker() （这里）
        """
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop_worker)

    @Slot(object)
    def update_data(self, y_new):
        self.buff[:-self.chunk_size] = self.buff[self.chunk_size:]
        self.buff[-self.chunk_size:] = y_new

        self.curve.setData(self.t_axis, self.buff)

    def closeEvent(self, event):
        self.stop_worker()
        super().closeEvent(event)

    def stop_worker(self):
        if not self.worker_thread.isRunning():
            return

        self.worker.stop()
        self.worker_thread.quit()
        if not self.worker_thread.wait(1000):
            self.worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait(1000)


def main():
    app = QApplication(sys.argv)
    # 启用抗锯齿，使曲线边缘更平滑
    pg.setConfigOptions(antialias=True)
    window = SineWaveDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
