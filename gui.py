from PyQt5       import QtCore, QtWidgets, QtGui
from constants   import *
from stylesheets import managerInstance as styleSheetManager
from strings     import run_file
import os, syntax, threading, subprocess, json, logger
from sys import exit

needs_to_be_updated = []

class FileMenu(QtWidgets.QWidget):
    item_changed = QtCore.pyqtSignal(str)
    item_renamed = QtCore.pyqtSignal(str)
    def __init__(self, parent, files):
        super().__init__()
            
        self.parent = parent
        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.entry_list = files

        self.tree_view = QtWidgets.QTreeView(self.parent)
        self.layout.addWidget(self.tree_view)
        
        self._init_GUI()

    def _init_GUI(self):
        self.m = QtGui.QStandardItemModel(self.tree_view)
        self.m.setHorizontalHeaderLabels(["Files"])
        self.m_proxy = _SortProxyModel(self.m)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setModel(self.m_proxy)
        self.tree_view.clicked.connect(self.emit_current_file)
        self.tree_view.model().m.itemChanged.connect(self.handle_item_changed)
        
        self.update()
        self.setLayout(self.layout)

    def set_modified(self, file, value):
        keys = file.split("/")[1:]
        self.status = False
        self.entry_list = self.update_dict(self.entry_list, keys, value)
        if self.status:
            threading.Thread(target=self.update()).start()

    def update_dict(self, data, keys, value):
        dct = {}
        for a, b in data.items():
            if a != keys[-1]:
                first = a
            else:
                if (not a.endswith("*")) and value:
                    first = a + " *"
                    self.status = True
                else:
                    if value == False:
                        self.status = True
                        first = a[:-2]
                    else:
                        first = a

            if not isinstance(b, dict):
                second = b
            else:
                second = self.update_dict(b, keys, value)

            dct[first] = second
        return dct
    
    def handle_item_changed(self, item):
        self.item_renamed.emit(item.text())

    def update(self):
        self.m.clear()
        self.file_entries = []

        for i, file in enumerate(self.entry_list):
            if self.entry_list[file] == {}:
                ext = file[file.rfind(".") + 1:]
                if ext in icons:
                    icon = icons[ext] 
                else:
                    icon = "_blank.png"
                icon = os.path.join(resource_path, icon)
                self.m.appendRow(QtGui.QStandardItem(QtGui.QIcon(icon), file))
                
            else:
                t = self.get_folder_contents(self.entry_list[file], file)
                self.m.appendRow(t)
                
    def emit_current_file(self, index):
        for sel in self.tree_view.selectedIndexes():
            val = "/" + sel.data()
            while sel.parent().isValid():
                sel = sel.parent()
                val = "/" + sel.data() + val
            self.item_changed.emit(val)

    def get_folder_contents(self, folder, name):
        if folder == {}:
            return QtGui.QStandardItem(QtGui.QIcon(icon_folder), name)
        else:
            t = QtGui.QStandardItem(QtGui.QIcon(icon_folder), name)
            for f in folder:
                if not folder[f] == {}:
                    item = self.get_folder_contents(folder[f], f)
                    item.setData(True, QtCore.Qt.UserRole)
                    t.appendRow(item)
                else:
                    ext = f[f.rfind(".") + 1:]
                    if ext in icons:
                        icon = icons[ext] 
                    else:
                        icon = "_blank.png"
                    icon = os.path.join(resource_path, icon)
                    item = QtGui.QStandardItem(QtGui.QIcon(icon), f)
                    item.setData(False, QtCore.Qt.UserRole)
                    t.appendRow(item)
            return t

    def parse_file_structure(self, file):
        file = ["." + file, ]
        dct = {}
        for item in file:
            p = dct
            for x in item.split('/'):
                p = p.setdefault(x, {})
        return dct

class HighlightedTextBox(QtWidgets.QPlainTextEdit):
    def __init__(self, parent, doSetup=True):
        super().__init__()

        if doSetup:
            self.last_key_backspace = False
            self.inserted_by_user = True
            self.parent = parent
            
            self.syntax = syntax.PythonHighlighter(self.document())
            needs_to_be_updated.append(self)
        
    def add_indent(self):
        if self.last_key_backspace or not self.inserted_by_user:
            #if the last key was a backspace (user is deleting text) we don't want to add the indent
            #and we don't want to insert an indent if the text wasn't typed by the user
            return

        #get cursor pos and text body
        pos = self.textCursor().position()
        text = self.toPlainText()
        #get text above the cursor
        top_text = text[:pos]

        #if the text ends with a colon and a newline, we add one to the indent
        if top_text.endswith(":\n"):
            self.insertPlainText(" " * indent_level * (self.get_indent_level(top_text) + 1))
        #if the text ends with a newline, indent by the previous amount
        elif top_text.endswith("\n"):
            self.insertPlainText(" " * indent_level * self.get_indent_level(top_text))
        else:
            self.inserted_by_user = False

    def get_indent_level(self, text):
        try:
            last_line = text.split("\n")[-2]
        except IndexError:
            return 0
        total = 0
        for i in last_line.split(" "):
            if not i == "":
                break
            total += 1
        return total // indent_level

    def insertPlainText(self, text):
        self.inserted_by_user = False
        super(HighlightedTextBox, self).insertPlainText(text)

    def setPlainText(self, text):
        self.inserted_by_user = False
        super(HighlightedTextBox, self).setPlainText(text)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            self.last_key_backspace = True
        else:
            self.last_key_backspace = False

        self.inserted_by_user = True
        super(HighlightedTextBox, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Return:
            self.add_indent()

    def update(self):
        super().__init__()
        #self.syntax = syntax.PythonHighlighter(self.document())
        self.syntax.redefine_words()
            
class _SortProxyModel(QtCore.QSortFilterProxyModel):
    """Sorting proxy model that always places folders on top."""
    def __init__(self, model):
        super().__init__()
        self.setSourceModel(model)
        self.m = model
        #self.setHorizontalHeaderLabels(["Files,"])

    def lessThan(self, left, right):
        """Perform sorting comparison.

        Since we know the sort order, we can ensure that folders always come first.
        """
        left_is_folder = left.data(QtCore.Qt.UserRole)
        left_data = left.data(QtCore.Qt.DisplayRole)
        right_is_folder = right.data(QtCore.Qt.UserRole)
        right_data = right.data(QtCore.Qt.DisplayRole)
        sort_order = self.sortOrder()

        if left_is_folder and not right_is_folder:
            result = sort_order == QtCore.Qt.AscendingOrder
        elif not left_is_folder and right_is_folder:
            result = sort_order != QtCore.Qt.AscendingOrder
        else:
            result = left_data < right_data
        return result

class Dialog(QtWidgets.QMainWindow):
    def __init__(self, initialX=600, initialY=400):
        super().__init__()
        self.layout = QtWidgets.QGridLayout()
        self.main = QtWidgets.QWidget()
        self.main.setLayout(self.layout)
        self.main.resize(initialX, initialY)
        
        self.setStyleSheet(styleSheetManager.StyleSheet)
        self.setCentralWidget(self.main)
        self.show()

class AppearanceTab(QtWidgets.QWidget):
    def __init__(self, initialX=600, initialY=400):
        super().__init__()
        logger.log(logger.DEBUG, "Starting AppearanceTab GUI construction...")

        self.colours = {"builtin": None}
        
        self.tabs = QtWidgets.QTabWidget(self)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.tabs, 0, 0, 10, 10)
        
        self.tab_syntax = QtWidgets.QWidget()
        self.tab_syntax_layout = QtWidgets.QGridLayout()
        self.tab_syntax.setLayout(self.tab_syntax_layout)
        self.tabs.addTab(self.tab_syntax, "Syntax")

        self.tab_interface = QtWidgets.QWidget()
        self.tab_interface_layout = QtWidgets.QGridLayout()
        self.tab_interface.setLayout(self.tab_interface_layout)
        self.tabs.addTab(self.tab_interface, "Interface")

        self.tab_ssheets = QtWidgets.QWidget()
        self.tab_ssheets_layout = QtWidgets.QGridLayout()
        self.tab_ssheets.setLayout(self.tab_ssheets_layout)
        self.tabs.addTab(self.tab_ssheets, "Stylesheets")

        self.init_tabs()
        self.resize(initialX, initialY)
        logger.log(logger.DEBUG, "AppearanceTab GUI construction complete")

    def init_tabs(self):
        with open("styles.json", "r") as f:
            self.styles = json.loads(f.read())

        #syntax highlighting
        self.l_keyw = QtWidgets.QLabel(self)
        self.t_keyw = HighlightedTextBox(self)
        self.t_keyw.insertPlainText(", ".join(self.styles["words"]["keywords"]))
        self.l_keyw.setText("Keywords")
        self.tab_syntax_layout.addWidget(self.l_keyw, 0, 0)
        self.tab_syntax_layout.addWidget(self.t_keyw, 1, 0)

        self.builtin_selection_layout = QtWidgets.QHBoxLayout()

        self.l_builtin = QtWidgets.QLabel(self)
        self.t_builtin = HighlightedTextBox(self)
        self.t_builtin.insertPlainText(", ".join(self.styles["words"]["builtins"]))
        self.l_builtin.setText("Builtins")
        self.builtin_selection_layout.addWidget(self.l_builtin)
        self.tab_syntax_layout.addWidget(self.t_builtin, 1, 1)

        self.b_builtin_colour = QtWidgets.QPushButton(self)
        self.b_builtin_colour.setMaximumWidth(16)
        self.b_builtin_colour.clicked.connect(lambda: self.change_syntax_colour("builtin", self.b_builtin_colour))
        self.b_builtin_colour.setStyleSheet("background-color: {}; border: 1px solid #000000;".format(self.styles["colours"]["builtin"][0]))
        self.builtin_selection_layout.addWidget(self.b_builtin_colour)

        self.tab_syntax_layout.addLayout(self.builtin_selection_layout, 0, 1)

        #interface style

        self.l_foreground = QtWidgets.QLabel("Foreground", self)
        self.l_background = QtWidgets.QLabel("Background", self)
        self.l_light_background = QtWidgets.QLabel("Light background", self)
        self.l_dark_background = QtWidgets.QLabel("Dark  background", self)

        self.b_bg_colour = QtWidgets.QPushButton(self)
        self.b_bg_colour.setMaximumWidth(16)
        self.b_bg_colour.clicked.connect(lambda: self.change_colour("bg", self.b_bg_colour))
        self.b_bg_colour.setStyleSheet("background-color: {}; border: 1px solid #000000;".format(self.styles["colours"]["bg"]))

        self.b_fg_colour = QtWidgets.QPushButton(self)
        self.b_fg_colour.setMaximumWidth(16)
        self.b_fg_colour.clicked.connect(lambda: self.change_colour("fg", self.b_fg_colour))
        self.b_fg_colour.setStyleSheet("background-color: {}; border: 1px solid #000000;".format(self.styles["colours"]["fg"]))

        self.b_light_bg_colour = QtWidgets.QPushButton(self)
        self.b_light_bg_colour.setMaximumWidth(16)
        self.b_light_bg_colour.clicked.connect(lambda: self.change_colour("light", self.b_light_bg_colour))
        self.b_light_bg_colour.setStyleSheet("background-color: {}; border: 1px solid #000000;".format(self.styles["colours"]["light"]))

        self.b_dark_bg_colour = QtWidgets.QPushButton(self)
        self.b_dark_bg_colour.setMaximumWidth(16)
        self.b_dark_bg_colour.clicked.connect(lambda: self.change_colour("dark", self.b_dark_bg_colour))
        self.b_dark_bg_colour.setStyleSheet("background-color: {}; border: 1px solid #000000;".format(self.styles["colours"]["dark"]))

        self.tab_interface_layout.addWidget(self.l_foreground, 0, 0)
        self.tab_interface_layout.addWidget(self.l_background, 1, 0)
        self.tab_interface_layout.addWidget(self.l_light_background, 2, 0)
        self.tab_interface_layout.addWidget(self.l_dark_background, 3, 0)

        self.tab_interface_layout.addWidget(self.b_fg_colour,       0, 1)
        self.tab_interface_layout.addWidget(self.b_bg_colour,       1, 1)
        self.tab_interface_layout.addWidget(self.b_light_bg_colour, 2, 1)
        self.tab_interface_layout.addWidget(self.b_dark_bg_colour, 3, 1)


        #Stylesheets

        self.c_stylesheet = QtWidgets.QComboBox(self)
        for sheet in styleSheetManager.raw_stylesheets:
            self.c_stylesheet.addItem(sheet)

        self.c_stylesheet.activated[str].connect(self.change_stylesheet)

        self.t_stylesheet = QtWidgets.QPlainTextEdit(self)

        self.tab_ssheets_layout.addWidget(self.c_stylesheet)
        self.tab_ssheets_layout.addWidget(self.t_stylesheet)
        self.change_stylesheet(self.c_stylesheet.itemText(self.c_stylesheet.currentIndex()))

    def change_stylesheet(self, sheet):
        self.t_stylesheet.clear()
        self.t_stylesheet.insertPlainText(styleSheetManager.raw_stylesheets[sheet])

    def change_colour(self, name, button):
        colour = QtWidgets.QColorDialog.getColor()
        hex_colour = hex(colour.rgb())[2:]
        button.setStyleSheet("background-color: #{}; border: 1px solid #000000;".format(hex_colour))
        self.colours[name] = "#" + hex_colour
        logger.log(logger.INFO, name + " colour changed to #" + hex_colour)

    def change_syntax_colour(self, name, button):
        colour = QtWidgets.QColorDialog.getColor()
        hex_colour = hex(colour.rgb())[2:]
        button.setStyleSheet("background-color: #{}; border: 1px solid #000000;".format(hex_colour))
        self.colours[name] = ["#" + hex_colour, "normal"]
        logger.log(logger.INFO, name + " colour changed to #" + hex_colour)
 
    def apply(self):
        logger.log(logger.DEBUG, "Starting apply of settings")
        keywords = self.t_keyw.toPlainText().replace(" ", "")
        if keywords.endswith(","):
            keywords = keywords[:-1]
        builtins = self.t_builtin.toPlainText().replace(" ", "")
        if builtins.endswith(","):
            builtins = builtins[:-1]

        keywords = keywords.split(",")
        builtins = builtins.split(",")
        self.styles["words"]["builtins"] = builtins
        self.styles["words"]["keywords"] = keywords
        for key in self.colours:
            if self.colours[key] == None: continue
            self.styles["colours"][key] = self.colours[key]
            
        with open("styles.json", "w") as f:
            f.write(json.dumps(self.styles, sort_keys=False, indent=4))
        logger.log(logger.DEBUG, "Finished writing stylesheets")
        """
        run_file("syntax.py")
        run_file("gui.py")
        for widget in needs_to_be_updated:
            widget.update()"""

class SettingsDialog(Dialog):
    def __init__(self, initialX=600, initialY=400):
        super().__init__(initialX, initialY)
        logger.log(logger.DEBUG, "Starting SettingsDialog GUI construction...")
        self.tabs = QtWidgets.QTabWidget(self)
        self.layout.addWidget(self.tabs)
        self.tabs.resize(initialX, initialY)
        
        self.tab_appearance = AppearanceTab()
        self.tab_appearance.setStyleSheet("QWidget, QWidget * {color: #dddddd; background-color: #333333;}")
        self.tabs.addTab(self.tab_appearance, "Appearance")

        self.tab_server = QtWidgets.QWidget()
        self.tab_server_layout = QtWidgets.QGridLayout()
        self.tab_server.setLayout(self.tab_server_layout)
        self.tabs.addTab(self.tab_server, "Server")

        self.tab_appearance1 = QtWidgets.QWidget()
        self.tab_appearance1_layout = QtWidgets.QGridLayout()
        self.tab_appearance1.setLayout(self.tab_appearance1_layout)
        self.tabs.addTab(self.tab_appearance1, "Old")

        self.b_apply = QtWidgets.QPushButton(self)
        self.b_apply.setText("Apply")
        self.b_apply.clicked.connect(self.tab_appearance.apply)
        self.layout.addWidget(self.b_apply)
        self.resize(initialX, initialY)
        logger.log(logger.DEBUG, "SettingsDialog GUI construction complete")

class TextDialog(Dialog):
    def __init__(self, text):
        super().__init__()
        
        self.text = HighlightedTextBox(self)
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text, 0, 0)
        self.insertPlainText(text)

    def insertPlainText(self, text):
        self.text.insertPlainText(text)


class LocalRunDialog(TextDialog):
    def __init__(self, net, file):
        super().__init__("")
        self.net = net
        self.current_file = file

    def run(self):
        self.net.send_data({"request": "get_file", "value": self.current_file})
        result = self.net.recv_data()
        text = result["result"]
        with open(".cache.py", "w") as f:
            f.write(text)

        self.t = threading.Thread(target=self.exec_thread)
        self.t.start()

    def exec_thread(self):
        self.process = subprocess.Popen(['python3', '-u', ".cache.py"], stdout=subprocess.PIPE)
        while True:
            output = b""
            if self.process.stdout:
                output += self.process.stdout.readline()# + self.process.stderr.readline()
            if self.process.stderr:
                output += self.process.stderr.readline()
            if output == b'' and self.process.poll() is not None:
                break
            if output:
                self.insertPlainText(output.strip().decode("utf-8") + "\n")
            rc = self.process.poll()

    def kill_process(self):
        self.process.kill()

    def closeEvent(self, event):
        self.kill_process()
        event.accept()
            
class BefungeTextBox(HighlightedTextBox):
    def __init__(self, parent):
        super().__init__(parent, False)

        #self.syntax = syntax.PythonHighlighter(self.document())
        needs_to_be_updated.append(self)
        
    def add_indent(self):
        pass #no auto indent needed for befunge

    def get_indent_level(self, text):
        pass #no auto indent needed for befunge
