"""
Unit 7: 信号交互与事件处理
==========================
学习目标:
  1. 理解 Qt 信号槽机制在 pyqtgraph 中的应用
  2. 监听 sigClicked / sigPointsClicked / sigPointsHovered
  3. 利用 sigRangeChanged 联动多个图表
  4. 实现 Crosshair (十字线跟随鼠标)
  5. 自定义鼠标交互
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 7: 信号交互与事件处理")

# ---------------------------------------------------------------------------
# 1. sigClicked: 点击曲线
# ---------------------------------------------------------------------------
win = pg.GraphicsLayoutWidget(title="Unit 7: 信号交互", show=True)
win.resize(1400, 900)

p1 = win.addPlot(title="1. sigClicked: 点击曲线", row=0, col=0)
x = np.linspace(0, 10, 200)
curve1 = p1.plot(x, np.sin(x), pen='y', name='sin',
                 clickable=True, width=3)

p1.addLegend()


def on_curve_clicked(item, ev):
    print(f"曲线被点击: {item.name()}")


curve1.sigClicked.connect(on_curve_clicked)


# ---------------------------------------------------------------------------
# 2. sigPointsClicked: 点击散点
# ---------------------------------------------------------------------------
p2 = win.addPlot(title="2. sigPointsClicked: 点击散点", row=0, col=1)

x_pts = np.random.uniform(0, 10, 50)
y_pts = np.random.uniform(0, 10, 50)

scatter = pg.ScatterPlotItem(x=x_pts, y=y_pts, size=10,
                             brush=pg.mkBrush(100, 200, 100))
p2.addItem(scatter)


def on_points_clicked(item, points, ev):
    for pt in points:
        print(f"散点被点击: pos=({pt.pos().x():.2f}, {pt.pos().y():.2f})")


scatter.sigClicked.connect(on_points_clicked)


# ---------------------------------------------------------------------------
# 3. sigPointsHovered: 鼠标悬停
# ---------------------------------------------------------------------------
p3 = win.addPlot(title="3. sigPointsHovered: 鼠标悬停 (看终端输出)", row=1, col=0)

x_pts2 = np.arange(10)
y_pts2 = np.random.normal(size=10)

hover_curve = p3.plot(x_pts2, y_pts2, pen=None, symbol='o', symbolSize=15,
                      symbolBrush='y')


def on_points_hovered(item, points, ev):
    if points:
        pt = points[0]
        print(f"Hover: pos=({pt.pos().x():.1f}, {pt.pos().y():.3f})")


hover_curve.sigPointsHovered.connect(on_points_hovered)


# ---------------------------------------------------------------------------
# 4. Crosshair: 十字线跟随鼠标
#    - 使用 InfiniteLine + sigRangeChanged 或鼠标事件
#    - 更简洁的方式: 使用 ScatterPlotItem 的 hover 信号更新
# ---------------------------------------------------------------------------
p4 = win.addPlot(title="4. Crosshair 十字线", row=1, col=1)
x = np.linspace(0, 10, 300)
p4.plot(x, np.sin(x) * 5 + 5, pen='c')

vline = pg.InfiniteLine(angle=90, movable=False, pen='y')
hline = pg.InfiniteLine(angle=0, movable=False, pen='y')
p4.addItem(vline)
p4.addItem(hline)

# 用于 hover 跟踪的文本
hover_text = pg.TextItem("", anchor=(0.5, 1), color='y')
p4.addItem(hover_text)


def mouse_moved(pos):
    # sigMouseMoved 直接发射 QPointF，不是元组
    if p4.sceneBoundingRect().contains(pos):
        mouse_point = p4.vb.mapSceneToView(pos)
        x_val = mouse_point.x()
        y_val = mouse_point.y()

        # 检查是否在数据范围内
        if 0 <= x_val <= 10:
            vline.setPos(x_val)
            hline.setPos(y_val)
            hover_text.setPos(x_val, y_val)
            hover_text.setText(f"({x_val:.2f}, {y_val:.2f})")


# 用 Proxy 监听场景鼠标移动
p4.scene().sigMouseMoved.connect(mouse_moved)


# ---------------------------------------------------------------------------
# 5. sigRangeChanged: 区间变化联动
#    - 用于在多个图之间同步缩放
# ---------------------------------------------------------------------------
p5 = win.addPlot(title="5. sigRangeChanged 联动 (主控)", row=2, col=0)
p6 = win.addPlot(title="5. 跟随 (从控)", row=2, col=1)

x = np.linspace(0, 100, 2000)
p5.plot(x, np.sin(x * 0.2) + np.random.normal(0, 0.1, size=2000), pen='y')
p6.plot(x, np.cos(x * 0.2), pen='c')

# 在 p5 上叠加 FFT 分析
p6.setLabel('left', 'Cos')
p6.setLabel('bottom', '时间')


def on_range_changed(vb, ranges):
    print(f"范围改变: X=[{ranges[0][0]:.2f}, {ranges[0][1]:.2f}], "
          f"Y=[{ranges[1][0]:.2f}, {ranges[1][1]:.2f}]")


p5.sigRangeChanged.connect(on_range_changed)


# ---------------------------------------------------------------------------
# 6. 鼠标右键菜单禁用 / 自定义
# ---------------------------------------------------------------------------
p7 = win.addPlot(title="6. 禁用了右键菜单", row=3, col=0)
p7.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 20, 100)), pen='m')


# 可以用 setMenuEnabled 来控制
class NoMenuViewBox(pg.ViewBox):
    def raiseContextMenu(self, ev):
        pass  # 不弹出菜单


# ---------------------------------------------------------------------------
# 7. 完整事件链示例: 拖拽标记 + 数据统计
# ---------------------------------------------------------------------------
p8 = win.addPlot(title="7. 拖拽区间统计 (观察统计变化)", row=3, col=1)

x = np.linspace(0, 50, 2000)
y = np.sin(x * 0.3) + np.random.normal(0, 0.15, size=2000)
p8.plot(x, y, pen='c')

lr = pg.LinearRegionItem(values=[10, 20])
lr.setZValue(-10)
p8.addItem(lr)

stat_label = pg.TextItem("", anchor=(0, 0), color='w',
                         fill=pg.mkBrush(0, 0, 0, 150))
stat_label.setPos(0, 2)
p8.addItem(stat_label)

# 添加平均线
avg_line = pg.InfiniteLine(angle=0, movable=False,
                           pen=pg.mkPen('r', style=pg.QtCore.Qt.PenStyle.DashLine))
p8.addItem(avg_line)


def update_stats():
    rmin, rmax = lr.getRegion()
    mask = (x >= rmin) & (x <= rmax)
    seg = y[mask]
    if len(seg) > 0:
        mean_val = seg.mean()
        std_val = seg.std()
        stat_label.setText(f"区间 [{rmin:.1f}, {rmax:.1f}]\n"
                           f"均值: {mean_val:.3f}\n"
                           f"标准差: {std_val:.3f}")
        avg_line.setPos(mean_val)


lr.sigRegionChanged.connect(update_stats)
update_stats()

pg.exec()
