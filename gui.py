from PyQt5 import QtCore, QtWidgets, QtGui
from constants import *
from stylesheets import QTreeViewStyle, QVScrollbarStyle, QHScrollbarStyle, QTabWidgetStyle
from stylesheets import QPlainTextStyle, QTreeViewHeaderStyle, QMainWindowStyle, QWidgetStyle
import os, syntax, threading, subprocess
from sys import exit

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
        
        self.tree_view.setStyleSheet(QTreeViewStyle + QVScrollbarStyle + QHScrollbarStyle)
        self.tree_view.header().setStyleSheet(QTreeViewHeaderStyle)
        
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
                self.m.appendRow(QtGui.QStandardItem(QtGui.QIcon(icon_file), file))
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
                    item = QtGui.QStandardItem(QtGui.QIcon(icon_file), f)
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
    def __init__(self, parent):
        super().__init__()

        self.last_key_backspace = False
        self.inserted_by_user = True
        self.parent = parent
        
        self.setStyleSheet(QPlainTextStyle)

        self.textChanged.connect(self.signal_text_changed)
        self.syntax = syntax.PythonHighlighter(self.document())
        
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
        #if the text ends with a newlinem, indent by the previous amount
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

    def signal_text_changed(self):
        pass #self.add_indent()

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
        #self.setStyleSheet("QWidget, QWidget * {color: #dddddd; background-color: #333333;}")

class SettingsDialog(Dialog):
    def __init__(self):
        super().__init__()
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setStyleSheet(QTabWidgetStyle)
        self.layout.addWidget(self.tabs)
        
        self.tab_appearance = AppearanceTab()
        self.tab_appearance.setStyleSheet("QWidget, QWidget * {color: #dddddd; background-color: #333333;}")
        self.tab_appearance_layout = QtWidgets.QGridLayout()
        self.tab_appearance.setLayout(self.tab_appearance_layout)
        self.tabs.addTab(self.tab_appearance, "Appearance")

        self.tab_server = QtWidgets.QWidget()
        self.tab_server.setStyleSheet(QWidgetStyle)
        self.tab_server_layout = QtWidgets.QGridLayout()
        self.tab_server.setLayout(self.tab_server_layout)
        self.tabs.addTab(self.tab_server, "Server")

        self.tab_appearance1 = QtWidgets.QWidget()
        self.tab_appearance1.setStyleSheet(QWidgetStyle)
        self.tab_appearance1_layout = QtWidgets.QGridLayout()
        self.tab_appearance1.setLayout(self.tab_appearance1_layout)
        self.tabs.addTab(self.tab_appearance1, "Old")

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
            
