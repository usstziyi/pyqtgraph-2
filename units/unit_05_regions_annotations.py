"""
Unit 5: 区域标注与参考线
=======================
学习目标:
  1. 使用 InfiniteLine 绘制水平和垂直参考线
  2. 使用 LinearRegionItem 创建可拖拽的区间
  3. 使用 TextItem 添加文本标注
  4. 使用 ArrowItem 绘制箭头
  5. 使用 CurvePoint 和 TargetItem
  6. 理解 sigRegionChanged 信号用于区间联动

核心概念:
  - InfiniteLine: 无限延伸的参考线 (垂直/水平/指定角度)
  - LinearRegionItem: 可拖拽的两边界区间选择器 (沿 X 或 Y 轴)
  - TextItem / LabelItem: 标注文本
  - ROI: Region of Interest (更灵活的矩形/圆形选择器)
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 5: 区域标注与参考线")

# ---------------------------------------------------------------------------
# 1. InfiniteLine: 无限参考线
#    - angle=90: 垂直线 (x 位置)
#    - angle=0:  水平线 (y 位置)
#    - movable=True: 可拖拽
#    - label: 可显示标签
#    - pen: 样式
# ---------------------------------------------------------------------------
win = pg.GraphicsLayoutWidget(title="Unit 5: 区域标注与参考线", show=True)
win.resize(1400, 900)

p1 = win.addPlot(title="1. InfiniteLine 参考线", row=0, col=0)
x = np.linspace(0, 10, 500)
y = np.sin(x) * 5 + 5
p1.plot(x, y, pen='c')

# 垂直线，位于 x=3, 可拖拽
vline = pg.InfiniteLine(pos=3, angle=90, movable=True, pen='r', label='x={value:0.2f}')
p1.addItem(vline)

# 水平线，位于 y=5, 可拖拽，带标签
hline = pg.InfiniteLine(pos=5, angle=0, movable=True,
                        pen=pg.mkPen('g', width=2, style=pg.QtCore.Qt.PenStyle.DashLine),
                        label='y={value:0.2f}', labelOpts={'position': 0.9})
p1.addItem(hline)

# 斜线: angle=45
dline = pg.InfiniteLine(pos=(2, 0), angle=45, movable=True,
                        pen=pg.mkPen('y', width=1), label='{value}')
p1.addItem(dline)

# 用 PlotItem.addLine() 快捷方法
p1.addLine(x=7, pen=pg.mkPen('m', width=1, style=pg.QtCore.Qt.PenStyle.DotLine),
                              movable=True, label='x={value:0.2f}')


# ---------------------------------------------------------------------------
# 2. LinearRegionItem: 可拖拽区间选择器
#    - values: 初始区间 (min, max)
#    - orientation: 'horizontal' 或 'vertical'
#    - movable: 可拖拽
#    - sigRegionChanged: 区间变化信号
# ---------------------------------------------------------------------------
p2 = win.addPlot(title="2. LinearRegionItem 区间选择", row=0, col=1)
x = np.linspace(0, 10, 500)
y = np.sin(x * 2) * 3 + 5
p2.plot(x, y, pen='c')

# 创建 X 轴方向的区间选择器
lr = pg.LinearRegionItem(values=[2, 4], orientation='horizontal')
lr.setZValue(-10)  # 放在曲线下方图层
p2.addItem(lr)

# 也可以创建 Y 轴方向的
lr_y = pg.LinearRegionItem(values=[4, 7], orientation='vertical',
                           pen=pg.mkPen('y', width=1),
                           brush=pg.mkBrush(255, 255, 0, 40))
# 固定宽度，不让用户拖拽单条边界线(可选)
lr_y.lines[0].setMovable(False)
lr_y.lines[1].setMovable(False)
p2.addItem(lr_y)


# ---------------------------------------------------------------------------
# 3. 区间联动: 上图选择 -> 下图显示详情
#    - sigRegionChanged 信号携带 region 对象
#    - 通过 getRegion() 获取当前区间
# ---------------------------------------------------------------------------
win2 = pg.GraphicsLayoutWidget(title="3. 区间联动", show=True)
win2.resize(1000, 600)

# 上图: 全览 + 区间选择器
p_overview = win2.addPlot(title="全览 (拖拽区间选择子图数据)", row=0, col=0)
x_ov = np.linspace(0, 100, 5000)
y_ov = np.sin(x_ov) + np.random.normal(0, 0.1, size=5000)
p_overview.plot(x_ov, y_ov, pen='c')

lr3 = pg.LinearRegionItem(values=[20, 40])
lr3.setZValue(-10) # 放在曲线下方图层
p_overview.addItem(lr3)

# 下图: 显示选中区间的详情
p_detail = win2.addPlot(title="选中区间的详情", row=1, col=0)
detail_curve = p_detail.plot(pen='g')


def update_detail():
    """当 LinearRegionItem 区间变化时，更新下图显示"""
    region = lr3.getRegion()  # 返回 (min, max)
    mask = (x_ov >= region[0]) & (x_ov <= region[1])
    detail_curve.setData(x_ov[mask], y_ov[mask])


lr3.sigRegionChanged.connect(update_detail)

# 初始化一次
update_detail()


# ---------------------------------------------------------------------------
# 4. TextItem: 文本标注
#    - 可在数据坐标或像素坐标中定位
#    - anchor: 锚点位置
# ---------------------------------------------------------------------------
p4 = win.addPlot(title="4. TextItem 文本标注", row=1, col=0)
x = np.linspace(0, 10, 200)
p4.plot(x, np.sin(x), pen='y')

text = pg.TextItem(text="峰值", color='r', anchor=(0.5, 0))
text.setPos(np.pi / 2, 1)
p4.addItem(text)

text2 = pg.TextItem(text="谷值", color='g', anchor=(0.5, 1))
text2.setPos(3 * np.pi / 2, -1)
p4.addItem(text2)


# ---------------------------------------------------------------------------
# 5. ArrowItem: 箭头
# ---------------------------------------------------------------------------
p5 = win.addPlot(title="5. ArrowItem 箭头", row=1, col=1)
p5.plot([0, 10], [0, 0], pen='w')

arrow = pg.ArrowItem(angle=45, tipAngle=30, headLen=20, tailLen=30,
                     brush='r', pen='w')
arrow.setPos(5, 0)
p5.addItem(arrow)

arrow2 = pg.ArrowItem(angle=-90, tipAngle=25, headLen=20,
                      tailLen=0, brush='g')
arrow2.setPos(5, 0)
p5.addItem(arrow2)


# ---------------------------------------------------------------------------
# 6. TargetItem: 可拖拽十字线目标
#    - 类似游标，可在曲线上拖动
# ---------------------------------------------------------------------------
p6 = win.addPlot(title="6. TargetItem 十字游标", row=2, col=0)
x = np.linspace(0, 10, 200)
p6.plot(x, np.sin(x), pen='c')

target = pg.TargetItem(pos=(5, 0), movable=True, pen='r')
p6.addItem(target)


# ---------------------------------------------------------------------------
# 7. 综合示例: 用区间选择器对信号进行分段统计
# ---------------------------------------------------------------------------
p7 = win.addPlot(title="7. 区间统计 (拖拽选择查看统计)", row=2, col=1)
x = np.linspace(0, 50, 1000)
y = np.sin(x * 0.3) * 5 + np.random.normal(0, 0.3, size=1000)
p7.plot(x, y, pen='c')

lr_stat = pg.LinearRegionItem(values=[10, 20])
lr_stat.setZValue(-10)
p7.addItem(lr_stat)

# 创建一个 TextItem 显示统计信息
stat_text = pg.TextItem(text="", color='w', anchor=(0, 0),
                        fill=pg.mkBrush(0, 0, 0, 150))
stat_text.setPos(0, 6)
p7.addItem(stat_text)


def update_stat():
    rmin, rmax = lr_stat.getRegion()
    mask = (x >= rmin) & (x <= rmax)
    if mask.sum() > 0:
        seg = y[mask]
        stat_text.setText(
            f"区间: [{rmin:.1f}, {rmax:.1f}]\n"
            f"均值: {seg.mean():.3f}\n"
            f"标准差: {seg.std():.3f}\n"
            f"点数: {mask.sum()}"
        )


lr_stat.sigRegionChanged.connect(update_stat)
update_stat()

pg.exec()
