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
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from Serialization import Serializer

from util import *


class EyePrompt(QWidget):
    def __init__(self, config, serializer: Serializer):
        super(EyePrompt, self).__init__()
        assert serializer is not None

        self.prompt_size = config["prompt_size"]
        self.corner_prompt_idx = 4 if config["corner_prompts"] else 0
        self.export_metadata = config["metadata"]
        self.serializer = serializer

        self._prompt_loc_lock = threading.Lock()
        self._prompt_loc = (0, 0)

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

    @property
    def prompt_loc(self):
        with self.prompt_loc_lock:
            x = (self._prompt_loc[0] + self.prompt_size / 2) / self.width()
            y = (self._prompt_loc[1] + self.prompt_size / 2) / self.height()
        return x, y

    @prompt_loc.setter
    def prompt_loc(self, n_loc):
        x_loc = int(n_loc[0] * self.width()) - self.prompt_size / 2
        y_loc = int(n_loc[1] * self.height()) - self.prompt_size / 2
        with self._prompt_loc_lock:
            self._prompt_loc = (x_loc, y_loc)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)

        rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.fillRect(rect, self.black_brush)

        painter.setBrush(self.prompt_brush)
        painter.drawEllipse(
            *self._prompt_loc,
            self.prompt_size,
            self.prompt_size
        )
        painter.end()

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

        self.capture_th = None

        # thread safe variables
        self._start_time = None
        self._start_time_lock = Lock()
        self._running = False
        self._running_lock = Lock()

        timer_config = config["prompt_config_options"]
        self.prompt_time = timer_config["prompt_time"] / 1e3
        self.capture_delay = timer_config["capture_delay"] / 1e3
        self.sample_num = timer_config["sample_num"]
        sample_time = self.prompt_time - self.capture_delay
        # sample_inc should have sample_num - 1 in the denominator,
        # but that would cause a slightly higher prompt time
        self.sample_inc = sample_time / self.sample_num

    @property
    def start_time(self):
        with self._start_time_lock:
            return self._start_time

    @start_time.setter
    def start_time(self, val):
        with self._start_time_lock:
            self._start_time = val

    @property
    def running(self):
        with self._running_lock:
            return self._running

    @running.setter
    def running(self, val):
        with self._running_lock:
            self._running = val

    @debug_fn(use_thread_id=True, print_args=True, member_fn=True)
    def start_prompts(self):
        self.capture_th = threading.Thread(target=self.run_capture)
        self.start_time = time.time()
        self.running = True
        self.capture_th.start()

    @debug_fn(use_thread_id=True, print_args=True, member_fn=True)
    def run_capture(self):
        idx = 1
        cap = cv2.VideoCapture(0)
        while True:
            if not self.running:
                return

            if self.corner_prompt_idx != 0:
                if self.corner_prompt_idx == 4:
                    self.prompt_loc = (0, 0)
                elif self.corner_prompt_idx == 3:
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

            time.sleep(self.capture_delay)
            for i in range(self.sample_num - 1):
                ret, frame = cap.read()
                if ret:
                    self.serializer.handle_data(self.prompt_loc, frame)
                time.sleep(self.sample_inc)
            ret, frame = cap.read()
            if ret:
                self.serializer.handle_data(self.prompt_loc, frame)

            time.sleep(max(idx * self.prompt_time + self.start_time - time.time(), 0))
            idx += 1

    @debug_fn(use_thread_id=True, print_args=True, member_fn=True)
    def shutdown(self):
        self.running = False
        if self.capture_th.is_alive():
            self.capture_th.join()


class SmoothPrompt(EyePrompt):
    def __init__(self, config, serializer):
        super(SmoothPrompt, self).__init__(config, serializer)

    def start_prompts(self):
        pass

    def shutdown(self):
        pass


def create_prompter(config, serializer) -> Optional[EyePrompt]:
    if config["prompt_config"] == "Mouse":
        return MousePrompt(config, serializer)

    if config["prompt_config"] == "Timer":
        return TimerPrompt(config, serializer)

    if config["prompt_config"] == "Smooth":
        return SmoothPrompt(config, serializer)

    return None
