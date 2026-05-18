"""
Unit 3: 图表美化与定制
======================
学习目标:
  1. 使用 pg.mkPen() / pg.mkColor() / pg.mkBrush() 控制颜色样式
  2. 掌握坐标轴定制: setLabel(), setRange(), setLogMode(), invertY()
  3. 添加标题和图例 (LegendItem)
  4. 网格线 (GridItem)
  5. 全局配置选项: pg.setConfigOptions()
  6. 使用 BarGraphItem 绘制柱状图
  7. 使用 ErrorBarItem 绘制误差条
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 3: 图表美化与定制")

# ---------------------------------------------------------------------------
# 0. 全局配置: setConfigOptions
#    - antialias: 抗锯齿 (True/False)
#    - background: 默认背景色
#    - foreground: 默认前景色
#    - imageAxisOrder: 图像轴顺序 ('row-major' / 'col-major')
# ---------------------------------------------------------------------------
pg.setConfigOptions(antialias=True)

# ---------------------------------------------------------------------------
# 1. mkPen: 创建画笔
#    格式: pg.mkPen(color, width=1, style=...)
#    color 可以传:
#      - 字符串: 'r', 'g', 'b', 'c', 'm', 'y', 'w', 'k'
#      - 元组: (R, G, B) 或 (R, G, B, A) 范围 0-255
#      - 十六进制: '#FF5500'
#      - QColor 对象
#      - 整数 0-15: 对应内置颜色索引
# ---------------------------------------------------------------------------
pen1 = pg.mkPen('r', width=2)                        # 红色, 线宽2
pen2 = pg.mkPen((0, 200, 100), width=3)               # 自定义绿色
pen3 = pg.mkPen('#FF8800', width=1)                   # 橙色
pen4 = pg.mkPen(style=pg.QtCore.Qt.PenStyle.DashLine)  # 虚线
pen5 = pg.mkPen(style=pg.QtCore.Qt.PenStyle.DotLine)   # 点线

# 线宽大于 1 时，pyqtgraph 用 QLine 线段方式绘制以提升性能
# 线宽为 1 时，pyqtgraph 用 QPainterPath 方式绘制 (更快)

brush1 = pg.mkBrush('r')                              # 红色画刷
brush2 = pg.mkBrush(0, 100, 200, 80)                  # 半透明蓝色
brush3 = pg.mkBrush('#FF00FF')                        # 品红色

win = pg.GraphicsLayoutWidget(title="Unit 3: 图表美化与定制", show=True)
win.resize(1200, 900)

# ---------------------------------------------------------------------------
# 2. 坐标轴定制
# ---------------------------------------------------------------------------
p_axis = win.addPlot(title="2. 坐标轴定制", row=0, col=0)
x = np.linspace(0, 10, 200)
p_axis.plot(x, np.sin(x) * 10 + 10, pen=pen1)

p_axis.setLabel('left', '电压', units='V')
p_axis.setLabel('bottom', '时间', units='s')

p_axis.setXRange(0, 10)      # 锁定 X 轴范围
p_axis.setYRange(0, 20)      # 锁定 Y 轴范围

p_axis.showGrid(x=True, y=True, alpha=0.3)

# Y 轴反转 (常用于图像显示)
# p_axis.invertY(True)

# 对数坐标
p_log = win.addPlot(title="2b. 对数坐标", row=0, col=1)
x = np.logspace(-1, 3, 100)
y = x ** 2
p_log.plot(x, y)
p_log.setLogMode(x=True, y=True)

# ---------------------------------------------------------------------------
# 3. 图例 (LegendItem)
#    - PlotItem.addLegend() 添加图例
#    - 绘图时需指定 name 参数
# ---------------------------------------------------------------------------
p_legend = win.addPlot(title="3. 图例", row=1, col=0)
p_legend.addLegend(offset=(-10, 10))  # offset 控制相对左上角的偏移 (像素)

x = np.linspace(0, 10, 200)
p_legend.plot(x, np.sin(x), pen=pen1, name='sin(x)')
p_legend.plot(x, np.cos(x), pen=pen2, name='cos(x)')
p_legend.plot(x, np.sin(2 * x), pen=pen3, name='sin(2x)')

# ---------------------------------------------------------------------------
# 4. 全部 Pen 样式对比
# ---------------------------------------------------------------------------
p_styles = win.addPlot(title="4. Pen 样式对比", row=1, col=1)

styles = [
    ("SolidLine", pg.QtCore.Qt.PenStyle.SolidLine),
    ("DashLine", pg.QtCore.Qt.PenStyle.DashLine),
    ("DotLine", pg.QtCore.Qt.PenStyle.DotLine),
    ("DashDotLine", pg.QtCore.Qt.PenStyle.DashDotLine),
    ("DashDotDotLine", pg.QtCore.Qt.PenStyle.DashDotDotLine),
]

for i, (name, style) in enumerate(styles):
    pen = pg.mkPen('w', style=style, width=2)
    p_styles.plot([0, 10], [i, i], pen=pen)

p_styles.getAxis('left').setTicks(
    [enumerate([s[0] for s in styles])])
p_styles.setYRange(-0.5, len(styles) - 0.5)

# ---------------------------------------------------------------------------
# 5. 阴影笔 (shadowPen): 绘制线条的底层阴影
# ---------------------------------------------------------------------------
p_shadow = win.addPlot(title="5. shadowPen 阴影笔", row=2, col=0)
x = np.linspace(0, 2 * np.pi, 200)
p_shadow.plot(x, np.sin(x), pen='w', name='sin')
p_shadow.plot(x, np.cos(x), pen='c', shadowPen=pg.mkPen('w', width=6),
              name='cos with shadow')

# ---------------------------------------------------------------------------
# 6. BarGraphItem: 柱状图
# ---------------------------------------------------------------------------
p_bar = win.addPlot(title="6. BarGraphItem 柱状图", row=2, col=1)
categories = ['A', 'B', 'C', 'D', 'E']
values = np.array([23, 45, 56, 78, 32])

bar_graph = pg.BarGraphItem(
    x=np.arange(len(categories)), height=values, width=0.6, brushes=[
        pg.mkBrush(r, g, 0)
        for r, g in zip(np.linspace(100, 255, 5).astype(int),
                        np.linspace(200, 50, 5).astype(int))
    ]
)
p_bar.addItem(bar_graph)

axis = p_bar.getAxis('bottom')
axis.setTicks([list(enumerate(categories))])

# ---------------------------------------------------------------------------
# 7. ErrorBarItem: 误差条图
# ---------------------------------------------------------------------------
p_err = win.addPlot(title="7. ErrorBarItem 误差条", row=3, col=0)
x = np.arange(5)
y = np.array([10, 15, 13, 17, 12])
errors = np.array([1.0, 0.5, 2.0, 1.5, 0.8])

p_err.plot(x, y, pen=None, symbol='o', symbolSize=10, symbolBrush='y')

err_item = pg.ErrorBarItem(x=x, y=y, height=errors,
                           beam=0.5, pen=pg.mkPen('r', width=2))
p_err.addItem(err_item)

# ---------------------------------------------------------------------------
# 8. FillBetweenItem: 两条曲线之间填充
# ---------------------------------------------------------------------------
p_fill = win.addPlot(title="8. FillBetweenItem 曲线间填充", row=3, col=1)
x = np.linspace(0, 10, 200)
y1 = np.sin(x) + 1
y2 = np.cos(x) + 1

curve1 = p_fill.plot(x, y1, pen='b')
curve2 = p_fill.plot(x, y2, pen='r')

fill = pg.FillBetweenItem(curve1, curve2, brush=pg.mkBrush(100, 100, 255, 80))
p_fill.addItem(fill)

# ---------------------------------------------------------------------------
# 9. 直接使用 setConfigOptions 修改外观
# ---------------------------------------------------------------------------
p_theme = win.addPlot(title="9. 外观示例", row=4, col=0, colspan=2)
x = np.linspace(0, 50, 1000)
p_theme.plot(x, np.sin(x) * np.exp(-x / 15), pen=pg.mkPen('c', width=2))
p_theme.setLabel('left', 'Signal')
p_theme.setLabel('bottom', 'Time')

# 背景网格
p_theme.showGrid(x=True, y=True, alpha=0.5)

pg.exec()
