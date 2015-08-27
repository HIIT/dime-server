# simple code by Krystian Samp - krychu (samp[dot]krystian[monkey]gmail.com), November 2006

import sys
from PyQt4 import QtGui, QtCore

from math import *

class MyView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        self.scene = QtGui.QGraphicsScene(self)
        #self.scene.setSceneRect(10.5,5,10,5)

        #self.scene.setStyleSheet("border: 0px")

        self.item = []
        numofcircles = 13
        angleinterval= (2*pi)/numofcircles
        r = 40
        for i in range(numofcircles):        
            x = (2.0/log(float(i+2)))*r*cos(i*angleinterval)
            y = (2.0/log(float(i+2)))*r*sin(i*angleinterval)
            d1= (2.0/log(float(i+2)))*15
            d2= (2.0/log(float(i+2)))*15
            #self.item = QtGui.QGraphicsEllipseItem(50, 0, 15, 15)
            ellipse = QtGui.QGraphicsEllipseItem(x,y,d1,d2)
            ellipse.setBrush(QtGui.QColor("black"))
            self.item.append(ellipse)

        del self.item[0]
        for i in range(len(self.item)):
            self.scene.addItem(self.item[i])

        self.setScene(self.scene)

        # Remember to hold the references to QTimeLine and QGraphicsItemAnimation instances.
        # They are not kept anywhere, even if you invoke QTimeLine.start().
        self.tl = QtCore.QTimeLine(1000)
        self.tl.setFrameRange(0, 100)

        self.a = []
        for i in range(len(self.item)):
            self.a.append(QtGui.QGraphicsItemAnimation())

        for i in range(len(self.item)):
            self.a[i].setItem(self.item[i])
            self.a[i].setTimeLine(self.tl)
            #self.a[i].setPosAt(0, QtCore.QPointF(0, -10))
            self.a[i].setRotationAt(1, 360)

        # Each method determining an animation state (e.g. setPosAt, setRotationAt etc.)
        # takes as a first argument a step which is a value between 0 (the beginning of the
        # animation) and 1 (the end of the animation)
        #self.a.setPosAt(0, QtCore.QPointF(0, -10))
        #self.a.setPosAt(0, QtCore.QPointF(0, 0))

        # self.a.setRotationAt(1, 360)
        # self.a2.setRotationAt(1, 360)
        # self.a3.setRotationAt(1, 360)
        # self.a4.setRotationAt(1, 360)

        self.tl.setLoopCount(0)
        #self.tl.start()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = MyView()
    view.show()
    sys.exit(app.exec_())