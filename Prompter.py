import time
import random
import threading
from typing import Optional

import cv2

from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from Serialization import Serializer


class EyePrompt(QWidget):
    def __init__(self, config, serializer: Serializer):
        super(EyePrompt, self).__init__()

        self.prompt_size = config["prompt_size"]
        self.corner_prompt_idx = 4 if config["corner_prompts"] else 0
        self.export_metadata = config["metadata"]
        self.serializer = serializer

        self.start_time = None
        self.prompt_loc_lock = threading.Lock()
        self.prompt_loc = None

        self.black_brush = QtGui.QBrush()
        self.black_brush.setColor(QtGui.QColor("black"))
        self.black_brush.setStyle(Qt.SolidPattern)

        self.prompt_brush = QtGui.QBrush()
        self.prompt_brush.setColor(QtGui.QColor(*config["prompt_color"]))
        self.prompt_brush.setStyle(Qt.SolidPattern)

    def start_prompts(self):
        raise NotImplementedError("EyePrompt.start_prompts is an abstract method")

    def shutdown(self):
        raise NotImplementedError("EyePrompt.shutdown is an abstract method")

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)

        size = (painter.device().width(), painter.device().height())
        rect = QtCore.QRect(0, 0, *size)
        painter.fillRect(rect, self.black_brush)

        painter.setBrush(self.redBrush)
        with self.prompt_loc_lock:
            if self.prompt_loc is not None:
                painter.drawEllipse(
                    int(self.prompt_loc[0] * size[0]),
                    int(self.prompt_loc[1] * size[1]),
                    self.prompt_size,
                    self.prompt_size
                )

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        if k == Qt.Key_Escape:
            self.endPrompts()
            self.close()


class MousePrompt(EyePrompt):
    def __init__(self, config):
        super(MousePrompt, self).__init__(config)
        self.setCursor(Qt.ArrowCursor)

        self.trigger_space = 10
        self.cap = cv2.VideoCapture(0)

    def start_prompts(self):
        self.start_time = time.time()
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
            return super().mousePressEvent(a0)

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
                self.update()
        else:
            return super().mousePressEvent(a0)


class TimerPrompt(EyePrompt):
    def __init__(self, config):
        super(TimerPrompt, self).__init__(config)
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
        pass


def create_prompter(config) -> Optional[EyePrompt]:
    if config["trigger"] == "Mouse":
        return MousePrompt(config)

    if config["trigger"] == "Timer":
        return TimerPrompt(config)

    return None
