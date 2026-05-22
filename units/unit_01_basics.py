"""
Unit 1: 快速入门 —— 基础绘图
===============================
学习目标:
  1. 理解 pyqtgraph 的核心架构 (PlotWidget, PlotItem, ViewBox, AxisItem)
  2. 用 pg.plot() 快速创建图形窗口
  3. 理解 QApplication 事件循环
  4. 用多种数据格式传入数据

pyqtgraph 架构层次:
  - QApplication : Qt 应用主循环 (每个 Qt 程序必需)
  - PlotWidget (QWidget) : 可在 GUI 中嵌入的绘图控件
    └── PlotItem (GraphicsWidget) : 绘图区 + 坐标轴 + 标题
        ├── ViewBox : 数据区域，支持鼠标缩放/平移
        ├── AxisItem (bottom) : X 轴
        ├── AxisItem (left)   : Y 轴
        └── PlotDataItem : 实际绘制的数据曲线
"""

import numpy as np
import pyqtgraph as pg

# ---------------------------------------------------------------------------
# 1. 创建 QApplication
#    - 每个 Qt 应用必须有一个 QApplication 实例
#    - pg.mkQApp() 会创建或返回已有的 QApplication
#    - sys.argv 允许 Qt 解析命令行参数
# ---------------------------------------------------------------------------
app = pg.mkQApp("Unit 1: 基础绘图")


# ---------------------------------------------------------------------------
# 2. 最简单的绘图: pg.plot(y)
#    - 自动生成 x 轴: np.arange(len(y))
#    - 返回 PlotWidget，可继续添加曲线
#    - 窗口右上角有 "A" 按钮：点击自动缩放
# ---------------------------------------------------------------------------

# 2a. 传入 Python list
data_list = [1, 3, 2, 5, 4, 8, 6, 7]
pw1 = pg.plot(data_list, title="2a. pg.plot(list) - 传入 Python list")
# # 等价于：
# pw = pg.PlotWidget(title="...")
# pw.plot(data_list)
# pw.show()
# pw1 = pg.plot(data1)  # 独立窗口 1，独立 PlotWidget
# pw2 = pg.plot(data2)  # 独立窗口 2，独立 PlotWidget
# pw3 = pg.plot(data3)  # 独立窗口 3，独立 PlotWidget

# 2b. 传入 numpy 数组
data_np = np.array([1, 3, 2, 5, 4, 8, 6, 7])
pw2 = pg.plot(data_np, title="2b. pg.plot(np.array) - 传入 numpy 数组")

# 2c. 同时传入 x 和 y
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)
pw3 = pg.plot(x, y, title="2c. pg.plot(x, y) - 传入 x 和 y")

# 2d. 指定颜色 (pen 参数)
y2 = np.cos(x)
pw4 = pg.plot(x, y2, pen='r', title="2d. pg.plot(x, y, pen='r') - 红色线条")


# ---------------------------------------------------------------------------
# 3. 在同一窗口中添加多条曲线
#    - pg.plot() 返回的 PlotWidget 可以继续调用 .plot()
#    - 每条 .plot() 返回一个 PlotDataItem
# ---------------------------------------------------------------------------
pw_multi = pg.plot(title="3. 多条曲线在同一窗口")
x = np.linspace(0, 10, 200)
pw_multi.plot(x, np.sin(x), pen='c', name='sin(x)')
pw_multi.plot(x, np.cos(x), pen='m', name='cos(x)')
pw_multi.plot(x, np.sin(x) * np.exp(-x / 3), pen='y', name='damped')


# ---------------------------------------------------------------------------
# 启动 Qt 事件循环
#    - exec() 进入事件循环，程序在此等待用户交互
#    - 关闭所有窗口后退出循环
# ---------------------------------------------------------------------------
pg.exec()
