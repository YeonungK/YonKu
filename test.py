import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication


app = QApplication([])
pw = pg.PlotWidget()
pw.show()

p1 = pw.plotItem
p2 = pg.ViewBox()


p1.scene().addItem(p2)
p1.showAxis('top')
p1.getAxis('top').linkToView(p2)
p2.setYLink(p1)

p3 = pg.ViewBox()
ax3 = pg.AxisItem('top')
p1.layout.addItem(ax3, 0, 1)
p1.scene().addItem(p3)

ax3.linkToView(p3)
p3.setYLink(p1)
ax3.setLabel('axis 3', color='#ff0000')

def update_views():
    p2.setGeometry(p1.vb.sceneBoundingRect())
    p3.setGeometry(p1.vb.sceneBoundingRect())


p1.vb.sigResized.connect(update_views)

# Plot data on primary axis
p1.plot([0, 1, 2, 3], [0, 1, 2, 3], pen="w")

# Plot data on secondary axis (linked to the same X-range)
p2.addItem(pg.PlotCurveItem([-1, 0, 1, 2], [0, 1, 2, 3], pen="b"))
p3.addItem(pg.PlotCurveItem([-2, -1, 0, 1], [0, 1, 2, 3], pen='r'))

# Optionally, you can set different Y-ranges for each ViewBox
p1.setYRange(0, 5)
p2.setYRange(0, 0.5)

app.exec_()