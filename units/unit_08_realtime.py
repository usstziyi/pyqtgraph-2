"""
Unit 8: 实时数据可视化
=====================
学习目标:
  1. 使用 QTimer 实现定时刷新
  2. 使用 setData() 增量更新数据 (比 plot() 重复创建更高效)
  3. 理解性能优化: downsampling, clipToView, skipFiniteCheck
  4. 滚动更新 (rolling update) 的技巧
  5. 构建实时性能基准测试
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

app = pg.mkQApp("Unit 8: 实时数据可视化")

# ---------------------------------------------------------------------------
# 1. QTimer 驱动的实时曲线 (最简单方式)
# ---------------------------------------------------------------------------
win1 = pg.GraphicsLayoutWidget(title="1. 实时正弦波 (QTimer)", show=True)
win1.resize(800, 400)

p1 = win1.addPlot(title="实时数据: QTimer")
p1.setLabel('left', '数值')
p1.setLabel('bottom', '样本点')

# 预分配数据缓冲区
buffer_size = 500
data = np.zeros(buffer_size)
x_data = np.arange(buffer_size)

# 创建曲线
curve1 = p1.plot(x_data, data, pen='y')

ptr = 0  # 数据写入位置指针


def update1():
    global ptr
    # ptr = (ptr + 1) % buffer_size 是 赋值 ，如果不加 global ，
    # Python 会在函数内部创建一个叫 ptr 的局部变量，外层的 ptr 始终为 0，永远不会变。
    data[ptr] = np.sin(ptr * 0.1) + np.random.normal(0, 0.1)
    ptr = (ptr + 1) % buffer_size
    curve1.setData(x_data, data)


timer1 = QtCore.QTimer()
timer1.timeout.connect(update1)
timer1.start(20)  # 每 20ms 更新一次 (50 FPS)


# ---------------------------------------------------------------------------
# 2. 环形缓冲区滚动更新
#    - 新数据从右侧进入，旧数据从左侧移出
#    - 适合持续监测场景
# ---------------------------------------------------------------------------
win2 = pg.GraphicsLayoutWidget(title="2. 环形缓冲区滚动更新", show=True)
win2.resize(800, 400)

p2 = win2.addPlot(title="环形缓冲区: 滚动更新")
p2.setLabel('left', '数值')

signal_freq = 2.0           # 源信号频率 (Hz)
signal_amp = 1.0           # 信号幅度
time_interval = 50          # 采样间隔 (ms)
dt = time_interval / 1000.0  # 转为秒
fs = 1.0 / dt               # 采样率 (Hz)

history_len = 300
x_time = np.arange(history_len) * dt   # X 轴: 真实时间 (秒)
y2 = np.zeros(history_len)
curve2 = p2.plot(x_time, y2, pen='c')

p2.setLabel('bottom', '时间', units='s')

step = 0

def update2():
    global step, y2
    t = step * dt                         # 当前采样时刻
    y2[:-1] = y2[1:]                      # 左移
    y2[-1] = signal_amp * np.sin(2 * np.pi * signal_freq * t)
    step += 1
    curve2.setData(x_time, y2)


timer2 = QtCore.QTimer()
timer2.timeout.connect(update2)
timer2.start(time_interval)


# ---------------------------------------------------------------------------
# 3. 性能优化: 批量更新 + downsampling
#    - 一次性更新 N 个数据点，而非逐个更新
#    - 使用 downsampling 减少绘制点数
# ---------------------------------------------------------------------------
win3 = pg.GraphicsLayoutWidget(title="3. 批量更新 + downsampling", show=True)
win3.resize(800, 400)

p3 = win3.addPlot(title="批量更新 (每 100ms 更新 50 个点)")
p3.setLabel('left', '数值')

total_size = 5000
x3 = np.arange(total_size)
y3 = np.zeros(total_size)

# 使用 setDownsampling 设置自动降采样 (避免直接传 autoDownsample/clipToView 在某些版本的兼容问题)
curve3 = p3.plot(x3, y3, pen='y')
p3.setDownsampling(auto=True, mode='peak')

idx = 0


def update3():
    global idx, y3
    # 批量生成 50 个新数据点
    chunk = 50
    y3[idx:idx + chunk] = np.sin(np.arange(chunk) * 0.1 + idx * 0.01)
    y3[idx:idx + chunk] += np.random.normal(0, 0.05, size=chunk)

    idx = (idx + chunk) % (total_size - chunk)
    if idx == 0:
        y3[:] = 0  # 回绕时清空

    curve3.setData(x3, y3)


timer3 = QtCore.QTimer()
timer3.timeout.connect(update3)
timer3.start(100)


# ---------------------------------------------------------------------------
# 4. 多通道实时显示
# ---------------------------------------------------------------------------
win4 = pg.GraphicsLayoutWidget(title="4. 多通道实时显示", show=True)
win4.resize(900, 600)

num_channels = 4
buffer_len = 400

channels = []
curves = []
plots = []

for ch in range(num_channels):
    p = win4.addPlot(title=f"通道 {ch + 1}", row=ch // 2, col=ch % 2)
    p.setLabel('left', f'Ch{ch + 1}')
    if ch >= num_channels - 2:
        p.setLabel('bottom', '样本')

    x4 = np.arange(buffer_len)
    y4 = np.zeros(buffer_len)

    color = pg.mkColor(ch * 60, 200 - ch * 40, 150)
    curve = p.plot(x4, y4, pen=color)

    channels.append(y4)
    curves.append(curve)
    plots.append(p)

step4 = 0


def update4():
    global step4
    for ch in range(num_channels):
        # 滚动
        channels[ch][:-1] = channels[ch][1:]
        channels[ch][-1] = (np.sin(step4 * 0.05 * (ch + 1))
                            + np.cos(step4 * 0.03 * (ch + 1))
                            + np.random.normal(0, 0.1))
    step4 += 1

    for ch in range(num_channels):
        curves[ch].setData(np.arange(buffer_len), channels[ch])


timer4 = QtCore.QTimer()
timer4.timeout.connect(update4)
timer4.start(30)


# ---------------------------------------------------------------------------
# 5. 实时直方图
# ---------------------------------------------------------------------------
win5 = pg.GraphicsLayoutWidget(title="5. 实时直方图", show=True)
win5.resize(600, 400)

p5 = win5.addPlot(title="实时直方图")
p5.setLabel('left', '频率')

# 累积分布数据
data_buf = np.random.normal(0, 1, size=2000)
hist_data = np.zeros(50)
x_bins = np.linspace(-4, 4, 51)

# 使用 BarGraphItem 绘制直方图
bar = pg.BarGraphItem(x=x_bins[:-1], height=hist_data,
                      width=0.15, brush='c')
p5.addItem(bar)


def update5():
    global data_buf
    # 添加新数据并回绕
    data_buf[:-10] = data_buf[10:]
    data_buf[-10:] = np.random.normal(0, 1, 10)

    hist, _ = np.histogram(data_buf, bins=50, range=(-4, 4))
    bar.setOpts(height=hist)


timer5 = QtCore.QTimer()
timer5.timeout.connect(update5)
timer5.start(100)


# ---------------------------------------------------------------------------
# 6. FPS 性能监控
#    - 跟踪实际刷新帧率
# ---------------------------------------------------------------------------
win6 = pg.GraphicsLayoutWidget(title="6. FPS 性能监控", show=True)
win6.resize(600, 200)

p6 = win6.addPlot(title="帧率 (FPS)")
p6.setLabel('left', 'FPS')
p6.setLabel('bottom', '时间 (s)')
p6.setYRange(0, 80)

fps_history = np.zeros(200)
fps_x = np.arange(200)
fps_curve = p6.plot(fps_x, fps_history, pen='g')

last_time = QtCore.QElapsedTimer()
last_time.start()
frame_count = 0
fps_ptr = 0

fps_text = pg.TextItem("FPS: 0", color='y', anchor=(0, 1))
fps_text.setPos(0, 70)
p6.addItem(fps_text)


def update_fps():
    global frame_count, fps_ptr

    frame_count += 1
    elapsed = last_time.elapsed()

    if elapsed >= 500:  # 每 500ms 计算一次 FPS
        current_fps = frame_count / (elapsed / 1000.0)

        fps_history[fps_ptr] = current_fps
        fps_ptr = (fps_ptr + 1) % len(fps_history)

        fps_curve.setData(fps_x, fps_history)
        fps_text.setText(f"FPS: {current_fps:.1f}")

        frame_count = 0
        last_time.restart()


timer_fps = QtCore.QTimer()
timer_fps.timeout.connect(update_fps)
timer_fps.start(16)  # 约 60 Hz

pg.exec()
