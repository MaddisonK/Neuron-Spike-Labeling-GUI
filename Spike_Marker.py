import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

# Generate layout
app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.setWindowTitle('Spike Tracker')
label = pg.LabelItem(justify='right')
win.addItem(label)
p1 = win.addPlot(1, 0)
p2 = win.addPlot(2, 0)
p1.setAutoVisible(y=True)

region = pg.LinearRegionItem()
region.setZValue(10)

p2.addItem(region, ignoreBounds=True)

w = QtGui.QWidget()
btn = QtGui.QPushButton('Undo Marker')
btn2 = QtGui.QPushButton('Primary Marker')
labl = QtGui.QLabel("Main List")
listw = QtGui.QListWidget()
labl2 = QtGui.QLabel("Dubious List")
listd = QtGui.QListWidget()

layout = QtGui.QGridLayout()
w.setLayout(layout)
layout.addWidget(btn, 0, 0)
layout.addWidget(btn2, 1, 0)
layout.addWidget(labl, 2, 0)
layout.addWidget(listw, 3, 0)
layout.addWidget(labl2, 4, 0)
layout.addWidget(listd, 5, 0)
w.show()

# return data
global main_list
main_list = []
global dub_list
dub_list = []

# data loader
def load_data_npz(data_file):
    with np.load(data_file, allow_pickle=True) as ld:
        for item in ld:
            data = ld[item]
    return data

# Plot and Load data
data1 = load_data_npz("trace.npz")[0]

p1.plot(data1, pen="w")
p2.plot(data1, pen="w")

# Region Magnifier
def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()
    p1.setXRange(minX, maxX, padding=0)

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

p1.sigRangeChanged.connect(updateRegion)

region.setRegion([1000, 2000])

# Events
global toggle_type
toggle_type = 1
global toggle_remove
toggle_remove = 0
global a
a = None

vLine = pg.InfiniteLine(angle=90, movable=False)
hLine = pg.InfiniteLine(angle=0, movable=False)
p1.addItem(vLine, ignoreBounds=True)
p1.addItem(hLine, ignoreBounds=True)
vb = p1.vb

def mouseMoved(evt):
    pos = evt[0]
    if p1.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        if index > 0 and index < len(data1):
            label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='font-size: 12pt'>y=%0.1f</span>" % (mousePoint.x(), data1[index]))
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())
        global x_last
        x_last = mousePoint.x()
        global y_last
        y_last = mousePoint.y()

def onClick(evt):
    global a
    global toggle_remove
    if toggle_remove == 0:
        if toggle_type == 1:
            a = pg.ArrowItem(angle=270, pen='g', brush=10.0)
            a.setPos(x_last, y_last)
            p1.addItem(a)
            a_main.append(a) #for undoing
            a_main_x.append(int(x_last))
            a_main_y.append(int(y_last))
            main_list.append(x_last) #for data
            listw.addItem(str(x_last)[:7]) #for appearance
            listw.setCurrentRow(listw.currentRow() + 1)
        elif toggle_type == 0:
            a = pg.ArrowItem(angle=270, headLen=10, tipAngle=80, tailLen=-2, baseAngle=20, pen='m', brush=10.0)
            a.setPos(x_last, y_last)
            p1.addItem(a)
            a_dub.append(a) #for undoing
            a_dub_x.append(int(x_last))
            a_dub_y.append(int(y_last))
            dub_list.append(x_last) #for data
            listd.addItem(str(x_last)[:7]) #for appearance
            listd.setCurrentRow(listd.currentRow() + 1)
    elif toggle_remove == 1:
        for i in range(len(a_main_x)):
            if (5 + a_main_x[i]) > x_last > (a_main_x[i]-5):
                if (10 + a_main_y[i]) > y_last >= (a_main_y[i]):
                    p1.removeItem(a_main[i])
                    a_main.pop(i)
                    listw.takeItem(i)
                    main_list.pop(i)
                    a_main_x.pop(i)
                    a_main_y.pop(i)
                    toggle_remove = 0
                    btn.setText("Undo Marker")
                    return None
        for i in range(len(a_dub_x)):
            if (5 + a_dub_x[i]) > x_last > (a_dub_x[i]-5):
                if (10 + a_dub_y[i]) > y_last >= (a_dub_y[i]):
                    p1.removeItem(a_dub[i])
                    a_dub.pop(i)
                    listd.takeItem(i)
                    dub_list.pop(i)
                    a_dub_x.pop(i)
                    a_dub_y.pop(i)
                    toggle_remove = 0
                    btn.setText("Undo Marker")
                    return None
        print("Please try again. Tip: Select the marker more closely")
        btn.setText("Undo Marker")
        toggle_remove = 0

def undo_last():
    global a
    p1.removeItem(a)
    if toggle_type == 1:
        listw.takeItem(listw.currentRow())
        main_list.pop()
    elif toggle_type == 0:
        listd.takeItem(listw.currentRow())
        dub_list.pop()
    print("undid")

def remove_marker():
    global toggle_remove
    toggle_remove = 1
    btn.setText("Undo Marker ON")

def marker_toggle():
    global toggle_type
    if toggle_type == 1:
        toggle_type = 0
        btn2.setText("Secondary Marker")
    elif toggle_type == 0:
        toggle_type = 1
        btn2.setText("Primary Marker")


# Arrow Database
a_main = []
a_main_x = []
a_main_y = []
a_dub = []
a_dub_x = []
a_dub_y = []

# Event Triggers
proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
click = pg.SignalProxy(p1.scene().sigMouseClicked, rateLimit=60, slot=onClick)
btn.clicked.connect(remove_marker)
btn2.clicked.connect(marker_toggle)

# Qt event loop
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

print("\n", "Data Acquired", "\n", "-------------", "\n", "Main Indices Found:", main_list, "\n", "Dubious Indices Found:", dub_list)


