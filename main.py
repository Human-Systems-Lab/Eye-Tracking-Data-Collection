import os
import sys
import platform
import time
import threading
import random
import json

from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt

import cv2

from serialization import Serializer

diskDir = ""


class ResourceLock:
    """
    wrapper on threading.Lock to enable use alongside the with block
    """

    def __init__(self):
        self._lock = threading.Lock()

    def __enter__(self):
        try:
            self._lock.acquire()
        except Exception as e:
            self._lock.release()
            raise e

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()
        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_value}')
            print(f'exc_traceback: {exc_traceback}')

    def locked(self):
        self._lock.locked()

    def acquire(self, *args, **kwargs):
        self._lock.acquire(*args, **kwargs)

    def release(self):
        self._lock.release()


class EyePrompt(QWidget):
    def __init__(self, *args, **kwargs):
        super(EyePrompt, self).__init__(*args, **kwargs)
        self.setCursor(Qt.BlankCursor)

        self._runningPrompts = False
        self._runningPromptsLock = ResourceLock()
        self._serializer = None
        self._serializerLock = ResourceLock()
        self._dataThread = None
        self._dataThreadLock = ResourceLock()
        self._cycleLength = 1
        self._cycleLengthLock = ResourceLock()

        self._startTime = None
        self._prompt_loc = None

        self.blackBrush = QtGui.QBrush()
        self.blackBrush.setColor(QtGui.QColor("black"))
        self.blackBrush.setStyle(Qt.SolidPattern)

        self.redBrush = QtGui.QBrush()
        self.redBrush.setColor(QtGui.QColor("red"))
        self.redBrush.setStyle(Qt.SolidPattern)

    @property
    def runningPrompts(self) -> bool:
        with self._runningPromptsLock:
            return self._runningPrompts

    @runningPrompts.setter
    def runningPrompts(self, val: bool) -> None:
        with self._runningPromptsLock:
            self._runningPrompts = val

    @property
    def serializer(self) -> Serializer:
        with self._serializerLock:
            return self._serializer

    @serializer.setter
    def serializer(self, val: Serializer) -> None:
        with self._serializerLock:
            self._serializer = val

    @property
    def dataThread(self) -> threading.Thread:
        with self._dataThreadLock:
            return self._dataThread

    @dataThread.setter
    def dataThread(self, val: threading.Thread) -> None:
        with self._dataThreadLock:
            self._dataThread = val

    @property
    def cycleLength(self) -> float:
        with self._cycleLengthLock:
            return self._cycleLength

    @cycleLength.setter
    def cycleLength(self, val: float) -> None:
        with self._cycleLengthLock:
            self._cycleLength = val

    def startPrompts(self):
        self._startTime = time.time()

        th = threading.Thread(target=self.collectData)
        th.start()
        self.dataThread = th

    def endPrompts(self):
        self.runningPrompts = False
        self.dataThread.join()

    def collectData(self):
        cycleNum = 1
        self._prompt_loc = (
            random.uniform(0, 1),
            random.uniform(0, 1)
        )
        cap = cv2.VideoCapture(0)

        self.runningPrompts = True
        while self.runningPrompts:
            # assumption is that the time it take to run this loop is much less than self.cycleLength
            if time.time() > self._startTime + cycleNum * self.cycleLength:
                cycleNum += 1
                self._prompt_loc = (
                    random.uniform(0, 1),
                    random.uniform(0, 1)
                )
                self.update()

            ret, frame = cap.read()
            if not ret:
                continue

            if self.serializer is not None:
                self.serializer.handle_data(self._prompt_loc, frame)

        cap.release()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)

        size = (painter.device().width(), painter.device().height())
        rect = QtCore.QRect(0, 0, *size)
        painter.fillRect(rect, self.blackBrush)

        dim = 10
        painter.setBrush(self.redBrush)
        if self.runningPrompts:
            x = int(self._prompt_loc[0] * size[0])
            y = int(self._prompt_loc[1] * size[1])
            painter.drawEllipse(x, y, dim, dim)
        else:
            pass

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        if k == Qt.Key_Escape:
            self.endPrompts()
            self.close()


class DataOutputOptions(QWidget):
    def __init__(self):
        super(DataOutputOptions, self).__init__()

        # Loading configurations and selecting a current configuration
        self.configs = dict()
        self.currentConfig = None
        for e in os.listdir(os.path.join(diskDir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                if self.currentConfig is None:
                    self.currentConfig = e[:-5]
                with open(os.path.join(diskDir, "DataOutputConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.configCombos = None
        self.newConfig = None
        self.nameLabel = None
        self.nameBox = None

        self.buildLayout()
        self.rebuildLayout = False

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if self.rebuildLayout:
            self.buildLayout()
            self.rebuildLayout = False
        super().paintEvent(a0)

    def buildLayout(self):
        layout = QVBoxLayout()

        self.configCombos = QComboBox()
        self.configCombos.setMinimumWidth(100)
        # noinspection PyUnresolvedReferences
        self.configCombos.changeEvent.connect(self.onSelect)
        for k in self.configs.keys():
            self.configCombos.addItem(k)
        self.newConfig = QPushButton("+")
        self.newConfig.setMaximumWidth(20)

        selectionLayout = QHBoxLayout()
        selectionLayout.addWidget(self.configCombos)
        selectionLayout.addWidget(self.newConfig)
        selectionWidget = QWidget()
        selectionWidget.setLayout(selectionLayout)

        self.nameLabel = QLabel("Configuration Name: ")
        self.nameLabel.setMinimumWidth(100)
        self.nameLabel.setMaximumWidth(100)
        self.nameBox = QLineEdit(self.currentConfig)
        # noinspection PyUnresolvedReferences
        self.nameBox.returnPressed.connect(self.onNameChange)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.nameLabel)
        nameLayout.addWidget(self.nameBox)
        nameWidget = QWidget()
        nameWidget.setLayout(nameLayout)

        layout.addWidget(selectionWidget)
        layout.addWidget(nameWidget)
        self.setLayout(layout)

    def onSelect(self, i):
        self.currentConfig = list(self.configs)[i]
        self.rebuildLayout = True
        self.update()

    def onNameChange(self):
        nName = self.nameBox.text()
        self.configs[nName] = self.configs[self.currentConfig]
        del self.configs[self.currentConfig]
        self.currentConfig = nName
        self.configCombos.setItemText(self.configCombos.currentIndex(), nName)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setCursor(Qt.ArrowCursor)
        self.eyePrompt = EyePrompt()

        self.setWindowIcon(QtGui.QIcon("assets/HSL-logo.png"))
        self.setWindowTitle("HSL | Eye Tracking Data Collection")
        self.setGeometry(100, 100, 900, 900)

        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("Save")

        # Building the Data Output widget
        self.dataOutput = QDockWidget("Data Output", self)
        self.dataOutputOptions = DataOutputOptions()
        self.dataOutput.setWidget(self.dataOutputOptions)
        self.dataOutput.setFloating(False)

        self.setCentralWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, self.dataOutput)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        if k == Qt.Key_Return:
            pass
            # self.eyePrompt.showFullScreen()
            # self.eyePrompt.cycleLength = 2
            # self.eyePrompt.startPrompts()


def main():
    global diskDir
    plat = platform.system()
    if plat == "Windows":
        diskDir = os.path.join(os.getenv("APPDATA"), "HSL")
    elif plat == "Linux":
        diskDir = os.path.join(os.path.expanduser("~"), ".HSL")
    else:
        print("Unsupported operating system: %s" % plat)
        print("This software only supports Windows and Linux")
        exit(1)

    if not os.path.isdir(diskDir):
        os.mkdir(diskDir)
    diskDir = os.path.join(diskDir, "EyeTracking-DataCollection")
    if not os.path.isdir(diskDir):
        os.mkdir(diskDir)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
