import os
import json
from functools import wraps

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import Qt


class TargetOptions(QWidget):
    """
    Abstract base class for all widgets representing an output target
    All targets must be able to be json serialized through the get_config() method
    """
    def get_config(self):
        """
        Serializes the current options selected for the output target
        :return: json representation of the options
        """
        raise NotImplementedError()


class DiskTargetOptions(TargetOptions):
    """
    Widget for managing the options for a disk target
    """
    def __init__(self, data=None):
        """
        :param data: serialized data retrieved from a get_config() call to initialize the widget
        """
        super(DiskTargetOptions, self).__init__()

        if data is None:
            self.textBox = QLineEdit("init")
        else:
            self.textBox = QLineEdit(data["data"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Disk"))
        layout.addWidget(self.textBox)
        self.setLayout(layout)

    def get_config(self):
        return {
            "type": "Disk",
            "data": self.textBox.text()
        }


class S3TargetOptions(TargetOptions):
    def __init__(self, data=None):
        """
        :param data: serialized data retrieved from a get_config() call to initialize the widget
        """
        super(S3TargetOptions, self).__init__()

        if data is None:
            self.textBox = QLineEdit("init")
        else:
            self.textBox = QLineEdit(data["data"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("S3"))
        layout.addWidget(self.textBox)
        self.setLayout(layout)

    def get_config(self):
        return {
            "type": "S3",
            "data": self.textBox.text()
        }


def checkReady(f):
    """
    Only to be used in the DataOutputOptions class for slot functions
    Ensures components of the widget are initialized
    """
    @wraps(f)
    def func(self, *args, **kwargs):
        if (
                self.config_select is None or
                self.new_config is None or
                self.del_config is None or
                self.name_label is None or
                self.name_box is None or
                self.target_select is None or
                self.target_options is None
        ):
            return

        return f(self, *args, **kwargs)
    return func


class DataOutputOptions(QWidget):
    """
    Widget for setting up the data serialization for the application
    """

    def __init__(self, disk_dir: str):
        super(DataOutputOptions, self).__init__()

        self.disk_dir = disk_dir
        self.targets = ["Disk", "S3"]
        self.target_widgets = [DiskTargetOptions, S3TargetOptions]

        # Loading configurations and selecting a current configuration
        self.configs = dict()
        self.current_config = None
        for e in os.listdir(os.path.join(self.disk_dir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                if self.current_config is None:
                    self.current_config = e[:-5]
                with open(os.path.join(self.disk_dir, "DataOutputConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.config_select = None
        self.new_config = None
        self.del_config = None
        self.name_label = None
        self.name_box = None
        self.target_select = None

        self.target_options = None

        self.build_layout()
        self.set_connections()

    def build_layout(self):
        """
        Initializes all the components of the DataOutputOptions widget
        """
        self.config_select = QComboBox()
        self.config_select.setMinimumWidth(100)
        # self.configCombos.removeItem()
        for k in self.configs.keys():
            self.config_select.addItem(k)
        self.new_config = QPushButton("+")
        self.new_config.setMaximumWidth(20)
        self.del_config = QPushButton("-")
        self.del_config.setMaximumWidth(20)

        selectionLayout = QHBoxLayout()
        selectionLayout.addWidget(self.config_select)
        selectionLayout.addWidget(self.new_config)
        selectionLayout.addWidget(self.del_config)
        selectionWidget = QWidget()
        selectionWidget.setLayout(selectionLayout)

        self.name_label = QLabel("Configuration Name: ")
        self.name_label.setMinimumWidth(100)
        self.name_label.setMaximumWidth(1000)
        self.name_box = QLineEdit(self.current_config)
        self.name_box.setMaxLength(50)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.name_label)
        nameLayout.addWidget(self.name_box)
        nameWidget = QWidget()
        nameWidget.setLayout(nameLayout)

        targetLabel = QLabel("Output target: ")
        self.target_select = QComboBox()
        for e in self.targets:
            self.target_select.addItem(e)
        self.target_select.setCurrentIndex(self.targets.index(self.configs[self.current_config]["type"]))

        targetLayout = QHBoxLayout()
        targetLayout.addWidget(targetLabel)
        targetLayout.addWidget(self.target_select)
        targetWidget = QWidget()
        targetWidget.setLayout(targetLayout)

        self.target_options = self.target_widgets[self.targets.index(self.configs[self.current_config]["type"])](
            self.configs[self.current_config])

        layout = QVBoxLayout()
        layout.addWidget(selectionWidget)
        layout.addWidget(nameWidget)
        layout.addWidget(targetWidget)
        layout.addWidget(self.target_options)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def set_connections(self):
        """
        Sets up all the connections between the components of the DataOutputOptions widget
        """
        self.config_select.currentIndexChanged.connect(self.on_config_select)
        self.new_config.pressed.connect(self.on_new_config)
        self.del_config.pressed.connect(self.on_del_config)
        self.name_box.returnPressed.connect(self.on_name_box)
        self.target_select.currentIndexChanged.connect(self.on_target_select)

    @checkReady
    def on_config_select(self, i: int) -> None:
        """
        Called when a new configuration is selected from the drop down at the top of the widget
        :param i: The new index of the configuration selected
        """
        if i == -1:
            self.current_config = ""
            self.name_box.setText("")
            self.name_box.setEnabled(False)
            self.target_select.setEnabled(False)
            self.layout().removeWidget(self.target_options)
            self.target_options.setHidden(True)
            self.target_options.destroy()
            self.target_options = QWidget()
            self.layout().addWidget(self.target_options)
            self.update()
            return

        self.current_config = self.config_select.itemText(i)
        self.name_box.setText(self.current_config)
        self.target_select.setCurrentIndex(self.targets.index(self.configs[self.current_config]["type"]))
        self.layout().removeWidget(self.target_options)
        self.target_options.setHidden(True)
        self.target_options.destroy()
        self.target_options = self.target_widgets[self.targets.index(self.configs[self.current_config]["type"])](
            self.configs[self.current_config])
        self.layout().addWidget(self.target_options)

        self.name_box.setEnabled(True)
        self.target_select.setEnabled(True)

    @checkReady
    def on_name_box(self) -> None:
        """
        Called when a new name is set for the current configuration
        """
        nName = self.name_box.text()
        self.configs[nName] = self.configs[self.current_config]
        del self.configs[self.current_config]
        self.current_config = nName
        self.config_select.setItemText(self.config_select.currentIndex(), nName)

    @checkReady
    def on_new_config(self) -> None:
        """
        Called when a new configuration is to be created by pressing the + button at the top of the widget
        """
        self.current_config = "configuration-" + str(len(self.configs) + 1)
        self.configs[self.current_config] = self.target_widgets[0]().get_config()
        self.name_box.setText(self.current_config)
        self.config_select.addItem(self.current_config)
        self.config_select.setCurrentIndex(len(self.configs) - 1)

    @checkReady
    def on_del_config(self) -> None:
        """
        Called when the current configuration is to be deleted by pressing the - button at the top of the widget
        """
        i = list(self.configs).index(self.current_config)
        del self.configs[self.current_config]
        self.config_select.removeItem(i)
        if i != 0:
            i -= 1
        elif len(self.config_select) == 0:
            self.current_config = ""
            self.name_box.setText("")
            self.target_select.setEnabled(False)
            self.layout().removeWidget(self.target_options)
            self.target_options.setHidden(True)
            self.target_options.destroy()
            self.target_options = QWidget()
            self.layout().addWidget(self.target_options)
            return

        self.current_config = list(self.configs)[i]

    @checkReady
    def on_target_select(self, i: int) -> None:
        """
        Called when the output target type is changed, ex. Disk to S3
        :param i: The index of the output target selected
        """
        if self.configs[self.current_config]["type"] != self.targets[i]:
            self.layout().removeWidget(self.target_options)
            self.target_options.setHidden(True)
            self.target_options.destroy()
            self.target_options = self.target_widgets[i]()
            self.layout().addWidget(self.target_options)
            self.configs[self.current_config] = self.target_options.get_config()
