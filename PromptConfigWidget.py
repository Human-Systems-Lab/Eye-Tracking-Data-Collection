import os
import json
import types
from typing import List
from functools import wraps

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


def no_recursion(default=None):
    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            if hasattr(func, "_executing") and func._executing:
                return default
            func._executing = True
            ret = f(*args, **kwargs)
            func._executing = False
            return ret

        return func
    return decorator


class QMultiSelect(QWidget):
    def __init__(self, labels: List[str], horizontal=False, on_select=None):
        super(QMultiSelect, self).__init__()
        self.options = dict()
        self.on_select = on_select

        @no_recursion()
        def on_button_select(this, *_):
            this.blockSignals(True)
            for k in self.options:
                self.options[k][0].setChecked(False)
                self.options[k][1] = False
            self.options[this.lbl][0].setChecked(True)
            self.options[this.lbl][1] = True

            if self.on_select is not None:
                self.on_select()

            this.blockSignals(False)

        layout = labels_layout = button_layout = None
        if horizontal:
            layout = QHBoxLayout()
        else:
            labels_layout = QVBoxLayout()
            button_layout = QVBoxLayout()

        for i, lbl in enumerate(labels):
            button = QRadioButton()
            button.setFixedHeight(25)
            label = QLabel(lbl)
            label.setFixedHeight(25)
            if horizontal:
                layout.addWidget(label)
                layout.addWidget(button)
                layout.addSpacing(25)
            else:
                labels_layout.addWidget(label, Qt.AlignLeft)
                button_layout.addWidget(button)
            self.options[lbl] = [button, False]
            button.lbl = lbl
            button.on_button_select = types.MethodType(on_button_select, button)
            # noinspection PyUnresolvedReferences
            button.toggled.connect(button.on_button_select)

        self.options[labels[0]][0].on_button_select()

        if horizontal:
            self.setFixedHeight(30)
        else:
            labels_widget = QWidget()
            labels_widget.setLayout(labels_layout)
            labels_widget.setFixedHeight(25 * len(labels))
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            button_widget.setFixedHeight(25 * len(labels))
            button_widget.setMaximumWidth(50)

            layout = QVBoxLayout()
            layout.addWidget(labels_widget)
            layout.addWidget(button_widget)

        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(layout)

    @property
    def selection(self):
        for k in self.options:
            if self.options[k][1]:
                return k
        return None

    @selection.setter
    def selection(self, val):
        if val not in self.options:
            return

        self.options[val][0].on_button_select()


class PromptSelector(QWidget):
    def __init__(self, val, color):
        super(PromptSelector, self).__init__()
        self.setMaximumHeight(100)

        self.max_size = 30
        self.edge_space = 10
        self.scene_size = self.max_size + 2 * self.edge_space

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QBrush(Qt.black, Qt.SolidPattern))
        self.scene.setSceneRect(QtCore.QRectF(2, 2, self.scene_size - 2, self.scene_size - 2))

        self.dot_display = QGraphicsView()
        self.dot_display.setScene(self.scene)
        self.dot_display.setMinimumHeight(self.scene_size)
        self.dot_display.setMinimumWidth(self.scene_size)
        self.dot_display.setMaximumHeight(self.scene_size)
        self.dot_display.setMaximumWidth(self.scene_size)
        self.dot_display.setAlignment(Qt.AlignCenter)

        self.r_slider = QSlider(Qt.Horizontal)
        self.g_slider = QSlider(Qt.Horizontal)
        self.b_slider = QSlider(Qt.Horizontal)
        for slider in [self.r_slider, self.g_slider, self.b_slider]:
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.setSingleStep(1)
        self.r_slider.setValue(color[0])
        self.g_slider.setValue(color[1])
        self.b_slider.setValue(color[2])

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(self.max_size)
        self.size_slider.setSingleStep(1)
        self.size_slider.setValue(val)

        self.prompt_brush = QtGui.QBrush(QtGui.QColor(*color), Qt.SolidPattern)
        self.on_prompt_change()

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("R"))
        color_layout.addWidget(self.r_slider)
        color_layout.addSpacing(25)
        color_layout.addWidget(QLabel("G"))
        color_layout.addWidget(self.g_slider)
        color_layout.addSpacing(25)
        color_layout.addWidget(QLabel("B"))
        color_layout.addWidget(self.b_slider)
        color_widget = QWidget()
        color_widget.setLayout(color_layout)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.size_slider)
        slider_layout.addWidget(color_widget)
        slider_widget = QWidget()
        slider_widget.setLayout(slider_layout)

        layout = QHBoxLayout()
        layout.addWidget(slider_widget)
        layout.addWidget(self.dot_display)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(layout)

        self.set_connections()

    # noinspection PyUnresolvedReferences
    def set_connections(self):
        self.size_slider.valueChanged.connect(self.on_prompt_change)
        self.r_slider.valueChanged.connect(self.on_color_change)
        self.g_slider.valueChanged.connect(self.on_color_change)
        self.b_slider.valueChanged.connect(self.on_color_change)

    def on_prompt_change(self):
        self.scene.clear()
        val = self.value()
        self.scene.addEllipse(
            (self.scene_size - val) / 2,
            (self.scene_size - val) / 2,
            val, val,
            brush=self.prompt_brush
        )

    def on_color_change(self):
        self.prompt_brush = QtGui.QBrush(QtGui.QColor(*self.color()), Qt.SolidPattern)
        self.on_prompt_change()

    def value(self):
        return self.size_slider.value()

    def color(self):
        return (
            self.r_slider.value(),
            self.g_slider.value(),
            self.b_slider.value()
        )


class PromptOptions(QWidget):
    """
    Options:
        prompt_size: int                  Size of the prompt on the screen
        prompt_color: (int, int, int)     Color of the prompt in RGB
        corner_prompts: True | False      Start with a prompt in each corner
        metadata: True | False            Whether to include metadata in the label file
        trigger: mouse | timer            Trigger for changing prompt position
    """

    def __init__(self, data=None):
        super(PromptOptions, self).__init__()

        self.corner_prompts = QCheckBox("Calibration")
        self.metadata = QCheckBox("Save Metadata")
        self.prev_trigger = None
        self.trigger = None
        self.trigger = QMultiSelect(["Mouse", "Timer"], True, self.on_trigger_select)

        self.trigger_options_map = {"Mouse": self.MouseTrigger, "Timer": self.TimerTrigger}

        if data is None:
            self.prompt_selector = PromptSelector(
                10,
                (255, 0, 0)
            )
            self.corner_prompts.setChecked(True)
            self.metadata.setChecked(True)
            self.trigger.selection = "Mouse"
            self.prev_trigger = "Mouse"
            self.trigger_options = self.MouseTrigger()
        else:
            if data["trigger"] == "Mouse":
                self.trigger_options = self.MouseTrigger(data["trigger_options"])
            elif data["trigger"] == "Timer":
                self.trigger_options = self.TimerTrigger(data["trigger_options"])
            else:
                raise ValueError("Invalid trigger type")

            self.prompt_selector = PromptSelector(
                data["prompt_size"],
                data["prompt_color"]
            )
            self.corner_prompts.setChecked(data["corner_prompts"])
            self.metadata.setChecked(data["metadata"])
            self.trigger.selection = data["trigger"]
            self.prev_trigger = data["trigger"]

        layout = QVBoxLayout()
        layout.addWidget(self.prompt_selector)
        layout.addWidget(self.corner_prompts)
        layout.addWidget(self.metadata)
        layout.addWidget(self.trigger)
        layout.addWidget(self.trigger_options)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def get_config(self):
        return {
            "prompt_size": self.prompt_selector.value(),
            "prompt_color": self.prompt_selector.color(),
            "corner_prompts": self.corner_prompts.isChecked(),
            "metadata": self.metadata.isChecked(),
            "trigger": self.trigger.selection,
            "trigger_options": self.trigger_options.get_config()
        }

    def on_trigger_select(self):
        if self.prev_trigger is None or self.trigger is None or self.prev_trigger == self.trigger.selection:
            return

        self.prev_trigger = self.trigger.selection

        self.layout().removeWidget(self.trigger_options)
        self.trigger_options.setHidden(True)
        self.trigger_options.destroy()
        self.trigger_options = self.trigger_options_map[self.prev_trigger]()
        self.layout().addWidget(self.trigger_options)
        self.update()

    class MouseTrigger(QWidget):
        """
        Options:
        """
        def __init__(self, data=None):
            super(PromptOptions.MouseTrigger, self).__init__()

            layout = QVBoxLayout()
            layout.addWidget(QLabel("Mouse Trigger"))
            layout.setAlignment(Qt.AlignTop)
            self.setLayout(layout)

        def get_config(self):
            return {}

    class TimerTrigger(QWidget):
        """
        Options:
            capture_delay: float              Time in seconds to wait before capturing data
            capture_count: int                Number of image/label pairs to capture per
        """
        def __init__(self, data=None):
            super(PromptOptions.TimerTrigger, self).__init__()

            if data is None:
                self.capture_delay = 500
                self.prompt_time = 2500
                self.sample_num = 5
            else:
                self.capture_delay = data["capture_delay"]
                self.prompt_time = data["prompt_time"]
                self.sample_num = data["sample_num"]

            self.capture_delay_slider = QSlider(Qt.Horizontal)
            self.capture_delay_slider.setRange(0, 900)
            self.capture_delay_slider.setValue(self.capture_delay)
            self.capture_delay_label = QLabel("%3d ms" % (self.capture_delay,))
            self.capture_delay_label.setFont(QtGui.QFont("Courier"))

            capture_delay_layout = QHBoxLayout()
            capture_delay_layout.addWidget(self.capture_delay_slider)
            capture_delay_layout.addWidget(self.capture_delay_label)
            capture_delay_widget = QWidget()
            capture_delay_widget.setLayout(capture_delay_layout)

            self.prompt_time_slider = QSlider(Qt.Horizontal)
            self.prompt_time_slider.setRange(1000, 5000)
            self.prompt_time_slider.setValue(self.prompt_time)
            self.prompt_time_label = QLabel("%5.3f s" % (self.prompt_time/1000,))
            self.prompt_time_label.setFont(QtGui.QFont("Courier"))

            prompt_time_layout = QHBoxLayout()
            prompt_time_layout.addWidget(self.prompt_time_slider)
            prompt_time_layout.addWidget(self.prompt_time_label)
            prompt_time_widget = QWidget()
            prompt_time_widget.setLayout(prompt_time_layout)

            self.sample_num_slider = QSlider(Qt.Horizontal)
            self.sample_num_slider.setRange(1, 10)
            self.sample_num_slider.setValue(self.sample_num)
            self.sample_num_label = QLabel(str(self.sample_num))
            self.sample_num_label.setFont(QtGui.QFont("Courier"))

            sample_num_layout = QHBoxLayout()
            sample_num_layout.addWidget(self.sample_num_slider)
            sample_num_layout.addWidget(self.sample_num_label)
            sample_num_widget = QWidget()
            sample_num_widget.setLayout(sample_num_layout)

            layout = QVBoxLayout()
            layout.addWidget(capture_delay_widget)
            layout.addWidget(prompt_time_widget)
            layout.addWidget(sample_num_widget)
            layout.setAlignment(Qt.AlignTop)
            self.setLayout(layout)

            self.set_connections()

        # noinspection PyUnresolvedReferences
        def set_connections(self):
            self.capture_delay_slider.valueChanged.connect(self.on_capture_delay)
            self.prompt_time_slider.valueChanged.connect(self.on_prompt_time)
            self.sample_num_slider.valueChanged.connect(self.on_sample_num)

        def get_config(self):
            return {
                "capture_delay": self.capture_delay,
                "prompt_time": self.prompt_time,
                "sample_num": self.sample_num
            }

        def on_capture_delay(self):
            self.capture_delay = self.capture_delay_slider.value()
            self.capture_delay_label.setText("%3d ms" % (self.capture_delay,))

        def on_prompt_time(self):
            self.prompt_time = self.prompt_time_slider.value()
            self.prompt_time_label.setText("%5.3f s" % (self.prompt_time/1000,))

        def on_sample_num(self):
            self.sample_num = self.sample_num_slider.value()
            self.sample_num_label.setText(str(self.sample_num))


class PromptConfigWidget(QWidget):
    """
    Widget for configuring the details of how and when the eye prompter samples data
    """

    def __init__(self, disk_dir: str):
        super(PromptConfigWidget, self).__init__()

        self.disk_dir = disk_dir

        self.configs = dict()
        self.current_config = ""
        for e in os.listdir(os.path.join(self.disk_dir, "PromptConfigurations")):
            if e.split(".")[-1] == "json":
                if not self.current_config:
                    self.current_config = e[:-5]
                with open(os.path.join(self.disk_dir, "PromptConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.config_select = QComboBox()
        self.config_select.setMinimumWidth(100)
        for k in self.configs.keys():
            self.config_select.addItem(k)
        self.new_config = QPushButton("+")
        self.new_config.setMaximumWidth(20)
        self.del_config = QPushButton("-")
        self.del_config.setMaximumWidth(20)

        selection_layout = QHBoxLayout()
        selection_layout.addWidget(self.config_select)
        selection_layout.addWidget(self.new_config)
        selection_layout.addWidget(self.del_config)
        selection_widget = QWidget()
        selection_widget.setLayout(selection_layout)

        self.name_label = QLabel("Configuration Name: ")
        self.name_label.setMinimumWidth(100)
        self.name_label.setMaximumWidth(1000)
        self.name_box = QLineEdit(self.current_config)
        self.name_box.setMaxLength(50)

        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_box)
        name_widget = QWidget()
        name_widget.setLayout(name_layout)

        configs_widget = QLabel("Configurations: ")

        if self.current_config:
            self.config_options = PromptOptions(self.configs[self.current_config])
        else:
            self.config_options = QWidget()

        layout = QVBoxLayout()
        layout.addWidget(selection_widget)
        layout.addWidget(name_widget)
        layout.addWidget(configs_widget)
        layout.addWidget(self.config_options)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.set_connections()

        if not self.current_config:
            self.del_config.setEnabled(False)
            self.name_box.setEnabled(False)
            self.update()

    def shutdown(self):
        if self.current_config:
            self.configs[self.current_config] = self.config_options.get_config()

        # Deleting old configurations
        for e in os.listdir(os.path.join(self.disk_dir, "PromptConfigurations")):
            if e.split(".")[-1] == "json":
                os.remove(os.path.join(self.disk_dir, "PromptConfigurations", e))

        # Serializing the new configurations
        for k in self.configs:
            with open(os.path.join(self.disk_dir, "PromptConfigurations", k + ".json"), "w") as f:
                json.dump(self.configs[k], f, indent=4)

    # noinspection PyUnresolvedReferences
    def set_connections(self):
        self.config_select.currentIndexChanged.connect(self.on_config_select)
        self.new_config.pressed.connect(self.on_new_config)
        self.del_config.pressed.connect(self.on_del_config)
        self.name_box.returnPressed.connect(self.on_name_box)

    def on_config_select(self, i: int) -> None:
        """
        Called when a new configuration is selected from the drop down at the top of the widget
        :param i: The new index of the configuration selected
        """
        if i == -1:
            self.current_config = ""
            self.del_config.setEnabled(False)
            self.name_box.setText("")
            self.name_box.setEnabled(False)

            self.layout().removeWidget(self.config_options)
            self.config_options.setHidden(True)
            self.config_options.destroy()
            self.config_options = QWidget()
            self.layout().addWidget(self.config_options)
            self.update()
            return

        if self.current_config:
            self.configs[self.current_config] = self.config_options.get_config()

        self.current_config = self.config_select.itemText(i)
        self.del_config.setEnabled(True)
        self.name_box.setText(self.current_config)

        self.layout().removeWidget(self.config_options)
        self.config_options.setHidden(True)
        self.config_options.destroy()
        self.config_options = PromptOptions(self.configs[self.current_config])
        self.layout().addWidget(self.config_options)

        self.name_box.setEnabled(True)

    def on_name_box(self) -> None:
        """
        Called when a new name is set for the current configuration
        """
        nName = self.name_box.text()
        self.configs[nName] = self.configs[self.current_config]
        del self.configs[self.current_config]
        self.current_config = nName
        self.config_select.setItemText(self.config_select.currentIndex(), nName)

    def on_new_config(self) -> None:
        """
        Called when a new configuration is to be created by pressing the + button at the top of the widget
        """
        new_config = "configuration-" + str(len(self.configs) + 1)
        self.configs[new_config] = PromptOptions().get_config()
        self.config_select.addItem(new_config)
        self.config_select.setCurrentIndex(len(self.configs) - 1)

    def on_del_config(self) -> None:
        """
        Called when the current configuration is to be deleted by pressing the - button at the top of the widget
        """
        current_config = self.current_config
        combo_idx = self.config_select.currentIndex()
        self.config_select.removeItem(combo_idx)
        self.configs.pop(current_config, None)

        if len(self.config_select) == 0:
            self.current_config = ""
            self.name_box.setText("")

            self.layout().removeWidget(self.config_options)
            self.config_options.setHidden(True)
            self.config_options.destroy()
            self.config_options = QWidget()
            self.layout().addWidget(self.config_options)
            return

        if combo_idx != 0:
            combo_idx -= 1
        self.current_config = self.config_select.itemText(combo_idx)
        self.config_select.setCurrentIndex(combo_idx)
