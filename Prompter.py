import time
import random
import threading
from typing import Optional

import cv2

from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from Serialization import Serializer

from util import *


class EyePrompt(QGraphicsView):
    def __init__(self, config, serializer: Serializer):
        super(EyePrompt, self).__init__()

        self._m_scene = QGraphicsScene()
        self.setScene(self._m_scene)

        self.prompt_size = config["prompt_size"]
        self.corner_prompt_idx = 4 if config["corner_prompts"] else 0
        self.export_metadata = config["metadata"]
        self.serializer = serializer

        self._prompt_loc_lock = threading.Lock()
        self._prompt_loc = None

        black_brush = QtGui.QBrush()
        black_brush.setColor(QtGui.QColor("black"))
        black_brush.setStyle(Qt.SolidPattern)
        self.setBackgroundBrush(black_brush)

        self.prompt_brush = QtGui.QBrush()
        self.prompt_brush.setColor(QtGui.QColor(*config["prompt_color"]))
        self.prompt_brush.setStyle(Qt.SolidPattern)

    def start_prompts(self):
        raise NotImplementedError("EyePrompt.start_prompts is an abstract method")

    def shutdown(self):
        raise NotImplementedError("EyePrompt.shutdown is an abstract method")

    @property
    def prompt_loc(self):
        with self.prompt_loc_lock:
            loc = self._prompt_loc
        return loc

    @prompt_loc.setter
    def prompt_loc(self, n_loc):
        with self._prompt_loc_lock:
            self._prompt_loc = n_loc
        x_loc = int(n_loc[0] * self._m_scene.width())
        y_loc = int(n_loc[1] * self._m_scene.height())
        self._m_scene.clear()
        self._m_scene.addEllipse(x_loc, y_loc, self.prompt_size, self.prompt_size)
        self.update()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        if k == Qt.Key_Escape:
            self.shutdown()
            self.close()


class MousePrompt(EyePrompt):
    def __init__(self, config, serializer):
        super(MousePrompt, self).__init__(config, serializer)
        self.setCursor(Qt.BlankCursor)

        self.trigger_space = 10
        self.cap = cv2.VideoCapture(0)

    def start_prompts(self):
        if self.corner_prompt_idx != 0:
            self.prompt_loc = (0, 0)
        else:
            self.prompt_loc = (
                random.uniform(0, 1),
                random.uniform(0, 1)
            )

    def shutdown(self):
        self.cap.release()
        # TODO: more shutdown stuff, idk what

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.prompt_loc is None:
            return

        m_geo = self.geometry()
        x_loc = int(self.prompt_loc[0] * m_geo.width())
        y_loc = int(self.prompt_loc[1] * m_geo.height())

        if (
                a0.button() == Qt.LeftButton and
                x_loc - self.trigger_space < a0.x() < x_loc + self.trigger_space and
                y_loc - self.trigger_space < a0.y() < y_loc + self.trigger_space
        ):
            # TODO: Capture image
            if self.corner_prompt_idx != 0:
                if self.corner_prompt_idx == 3:
                    self.prompt_loc = (0, 1)
                elif self.corner_prompt_idx == 2:
                    self.prompt_loc = (1, 1)
                else:
                    self.prompt_loc = (1, 0)
                self.corner_prompt_idx -= 1
            else:
                self.prompt_loc = (
                    random.uniform(0, 1),
                    random.uniform(0, 1)
                )


class TimerPrompt(EyePrompt):
    def __init__(self, config, serializer):
        super(TimerPrompt, self).__init__(config, serializer)
        self.setCursor(Qt.BlankCursor)

        self.prompt_loc_th = None
        self.capture_th = None

    def start_prompts(self):
        self.prompt_loc_th = threading.Thread(target=self.run_prompt_loc)
        self.capture_th = threading.Thread(target=self.run_capture)

    def run_prompt_loc(self):
        pass

    def run_capture(self):
        pass

    def shutdown(self):
        if self.prompt_loc_th.is_alive():
            self.prompt_loc_th.join()
        if self.capture_th.is_alive():
            self.capture_th.join()


def create_prompter(config, serializer) -> Optional[EyePrompt]:
    if config["trigger"] == "Mouse":
        return MousePrompt(config, serializer)

    if config["trigger"] == "Timer":
        return TimerPrompt(config, serializer)

    return None
