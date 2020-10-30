import os
import json

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout


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

        target_label = QLabel("Output target: ")
        self.target_select = QComboBox()
        for e in self.targets:
            self.target_select.addItem(e)
        if self.current_config:
            self.target_select.setCurrentIndex(self.targets.index(self.configs[self.current_config]["type"]))

        target_layout = QHBoxLayout()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_select)
        target_widget = QWidget()
        target_widget.setLayout(target_layout)

        if self.current_config:
            self.target_options = self.target_widgets[self.targets.index(self.configs[self.current_config]["type"])](
                self.configs[self.current_config])
        else:
            self.target_options = QWidget()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.set_connections()

        if not self.current_config:
            self.del_config.setEnabled(False)
            self.name_box.setEnabled(False)
            self.target_select.setEnabled(False)

            self.layout().removeWidget(self.target_options)
            self.target_options.setHidden(True)
            self.target_options.destroy()
            self.target_options = QWidget()
            self.layout().addWidget(self.target_options)
            self.update()

    def shutdown(self):
        pass

    # noinspection PyUnresolvedReferences
    def set_connections(self):
        pass
