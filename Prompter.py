import time
import random
import threading

import cv2

from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from Serialization import Serializer


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
