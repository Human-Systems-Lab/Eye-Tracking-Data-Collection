import os
import json
import random

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDockWidget
import webbrowser


from PyQt5.QtCore import Qt


class MenuBar(QMainWindow):
    """
    Menu bar for additional config options
    """

    def __init__(self, disk_dir: str, main_window: QMainWindow):
        super(MenuBar, self).__init__()

        self.disk_dir = disk_dir
        self.main_window = main_window

        menubar = main_window.menuBar()

        # Items In Menu Bar
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')


        #set up items within menus
        loginAct = QAction('&Login', self)
        loginAct.setShortcut('Ctrl+L')
        loginAct.triggered.connect(self.openLoginWindow)
        fileMenu.addAction(loginAct)

        readMeAct = QAction('&View Readme', self)
        readMeAct.triggered.connect(self.openReadMe)
        helpMenu.addAction(readMeAct)



    """
    Action Functions
    """
    def openLoginWindow(self):
        self.main_window.drawLoginPopup(self.main_window)

    def openReadMe(self):
        webbrowser.open('https://github.com/Human-Systems-Lab/Eye-Tracking-Data-Collection/blob/master/README.md')






