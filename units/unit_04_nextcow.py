import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("nextRow demo")

# pg.GraphicsLayoutWidget 默认可以理解为“按行从左到右排列”。
win = pg.GraphicsLayoutWidget(title="nextRow() / nextCol() Demo", show=True)
win.resize(800, 500)

x = np.linspace(0, 10, 200)

# ===== 第一行：三个图并排 =====
p = win.addPlot(title="1-1")
p.plot(x, np.sin(x), pen='c')

p = win.addPlot(title="1-2")
p.plot(x, np.cos(x), pen='m')

p = win.addPlot(title="1-3")
p.plot(x, np.sin(x * 2), pen='y')


# ===== 第二行：2-1 跨两列，2-2 占一列 =====
win.nextRow()

p = win.addPlot(title="2-1", colspan=2)
p.plot(x, np.sin(x) * np.exp(-x / 5), pen='g')

p = win.addPlot(title="2-2")
p.plot(x, np.random.normal(size=200), pen='r')


# ===== 第三行：四个图 =====
win.nextRow()

for i in range(4):
    p = win.addPlot(title=f"Loop-{i + 1}")
    p.plot(np.random.normal(size=50) + i * 2)

pg.exec()