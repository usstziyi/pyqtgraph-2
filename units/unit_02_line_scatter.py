"""
Unit 2: 线条与散点图
====================
学习目标:
  1. 深入理解 PlotDataItem —— pyqtgraph 的核心数据类
  2. 掌握线图 (curve) 和散点图 (scatter) 的组合使用
  3. 了解 PlotCurveItem 和 ScatterPlotItem
  4. 使用 symbol、symbolPen、symbolBrush、symbolSize
  5. 了解 fillLevel / fillBrush 填充功能
  6. 认识 connect 参数控制连线行为
  7. 处理 NaN 值

核心概念:
  PlotDataItem = PlotCurveItem (连线) + ScatterPlotItem (散点)
  可以只显示连线 (默认)、只显示散点、或同时显示两者
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 2: 线条与散点图")

# ---------------------------------------------------------------------------
# 1. 线图与散点图的分离控制
# ---------------------------------------------------------------------------
win = pg.GraphicsLayoutWidget(title="Unit 2: 线条与散点图", show=True)
win.resize(1000, 800)

# ---------------------------------------------------------------------------
# 1a. 默认: 只有线条，无散点
# ---------------------------------------------------------------------------
p1 = win.addPlot(title="1a. 默认: 只有线条 (pen)", row=0, col=0)
x = np.linspace(0, 10, 30)
p1.plot(x, np.sin(x), pen='y')

# ---------------------------------------------------------------------------
# 1b. pen=None: 只有散点，无线条
# ---------------------------------------------------------------------------
p2 = win.addPlot(title="1b. pen=None: 只有散点", row=0, col=1)
p2.plot(x, np.sin(x), pen=None, symbol='o', symbolSize=8, symbolBrush='y')

# ---------------------------------------------------------------------------
# 1c. 同时显示线条和散点
# ---------------------------------------------------------------------------
p3 = win.addPlot(title="1c. 线条 + 散点", row=1, col=0)
p3.plot(x, np.sin(x), pen='c', symbol='d', symbolSize=6, symbolBrush='w')

# ---------------------------------------------------------------------------
# 1d. 不同散点符号
#    - 支持的符号: 'o' 圆, 's' 方, 't' 三角, 'd' 菱形, '+' 加号,
#      'x' 叉号, 't1' 倒三角, 't2' 右三角, 't3' 左三角, 'p' 五角星,
#      'h' 六边形, 'star' 星形, 'arrow_' 系列箭头
# ---------------------------------------------------------------------------
p4 = win.addPlot(title="1d. 不同符号类型", row=1, col=1)
symbols = ['o', 's', 't', 'd', '+', 'x', 'star']
x = np.arange(len(symbols)) + 1
for i, sym in enumerate(symbols):
    p4.plot([i + 1], [1], pen=None, symbol=sym, symbolSize=15,
            symbolBrush=(i * 30, 200 - i * 30, i * 30), name=sym)

# ---------------------------------------------------------------------------
# 2. 逐点定制: 为每个点指定不同的样式
#    - symbol 可传列表: 每个点不同符号
#    - symbolBrush 可传列表: 每个点不同填充色
#    - symbolSize 可传列表: 每个点不同大小
# ---------------------------------------------------------------------------
p5 = win.addPlot(title="2. 逐点定制样式", row=2, col=0)
x = np.arange(10)
y = np.random.normal(size=10)
sizes = np.linspace(5, 25, 10)
colors = np.linspace(0, 255, 10).astype(int)
brushes = [pg.mkBrush(r, g, 0) for r, g in zip(colors, 255 - colors)]
p5.plot(x, y, pen=None, symbol='o', symbolSize=sizes, symbolBrush=brushes)

# ---------------------------------------------------------------------------
# 3. fillLevel: 曲线与指定水平线之间填充
#    - fillLevel=0: 填充曲线下方到 y=0 的区域
#    - fillBrush 指定填充画笔
# ---------------------------------------------------------------------------
p6 = win.addPlot(title="3. fillLevel 填充", row=2, col=1)
x = np.linspace(0, 4 * np.pi, 200)
y = np.sin(x)
p6.plot(x, y, pen='w')
curve = p6.plot(x, y, pen='g', fillLevel=0,
                fillBrush=(0, 255, 0, 80))

# ---------------------------------------------------------------------------
# 4. connect 参数: 控制连线行为
#    - 'auto' (默认) : 遇到 NaN 自动断开
#    - 'all' : 忽略 NaN，强制连接所有点
#    - 'finite' : 同 auto
#    - 'pairs' : 每两个点组成一对线段
# ---------------------------------------------------------------------------
p7 = win.addPlot(title="4a. connect='auto' (NaN断开)", row=3, col=0)
x = np.linspace(0, 10, 100)
y_with_nan = np.sin(x).copy()
y_with_nan[40:60] = np.nan  # 插入 NaN 制造断点
p7.plot(x, y_with_nan, pen='y')

p8 = win.addPlot(title="4b. connect='all' (忽略NaN)", row=3, col=1)
p8.plot(x, y_with_nan, pen='r')
curve_all = p8.plot(x, y_with_nan, pen='r', connect='all')

# ---------------------------------------------------------------------------
# 5. stepMode: 阶梯图
#    - 'left': 左阶梯
#    - 'right': 右阶梯
#    - 'center': 居中阶梯 (常用于直方图，需 len(x)=len(y)+1)
# ---------------------------------------------------------------------------
p9 = win.addPlot(title="5. stepMode 阶梯图", row=4, col=0)
x_step = np.arange(10)
y_step = np.random.randint(1, 10, size=10)
p9.plot(x_step, y_step, pen='c', symbol='o')
p9.plot(x_step, y_step, pen='y', stepMode='right')

# ---------------------------------------------------------------------------
# 6. scatterPlot: 纯散点图的便捷方法
#    - PlotItem.scatterPlot() 等价于 plot(pen=None, ...)
#    - 简化的参数: size 代替 symbolSize, brush 代替 symbolBrush
# ---------------------------------------------------------------------------
p10 = win.addPlot(title="6. scatterPlot 便捷方法", row=4, col=1)
n = 200
x_rand = np.random.normal(size=n)
y_rand = np.random.normal(size=n)
p10.scatterPlot(x_rand, y_rand, size=5,
                brush=pg.mkBrush(100, 100, 255, 120))

pg.exec()
