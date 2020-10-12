import sys
import time
import threading

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QWidget

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt

from serialization import Serializer


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
        # TODO: proper variable initialization
        cycleNum = 0
        self._prompt_loc = (0, 0)

        self.runningPrompts = True
        while self.runningPrompts:
            if self._startTime - cycleNum * self.cycleTime > 0:
                self.cycleNum += 1
                # TODO: proper randomization of the prompt
                self._prompt_loc = (0, 0)

            # TODO: pass the current webcam capture with the prompt location to the serializer

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("black"))
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        if self.runningPrompts:
            # prompt the user
            pass
        else:
            pass


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowIcon(QIcon("assets/HSL-logo.png"))
        self.setWindowTitle("HSL | Eye Tracking Data Collection")
        self.setGeometry(100, 100, 500, 500)

        self.baseLayout = QGridLayout()
        self.eyePrompt = EyePrompt()
        self.baseLayout.addWidget(self.eyePrompt, 0, 0)
        self.baseLayout.addWidget(QPushButton('start'), 1, 1)
        self.baseLayout.setRowStretch(0, 3)
        self.baseLayout.setColumnStretch(0, 3)

        self.setLayout(self.baseLayout)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        print(k)
        if k == ord(' '):
            print("space!")
        elif k == Qt.Key_Return:
            print("Enter?")
        elif k == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
        else:
            print(k)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
