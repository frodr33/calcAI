#!/usr/bin/env python
#####################################################################
## CS 4701: Fall 2018 Project                                      ##
## Notebook Calculator GUI                                         ##
##                                                                 ##
##                                                                 ##
## Description: The GUI allows the user to write their equation    ##
##              and save it as a JPEG to be passed in to our       ##
##              CNN and solved. Alternatively, users have the      ##
##              option so simply click the evaluate button to      ##
##              directly input the image into the CNN and then     ##
##              display the output in the terminal                 ##
## References:  We use the PyQt5 library, as well as the following ##
##              PyQt5 projects and guides for reference:           ##
##              https://github.com/mfitzp/15-minute-apps           ##
##              http://zetcode.com/gui/pyqt5/                      ##
##                                                                 ##
##                                                                 ##
#####################################################################

from PyQt5.QtCore import QDir, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, qRgb
from PyQt5.QtWidgets import (QAction, QApplication, QColorDialog, QFileDialog,
        QInputDialog, QMainWindow, QMenu, QMessageBox, QWidget, QToolBar)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import CNN

class DrawingArea(QWidget):
    def __init__(self, parent=None):
        super(DrawingArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        # self.setGeometry(100,100,600,400)
        self.myPenWidth = 24
        self.myPenColor = Qt.black
        self.image = QImage()
        self.lastPoint = QPoint()

    def openImage(self, fileName):
        loadedImage = QImage()
        if not loadedImage.load(fileName):
            return False

        newSize = loadedImage.size().expandedTo(self.size())
        self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = False
        self.update()
        return True

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    #def setPenColor(self, newColor):
    #    self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(DrawingArea, self).resizeEvent(event)

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine,
                Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)

        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.addToolBar(self.createToolBar())
        self.saveAsActs = []
        self.drawingArea = DrawingArea()
        self.setCentralWidget(self.drawingArea)
        self.createActions()
        self.createMenus()
        self.setWindowTitle("Notebook Calculator")
        self.resize(1200, 600)
        self.createToolBar()

    def createToolBar(self):
        toolBar = QToolBar()
        button = QPushButton('Evaluation Expression')
        toolBar.addWidget(button)
        button.clicked.connect(self.on_evaluate_clicked)
        toolBar.addWidget(QLabel('Evaluates the expression drawn using our Neural Network backend'))
        return toolBar

    def on_evaluate_clicked(self):
        alert = QMessageBox()
        alert.setText('Evaluating Expression...please name the drawing!')
        # print(alert.exec_())
        visibleImage = self.drawingArea.image
        self.drawingArea.resizeImage(visibleImage, self.drawingArea.size())
        fileName = "CNN_input.JPG"
        visibleImage.save(fileName, "")
        neural_net = CNN.CNN()
        neural_net.predict(fileName)
        # neural_net.test()


    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def open(self):
        if self.maybeSave():
            fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                    QDir.currentPath())
            if fileName:
                self.drawingArea.openImage(fileName)

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

    def penColor(self):
        newColor = QColorDialog.getColor(self.drawingArea.penColor())
        if newColor.isValid():
            self.drawingArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QInputDialog.getInt(self, "Scribble",
                "Select pen width:", self.drawingArea.penWidth(), 1, 50, 1)
        if ok:
            self.drawingArea.setPenWidth(newWidth)

    def about(self):
        QMessageBox.about(self, "About Notebook Calculator",
                "<p>This application was made for a CS 4701 final project.</p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QAction("&Print...", self,
                triggered=self.drawingArea.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.penColorAct = QAction("&Pen Color...", self,
                triggered=self.penColor)

        self.penWidthAct = QAction("Pen &Width...", self,
                triggered=self.penWidth)

        self.clearScreenAct = QAction("&Clear Screen", self, shortcut="Ctrl+L",
                triggered=self.drawingArea.clearImage)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.saveAsMenu = QMenu("&Save As", self)

        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def maybeSave(self):
        if self.drawingArea.isModified():
            ret = QMessageBox.warning(self, "Scribble",
                        "The image has been modified.\n"
                        "Do you want to save your changes?",
                        QMessageBox.Save | QMessageBox.Discard |
                        QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat):
        initialPath = QDir.currentPath() + '/untitled.' + fileFormat

        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.drawingArea.saveImage(fileName, fileFormat)

        return False


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

