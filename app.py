#TODO
#fix server, make sure to return status after every request
#add multiple modes to server
#debug on server?
#python debug mode, python run mode needs to be fixed
#Add mode setting to settings dialogue
#split gui class
#crash if type when no document open
#FIX THE DAMN BLODDY STYLESHEETS + MAKE IT SIMPLER (i.e. one stylesheet applied to all...?)

#import Python standard libraries + PyQt5
import sys, os, json, threading, webbrowser, traceback
from PyQt5 import QtCore, QtWidgets, QtGui


from interpreters.befunge import befunge_debug
import logger

mode = "python"

#import helper files
import gui, net
from constants import *
from stylesheets import managerInstance as styleSheetManager

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
        logger.log("debug", "Network handler created")
        self.init_GUI()

    def init_GUI(self):
        logger.log(logger.DEBUG, "Loading stylesheets...")
        styleSheetManager.loadSheets()
        logger.log(logger.DEBUG, "Finished loading stylesheets")
        
        self.initMenus()
        logger.log("debug", "Menus initialised")
        
        self.main = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.main)
        self.main.setLayout(self.layout)

        self.file_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.text_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        logger.log(logger.DEBUG, "Getting file structure...")
        dct = self.get_file_structure()
        logger.log(logger.DEBUG, "File structure successfully downloaded")

        self.file_list = gui.FileMenu(self, dct["."])
        self.file_list.item_changed.connect(self.send_file_request)
        self.file_list.item_renamed.connect(self.rename_file)
        self.file_splitter.addWidget(self.file_list)
        
        self.text_splitter.splitterMoved[int, int].connect(self.text_splitter_moved)
        self.text_splitter.setSizes(self.config["text_splitter"])
        self.text_splitter.setSizes([10, 10])
        
        self.file_splitter.splitterMoved[int, int].connect(self.file_splitter_moved)
        self.file_splitter.setSizes(self.config["file_splitter"])

        logger.log("debug", "text_splitter sizes: " + str(self.config["text_splitter"]))
        logger.log("debug", "file_splitter sizes: " + str(self.config["file_splitter"]))

        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/bin/',"Image files (*.jpg *.gif)")

        self.init_GUI_modes()

        self.main_text.setPlainText(self.data)
        self.main_text.textChanged.connect(self.update_file_contents)
        self.text_splitter.addWidget(self.main_text)

        self.output_text = QtWidgets.QPlainTextEdit(self.main)
        self.text_splitter.addWidget(self.output_text)
        self.file_splitter.addWidget(self.text_splitter)
        
        self.layout.addWidget(self.file_splitter)
        self.main.setLayout(self.layout)
        self.setCentralWidget(self.main)
        
        self.applyStyleSheets()
        logger.log("debug", "Created UI successfully")
        self.show()

    def applyStyleSheets(self):
        logger.log("debug", "Applying stylesheets...")
        self.setStyleSheet(styleSheetManager.StyleSheet)

    def initMenus(self):
        self.menu = self.menuBar()
        self.m_file = self.menu.addMenu("&File")
        self.m_edit= self.menu.addMenu("&Edit")
        self.m_server = self.menu.addMenu("&Server")
        self.m_run = self.menu.addMenu("&Run")
        self.m_options = self.menu.addMenu("&Options")
        self.m_help = self.menu.addMenu("&Help")
        
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

    def init_GUI_modes(self):
        #init the bits of the GUI that differ depending on the mode
        if mode == "python":
            self.main_text = gui.HighlightedTextBox(self)
            
        elif mode == "befunge":
            self.main_text = gui.BefungeTextBox(self)

    def show_debug_gui(self):
        logger.log("debug", "Starting debugging...")
        self.b_step = QtWidgets.QPushButton("Step", self)
        self.b_step.clicked.connect(self.debug_step)
        self.b_exit = QtWidgets.QPushButton("Exit", self)
        self.b_exit.clicked.connect(self.stop_debugging)
        self.layout.addWidget(self.b_step)
        self.layout.addWidget(self.b_exit)
        self.main_text.setReadOnly(True)

    def stop_debugging(self):
        logger.log("debug", "Stopping debugging...")
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
        if self.debugger.inter.running == False:
            self.stop_debugging()
            
    def debug_program(self):
        if mode == "python":
            logger.log("error", "Python debugging not yet supported")
        elif mode == "befunge":
            logger.log("Attempting to debug befunge program...")
            self.debugger = befunge_debug.Debugger(self.main_text, self.output_text)
            self.show_debug_gui()
    
    def run_remote(self):
        logger.log("debug", "Attempting to run " + mode + " program on remote server '" + constants.HOST + "'")
        self.net.send_data({"language": mode, "request": "run", "value": self.strip_star(self.current_file)})

    def stop_running(self):
        logger.log("debug", "Attempting to stop running on remote server '" + constants.HOST + "'")
        self.net.send_data({"request": "stop"})
        to_print = self.net.recv_data()["print"] #TODO fix
        text_dialog = gui.TextDialog(to_print)

    def run_locally(self):
        logger.log("debug", "Attempting to run " + mode + " locally...")
        run_dialog = gui.LocalRunDialog(self.net, self.strip_star(self.current_file))
        run_dialog.run()

    def strip_star(self, file):
        if file.endswith("*"):
            return file[:-2]
        return file
    
    def rename_file(self, item):
        logger.log("debug", "Requesting rename of '{}' to '{}'".format(self.strip_star(self.current_file), item))
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
        logger.log("debug", "Saving file '" + self.strip_star(self.current_file) + "'")
        self.net.send_data({"request": "write_file", "file": self.strip_star(self.current_file), "value": self.data})
        current_index = self.file_list.tree_view.currentIndex()
        r, c = current_index.row(), current_index.column()
        self.file_list.set_modified(self.current_file + " *", False)
        self.file_list.tree_view.setCurrentIndex(self.file_list.m_proxy.index(r, c))

    def send_file_request(self, file):
        self.current_file = file
        if self.cache.get(file, False): #if it's in the cache...
            logger.log("debug", "Cache hit on file '" + file + "'")
            self.data = self.cache[file]
            self.update_text()
            return
        
        logger.log("debug", "Cache miss on file '" + file + "'")
        self.net.send_data({"request": "get_file", "value": self.strip_star(file)})
        result = self.net.recv_data()
        if result["status"] == 0:
            self.data = result["result"]
            self.update_text()
        else:
            logger.log("warning", "File request returned non-zero response: " + result["status"] + " on file '" + file + "'")

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

    def text_splitter_moved(self, pos, index):
        self.config["text_splitter"] = self.text_splitter.sizes()
        self.save_config()

    def file_splitter_moved(self, pos, index):
        self.config["file_splitter"] = self.file_splitter.sizes()
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

def handleException(exc_type, exc_value, exc_traceback):
    logger.log(logger.FATAL, "Exception was generated!")
    logger.log(logger.FATAL, exc_type.__name__ + ": " + str(exc_value))
    for x in "".join(traceback.format_tb(exc_traceback)).split("\n"):
        logger.log(logger.FATAL, "    " + x)

if __name__ == "__main__":
    sys.excepthook = handleException
    logger.log(logger.DEBUG, "Setting style to {}".format("Fusion"))
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    status = app.exec_()
    logger.log(logger.INFO, "Process exited with code " + str(status))
    win.net.close()
    logger.log(logger.INFO, "Closed network socket")
    sys.exit(status)
