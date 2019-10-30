#import Python standard libraries + PyQt5
import sys, os, json, threading, webbrowser
from PyQt5 import QtCore, QtWidgets, QtGui
from interpreters.befunge import befunge_debug

mode = "befunge"

#import helper files
import gui, net
from constants import *
from stylesheets import QMainWindowStyle, QMenuStyle

#main window class
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.open_config()
        self.cache = {}
        self.data = ""
        self.current_file = ""
        self.b_step = None
        self.net = net.NetworkHandler(HOST, PORT)
        self.init_GUI()

    def init_GUI(self):
        self.menu = self.menuBar()
        self.m_file = self.menu.addMenu("&File")
        self.m_edit= self.menu.addMenu("&Edit")
        self.m_server = self.menu.addMenu("&Server")
        self.m_run = self.menu.addMenu("&Run")
        self.m_options = self.menu.addMenu("&Options")
        self.m_help = self.menu.addMenu("&Help")

        self.setStyleSheet(QMainWindowStyle)

        self.menu.setStyleSheet(QMenuStyle)
        
        self.me_save = QtWidgets.QAction("Save", self)
        self.me_save.triggered.connect(self.save_file)
        self.me_save.setShortcut("Ctrl+s")
        self.m_file.addAction(self.me_save)

        self.me_run_locally = QtWidgets.QAction("Run locally...", self)
        self.me_run_locally.triggered.connect(self.run_locally)
        self.me_run_locally.setShortcut("f5")
        self.m_run.addAction(self.me_run_locally)

        self.me_run_remote = QtWidgets.QAction("Run on remote server", self)
        self.me_run_remote.triggered.connect(self.run_remote)
        self.me_run_remote.setShortcut("f6")
        self.m_run.addAction(self.me_run_remote)

        self.me_stop = QtWidgets.QAction("Stop running on server", self)
        self.me_stop.triggered.connect(self.stop_running)
        self.me_stop.setShortcut("f1")
        self.m_run.addAction(self.me_stop)
        
        self.me_debug = QtWidgets.QAction("Debug", self)
        self.me_debug.triggered.connect(self.debug_program)
        self.me_debug.setShortcut("f4")
        self.m_run.addAction(self.me_debug)

        self.me_options = QtWidgets.QAction("Options", self)
        self.me_options.triggered.connect(self.options)
        self.m_options.addAction(self.me_options)
        
        self.me_GitHub = QtWidgets.QAction("GitHub", self)
        self.me_GitHub.triggered.connect(self.GitHub)
        self.m_help.addAction(self.me_GitHub)

        self.main = QtWidgets.QWidget()
        self.layout = QtWidgets.QHBoxLayout(self.main)

        self.splitter = QtWidgets.QSplitter()
        
        dct = self.get_file_structure()

        self.file_list = gui.FileMenu(self, dct["."])
        self.file_list.item_changed.connect(self.send_file_request)
        self.file_list.item_renamed.connect(self.rename_file)
        self.splitter.addWidget(self.file_list)
        
        self.splitter.splitterMoved[int, int].connect(self.splitter_moved)
        self.splitter.setSizes(self.config["splitter0"])

        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/bin/',"Image files (*.jpg *.gif)")

        self.init_GUI_modes()
        
        self.layout.addWidget(self.splitter)
        self.main.setLayout(self.layout)
        self.setCentralWidget(self.main)
        self.show()

    def init_GUI_modes(self):
        #init the bits of the GUI that differ depending on the mode
        if mode == "python":
            self.main_text = gui.HighlightedTextBox(self)
            self.main_text.setPlainText(self.data)
            self.main_text.textChanged.connect(self.update_file_contents)
            self.splitter.addWidget(self.main_text)

##            self.m_language = self.menu.addMenu("&Python")
##            self.me_tocome = QtWidgets.QAction("To Come!", self)
##            self.m_language.addAction(self.me_tocome)
            
        elif mode == "befunge":
            self.main_text = gui.BefungeTextBox(self)
            self.main_text.setPlainText(self.data)
            self.main_text.textChanged.connect(self.update_file_contents)
            self.splitter.addWidget(self.main_text)

    def show_debug_gui(self):
        self.b_step = QtWidgets.QPushButton("Step", self)
        self.b_step.clicked.connect(self.debug_step)
        self.b_exit = QtWidgets.QPushButton("Exit", self)
        self.b_exit.clicked.connect(self.stop_debugging)
        self.layout.addWidget(self.b_step)
        self.layout.addWidget(self.b_exit)
        self.main_text.setReadOnly(True)

    def stop_debugging(self):
        self.layout.removeWidget(self.b_step)
        self.layout.removeWidget(self.b_exit)
        self.b_exit.deleteLater()
        self.b_step.deleteLater()
        self.b_step = None
        self.b_exit = None
        self.debugger.cleanUp()
        self.debugger = None
        self.main_text.setReadOnly(False)

    def debug_step(self):
        self.debugger.debug_step()
            
    def debug_program(self):
        if mode == "python":
            print("Python debugging not yet supported")
        elif mode == "befunge":
            self.debugger = befunge_debug.Debugger(self.main_text)
            self.show_debug_gui()
    
    def run_remote(self):
        self.net.send_data({"request": "run", "value": self.strip_star(self.current_file)})

    def stop_running(self):
        self.net.send_data({"request": "stop"})
        to_print = self.net.recv_data()["print"]
        text_dialog = gui.TextDialog(to_print)

    def run_locally(self):
        run_dialog = gui.LocalRunDialog(self.net, self.strip_star(self.current_file))
        run_dialog.run()

    def strip_star(self, file):
        if file.endswith("*"):
            return file[:-2]
        return file
    
    def rename_file(self, item):
        self.net.send_data({"request": "rename_file", "from": self.strip_star(self.current_file), "to": item})
        self.cache[item] = self.cache[self.current_file]
        self.cache[self.current_file] = None
        self.current_file = item

    def update_file_contents(self):
        self.data = self.main_text.toPlainText()
        self.cache[self.strip_star(self.current_file)] = self.data
        if not self.main_text.inserted_by_user:
            return
        current_index = self.file_list.tree_view.currentIndex()
        r, c = current_index.row(), current_index.column()
        self.file_list.set_modified(self.current_file, True)
        self.file_list.tree_view.setCurrentIndex(self.file_list.m_proxy.index(r, c))
        
    def save_file(self):
        self.net.send_data({"request": "write_file", "file": self.strip_star(self.current_file), "value": self.data})
        current_index = self.file_list.tree_view.currentIndex()
        r, c = current_index.row(), current_index.column()
        self.file_list.set_modified(self.current_file + " *", False)
        self.file_list.tree_view.setCurrentIndex(self.file_list.m_proxy.index(r, c))

    def send_file_request(self, file):
        self.current_file = file
        if self.cache.get(file, False): #if it's in the cache...
            self.data = self.cache[file]
            self.update_text()
            return
        
        self.net.send_data({"request": "get_file", "value": self.strip_star(file)})
        result = self.net.recv_data()
        if result["status"] == 0:
            self.data = result["result"]
            self.update_text()
        else:
            print("[ WAR ]: File request returned non-zero response: " + result["status"])

    def update_text(self):
        self.main_text.setPlainText(str(self.data))

    def get_file_structure(self):
        self.net.send_data({"request": "list"})
        result = self.net.recv_data()["result"]
        dct = {}
        for item in result:
            p = dct
            for x in item.split(os.sep):
                p = p.setdefault(x, {})
        return dct

    def splitter_moved(self, pos, index):
        self.config["splitter0"] = self.splitter.sizes()
        self.save_config()

    def open_config(self):
        with open(config, "r") as f:
            self.config = json.loads(f.read())

    def save_config(self):
        with open(config, "w") as f:
            f.write(json.dumps(self.config))

    def GitHub(self):
        webbrowser.open("https://github.com/Jachdich/lime-ide")

    def options(self):
        self.sss = gui.SettingsDialog()

if __name__ == "__main__":
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    print(QtWidgets.QStyleFactory.keys())
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    print(app.exec_())
    win.net.close()
