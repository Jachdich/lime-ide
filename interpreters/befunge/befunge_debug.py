from PyQt5 import QtGui
from interpreters.befunge import befunge_interpreter
from constants import DEBUGGER_PORT, HOST
import socket
###TEMP IMPORTS
import time

class Debugger:
    def __init__(self, textbox, outbox):
        self.inter = befunge_interpreter.Interpreter(textbox.toPlainText())
        self.textbox = textbox
        self.outbox = outbox
        
    def debug_step(self):
        a = time.time()
        ip = self.inter.debug_step()
        print("Step", time.time() - a); a = time.time()
        self.highlight((ip[0], ip[1]))
        self.running = self.inter.running
        print("highlight", time.time() - a); a = time.time()
        s = socket.socket()
        s.connect((HOST, DEBUGGER_PORT))
        self.outbox.setPlainText(s.recv(1024).decode("utf-8"))
        s.close()
        print("file", time.time() - a); a = time.time()
        
    def highlight(self, ip):
        old_format = self.textbox.currentCharFormat()
        text = "\n".join(["".join(x) for x in self.inter.m])
        self.textbox.setPlainText("")
        x = 0
        y = 0
        for char in text:
            if not char == "\n":
                if x == ip[0] and y == ip[1]:
                    fg = QtGui.QColor(180, 180, 180)
                    bg = QtGui.QColor(50, 100, 50)

                    color_format = self.textbox.currentCharFormat()
                    color_format.setBackground(bg)
                    color_format.setForeground(fg)
                    self.textbox.setCurrentCharFormat(color_format)
                    self.textbox.insertPlainText(char)
                else:
                    self.textbox.setCurrentCharFormat(old_format)
                    self.textbox.insertPlainText(char)
                x += 1
            else:
                self.textbox.setCurrentCharFormat(old_format)
                self.textbox.insertPlainText(char)
                y += 1
                x = 0
                
        #restore format
        self.textbox.setCurrentCharFormat(old_format)

    def cleanUp(self):
        self.highlight((-1, -1))
