from PyQt5 import QtCore, QtWidgets, QtGui
import sys
import threading
import time

stylesheet = """
QWidget {
   background-color: #000000;
}

QLabel {
   background-color: #000000;
   color: #ffffff;
   font-size: 800px;
   qproperty-alignment: AlignCenter;
}
"""

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.text = QtWidgets.QLabel("0")
        self.layout.addWidget(self.text)
        self.showFullScreen()
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            t = threading.Thread(target=self.counting)
            t.start()
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
    def counting(self):
        counting = 0
        while True:
            self.text.setText(str(counting))
            counting += 1
            time.sleep(15)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    print(app.exec_())
