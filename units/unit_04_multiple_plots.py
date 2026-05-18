"""
Unit 4: 多图布局与子图
======================
学习目标:
  1. 使用 GraphicsLayoutWidget 创建网格布局
  2. addPlot() 的 row/col/rowspan/colspan 参数
  3. ViewBox 的 X/Y 轴联动 (setXLink / setYLink)
  4. GraphicsLayout 嵌套
  5. 多个 PlotWidget 的创建和管理
  6. 使用 clear() 和 clearPlots()
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 4: 多图布局与子图")

# ---------------------------------------------------------------------------
# 1. GraphicsLayoutWidget: 网格布局
#    - row, col 指定位置 (从 0 开始)
#    - colspan, rowspan 指定跨越行列数
# ---------------------------------------------------------------------------
win = pg.GraphicsLayoutWidget(title="Unit 4: 多图布局与子图", show=True)
win.resize(1200, 900)

# 第一行: 两个并排图
p1 = win.addPlot(title="1a. 共享数据 - 左上", row=0, col=0)
p2 = win.addPlot(title="1b. 共享数据 - 右上", row=0, col=1)

# 第二行: 一个跨两列的大图
p3 = win.addPlot(title="2. 跨两列的大图", row=1, col=0, colspan=2)

# 第三行: 三个并排图
p4 = win.addPlot(title="3a. 左下", row=2, col=0)
p5 = win.addPlot(title="3b. 中下", row=2, col=1)
p6 = win.addPlot(title="3c. 右下", row=2, col=2)

x = np.linspace(0, 10, 200)
p1.plot(x, np.sin(x), pen='c')
p2.plot(x, np.cos(x), pen='m')
p3.plot(x, np.sin(x) * np.exp(-x / 4), pen='g')

frequencies = [1, 2, 5]
for i, freq in enumerate(frequencies):
    for p in [p4, p5, p6]:
        p.plot(x, np.sin(freq * x), pen=(i * 80, 200 - i * 60, i * 60))


# ---------------------------------------------------------------------------
# 2. ViewBox 联动: setXLink / setYLink
#    - 当一个图的 X 轴缩放时，另一个同步变化
#    - setXLink(plot) 使当前图的 X 轴跟随指定 plot 的 X 轴
# ---------------------------------------------------------------------------
win2 = pg.GraphicsLayoutWidget(title="2. X 轴联动", show=True)
win2.resize(1000, 600)

# 上面的大图（主控）
p_top = win2.addPlot(title="主控 (X 轴驱动者)", row=0, col=0)
p_top.setLabel('bottom', '时间', units='s')

# 下面的两个子图（跟随）
p_bot_left = win2.addPlot(title="跟随 1", row=1, col=0)
p_bot_right = win2.addPlot(title="跟随 2", row=1, col=1)

# 将下面两个图的 X 轴链接到上面
p_bot_left.setXLink(p_top)
p_bot_right.setXLink(p_top)

x = np.linspace(0, 100, 2000)
p_top.plot(x, np.sin(x * 0.5), pen='y')

p_bot_left.plot(x, np.cos(x * 0.5), pen='c')
p_bot_left.setLabel('left', 'Cos')

p_bot_right.plot(x, np.sin(x * 0.5) * np.cos(x * 0.02), pen='m')
p_bot_right.setLabel('left', 'Modulated')


# ---------------------------------------------------------------------------
# 3. Y 轴联动: setYLink
# ---------------------------------------------------------------------------
win3 = pg.GraphicsLayoutWidget(title="3. Y 轴联动", show=True)
win3.resize(800, 500)

p_left = win3.addPlot(title="Y 轴联动 - 左", row=0, col=0)
p_right = win3.addPlot(title="Y 轴联动 - 右", row=0, col=1)
p_right.setYLink(p_left)  # Y 轴联动

x = np.linspace(0, 20, 500)
p_left.plot(x, np.sin(x), pen='g')
p_right.plot(x, np.cos(x), pen='r')


# ---------------------------------------------------------------------------
# 4. 通过 nextRow() / nextCol() 自动换行
# ---------------------------------------------------------------------------
win4 = pg.GraphicsLayoutWidget(title="4. nextRow 自动布局", show=True)
win4.resize(800, 500)

for i in range(3):
    p = win4.addPlot(title=f"Plot {i + 1}", row=i, col=0)
    p.plot(np.random.normal(size=100))
    p.setLabel('left', f'Ch{i + 1}')


# ---------------------------------------------------------------------------
# 5. 清除与重置
#    - clear(): 从 ViewBox 中移除所有项
#    - clearPlots(): 仅移除曲线数据
# ---------------------------------------------------------------------------
win5 = pg.GraphicsLayoutWidget(title="5. 清除演示", show=True)
win5.resize(600, 400)

p_clr = win5.addPlot(title="点击 Auto-Range 后观察")

x = np.linspace(0, 10, 200)
for i in range(5):
    p_clr.plot(x, np.sin(x + i), pen=(i * 50, 200, 200))

# 在另一个窗口展示清除效果
win5b = pg.GraphicsLayoutWidget(title="5b. 清除后重新绘图", show=True)
win5b.resize(600, 400)
p_clr2 = win5b.addPlot(title="已清除并重新绘制")

# 先添加数据
for i in range(5):
    p_clr2.plot(x, np.random.normal(size=200), pen=(i * 50, 200, 200))

# 清除
p_clr2.clearPlots()

# 重新绘制
p_clr2.plot(x, np.sin(x), pen='c', name='new sin')


# ---------------------------------------------------------------------------
# 6. 在 QWidget 中嵌入 PlotWidget
#    - 适合构建自定义 GUI
#    - PlotWidget 是 QWidget 子类，可直接添加到 Qt 布局
# ---------------------------------------------------------------------------
from pyqtgraph.Qt import QtWidgets

win6 = QtWidgets.QMainWindow()
win6.setWindowTitle("6. 在 Qt 窗口中嵌入 PlotWidget")
win6.resize(900, 600)

central = QtWidgets.QWidget()
win6.setCentralWidget(central)
layout = QtWidgets.QVBoxLayout()
central.setLayout(layout)

# 创建 PlotWidget 并添加到布局
pw = pg.PlotWidget(title="嵌入的 PlotWidget")
pw.setLabel('left', '值')
pw.setLabel('bottom', '样本')
pw.plot(np.random.normal(size=200), pen='y')
layout.addWidget(pw)

# 添加一个控制按钮
btn = QtWidgets.QPushButton("添加新曲线")
layout.addWidget(btn)


def add_new_curve():
    pw.plot(np.random.normal(size=200), pen=pg.mkPen(
        np.random.randint(0, 256, 3)))


btn.clicked.connect(add_new_curve)

win6.show()

pg.exec()
