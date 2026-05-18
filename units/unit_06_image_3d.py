"""
Unit 6: 图像显示与 3D 图形
==========================
学习目标:
  1. 使用 pg.image() 快速显示图像
  2. 使用 ImageItem 和 PlotItem 显示带坐标轴的图像
  3. 使用 ImageView 进行交互式图像查看 (含直方图/色阶调整)
  4. 使用 ColorBarItem 添加色阶条
  5. 使用 HistogramLUTItem 控制色阶
  6. 3D 图形: GLViewWidget + GLLinePlotItem / GLScatterPlotItem / GLSurfacePlotItem

依赖:
  3D 部分需要 PyOpenGL: uv pip install PyOpenGL
"""

import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("Unit 6: 图像显示与3D图形")
pg.setConfigOptions(imageAxisOrder='row-major')

# ---------------------------------------------------------------------------
# 1. 快速显示图像: pg.image()
# ---------------------------------------------------------------------------
img_data = np.random.normal(size=(200, 200))
img_data += np.sin(np.linspace(0, 10, 200)).reshape(-1, 1)
pg.image(img_data, title="1. pg.image() 快速显示")


# ---------------------------------------------------------------------------
# 2. 在 PlotItem 中使用 ImageItem (带坐标轴)
# ---------------------------------------------------------------------------
win = pg.GraphicsLayoutWidget(title="Unit 6: 图像与3D", show=True)
win.resize(1400, 900)

p_img = win.addPlot(title="2. ImageItem 在 PlotItem 中", row=0, col=0)

# 创建数据
x = np.linspace(-5, 5, 200)
y = np.linspace(-3, 3, 150)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-np.sqrt(X**2 + Y**2) / 3)

img = pg.ImageItem(image=Z)
img.setRect(pg.QtCore.QRectF(x[0], y[0], x[-1] - x[0], y[-1] - y[0]))
p_img.addItem(img)

p_img.setLabel('left', 'Y')
p_img.setLabel('bottom', 'X')

# 添加色阶条
p_img.addColorBar(img, colorMap='viridis')


# ---------------------------------------------------------------------------
# 3. ImageView: 交互式图像查看器
#    - 内置直方图/色阶调整
#    - 支持缩放和 ROI 选择
#    - 支持时间序列图像 (3D 数据)
# ---------------------------------------------------------------------------
win2 = pg.GraphicsLayoutWidget(title="3. ImageView 交互式查看器", show=True)
win2.resize(800, 600)

from pyqtgraph import ImageView

# 创建 3D 数据 (帧, 行, 列)
frames = np.zeros((20, 128, 128))
for i in range(20):
    # 每个帧是一个移动的高斯斑点
    x0 = 64 + 30 * np.cos(i * np.pi / 10)
    y0 = 64 + 30 * np.sin(i * np.pi / 10)
    X, Y = np.meshgrid(np.arange(128), np.arange(128))
    frames[i] = np.exp(-((X - x0)**2 + (Y - y0)**2) / 200)

iv = ImageView()
iv.setImage(frames)
iv.setWindowTitle("ImageView: 使用下方滑块切换帧")


# ---------------------------------------------------------------------------
# 4. colormap: 颜色映射
#    - pyqtgraph 内置多种 colormap: 'viridis', 'inferno', 'plasma',
#      'cividis', 'CET-L4', 'CET-R3', 'CET-L8' 等
# ---------------------------------------------------------------------------
p_cm = win.addPlot(title="4. 不同 colormap 对比", row=0, col=1)
data = np.linspace(0, 1, 256).reshape(1, -1)
img_cm = pg.ImageItem(image=data)
img_cm.setRect(pg.QtCore.QRectF(0, 0, 1, 1))
p_cm.addItem(img_cm)

cm_bar = p_cm.addColorBar(img_cm, colorMap='CET-R3')


# ---------------------------------------------------------------------------
# 5. HistogramLUTItem: 手动色阶控制
# ---------------------------------------------------------------------------
p_hist = win.addPlot(title="5. 带 HistogramLUT 的图像", row=1, col=0)

img2_data = np.random.gamma(2, 2, size=(200, 200))
img2 = pg.ImageItem(image=img2_data)
p_hist.addItem(img2)

# 直方图色阶控件 (嵌入在窗口右侧)
hist = pg.HistogramLUTItem()
hist.setImageItem(img2)
# 添加到布局
p_hist.vb.addItem(hist, ignoreBounds=True)


# ---------------------------------------------------------------------------
# 6. PColorMeshItem: 伪彩色网格
#    - 用于非均匀网格数据
# ---------------------------------------------------------------------------
p_mesh = win.addPlot(title="6. PColorMeshItem 伪彩色网格", row=1, col=1)

x = np.linspace(-5, 5, 50)
y = np.linspace(-3, 3, 30)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)

mesh = pg.PColorMeshItem(x, y, Z, colorMap='plasma')
p_mesh.addItem(mesh)

p_mesh.addColorBar(mesh, colorMap='plasma')


# ---------------------------------------------------------------------------
# 7. 3D 图形: GLViewWidget
#    警告: 如果 PyOpenGL 未安装，以下代码会跳过
# ---------------------------------------------------------------------------
HAS_OPENGL = False
try:
    import OpenGL
    HAS_OPENGL = True
except ImportError:
    pass

if HAS_OPENGL:
    import pyqtgraph.opengl as gl

    # GLViewWidget 是独立 QWidget，直接 show() 即可
    gl_widget = gl.GLViewWidget()
    gl_widget.setWindowTitle("7. 3D 图形 (GLViewWidget)")
    gl_widget.resize(800, 600)
    gl_widget.opts['distance'] = 20

    # 地面网格
    grid = gl.GLGridItem()
    gl_widget.addItem(grid)

    # 3D 坐标轴
    axis = gl.GLAxisItem()
    gl_widget.addItem(axis)

    # 3D 空间曲线
    t = np.linspace(0, 4 * np.pi, 500)
    x3d = np.sin(t)
    y3d = np.cos(t)
    z3d = t / (2 * np.pi)

    line3d = gl.GLLinePlotItem(
        pos=np.column_stack([x3d, y3d, z3d]),
        color=pg.mkColor('c'),
        width=2
    )
    gl_widget.addItem(line3d)

    # 3D 散点
    scatter3d = gl.GLScatterPlotItem(
        pos=np.column_stack([x3d[::10], y3d[::10], z3d[::10]]),
        color=pg.mkColor('y'),
        size=5
    )
    gl_widget.addItem(scatter3d)

    # 3D 曲面
    sx = np.linspace(-5, 5, 50)
    sy = np.linspace(-5, 5, 50)
    SX, SY = np.meshgrid(sx, sy)
    SZ = np.sin(np.sqrt(SX**2 + SY**2))

    surface = gl.GLSurfacePlotItem(
        x=sx, y=sy, z=SZ,
        color=pg.mkColor(0, 150, 200, 100),
        shader='shaded'
    )
    gl_widget.addItem(surface)

    gl_widget.show()
else:
    p_no3d = win.addPlot(title="7. 3D 图形 (未安装 PyOpenGL)", row=2, col=0,
                          colspan=2)
    text_no3d = pg.TextItem(
        text="未安装 PyOpenGL。要启用 3D 功能，请运行:\n"
             "  uv pip install PyOpenGL",
        color='y', anchor=(0.5, 0.5))
    text_no3d.setPos(0.5, 0.5)
    p_no3d.addItem(text_no3d)
    p_no3d.setXRange(0, 1)
    p_no3d.setYRange(0, 1)

pg.exec()
