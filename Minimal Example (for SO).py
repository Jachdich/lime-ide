from PyQt5 import QtWidgets

QWidgetStyle = """
QWidget {
    color: #dddddd;
    background-color: #333333;
}
"""

QMainWindowStyle = """
QMainWindow {
    color: #dddddd;
    background-color: #333333;
}
"""

QTabWidgetStyle = """
QTabWidget {
    background-color: #333333;
    color: #dddddd;
}
QTabBar {
    color: #dddddd;
    background-color: #333333;
}
"""

class Dialog(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout()
        self.main = QtWidgets.QWidget()
        self.main.setLayout(self.layout)
        
        self.setStyleSheet(QMainWindowStyle)
        self.setCentralWidget(self.main)
        self.show()

class AppearanceTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class SettingsDialog(Dialog):
    def __init__(self):
        super().__init__()
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setStyleSheet(QTabWidgetStyle)
        self.layout.addWidget(self.tabs)
        
        self.tab_appearance = AppearanceTab()
        self.tab_appearance.setStyleSheet(QWidgetStyle)
        #self.tab_appearance.setStyleSheet("QWidget, QWidget * {color: #dddddd; background-color: #333333;}") note: Tried this however it didn't work.
        self.tab_appearance_layout = QtWidgets.QGridLayout()
        self.tab_appearance.setLayout(self.tab_appearance_layout)
        self.tabs.addTab(self.tab_appearance, "Appearance")

        self.tab_server = QtWidgets.QWidget()
        self.tab_server.setStyleSheet(QWidgetStyle)
        self.tab_server_layout = QtWidgets.QGridLayout()
        self.tab_server.setLayout(self.tab_server_layout)
        self.tabs.addTab(self.tab_server, "Server")

if __name__ == "__main__":
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    app = QtWidgets.QApplication([])
    d = SettingsDialog()
    print(app.exec_())
