import os
import json

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtCore import Qt


class ConfigOptions(QWidget):
    def __init__(self, data=None):
        super(ConfigOptions, self).__init__()
        pass

    def get_config(self):
        return {}


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
            self.config_options = ConfigOptions()
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
        self.config_options = ConfigOptions(self.configs[self.current_config])
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
        self.configs[new_config] = ConfigOptions().get_config()
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
