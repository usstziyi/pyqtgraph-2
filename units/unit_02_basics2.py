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
# 4. 不依赖 pg.plot()：手动创建 PlotWidget
#    - 适合在自定义 GUI 中嵌入
#    - PlotWidget 本质是 QGraphicsView + PlotItem 的组合
# ---------------------------------------------------------------------------
# 创建一个独立窗口，设置窗口标题和大小
win = pg.GraphicsLayoutWidget(title="4. 手动创建控件")
win.resize(800, 500)

# addPlot() 在 GraphicsLayoutWidget 中添加 PlotItem
# row, col 指定网格位置
plot = win.addPlot(title="手动创建的 PlotItem")
x = np.linspace(0, 5, 100)
plot.plot(x, np.sin(x), pen='g', name='sin')

# 设置坐标轴标签
plot.setLabel('left', '幅值')
plot.setLabel('bottom', '时间', units='s')

win.show()


# ---------------------------------------------------------------------------
# 启动 Qt 事件循环
#    - exec() 进入事件循环，程序在此等待用户交互
#    - 关闭所有窗口后退出循环
# ---------------------------------------------------------------------------
pg.exec()
