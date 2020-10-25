import os
import json
from typing import Optional
from functools import wraps

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtCore import Qt

from Serialization import Serializer
from Serialization import DiskSerializer
from Serialization import S3Serializer

documents_dir = os.path.join(os.path.expanduser("~"), "Documents")


def valid_fmt(fmt: str) -> bool:
    char_counts = {}

    for e in fmt:
        if e in char_counts:
            char_counts[e] += 1
        else:
            char_counts[e] = 1

    for k, v in (
            ('Y', 4),
            ('M', 2),
            ('D', 2),
            ('h', 2),
            ('m', 2),
            ('s', 5)
    ):
        if k not in char_counts or char_counts[k] != v:
            return False

    return True


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

    def create_serializer(self) -> Serializer:
        """
        Creates and returns the appropriate serializer for the target options
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
            self.base_dir = documents_dir
            self.img_dir = "images"
            self.img_fmt = "YYYYMMDD/hhmmss-sss"
            self.lbl_dir = "labels"
            self.lbl_fmt = "YYYYMMDD/hhmmss-sss"
        else:
            self.base_dir = data["base_dir"]
            self.img_dir = data["img_dir"]
            self.img_fmt = data["img_fmt"]
            self.lbl_dir = data["lbl_dir"]
            self.lbl_fmt = data["lbl_fmt"]

        self.base_dir_box = None
        self.base_dir_browse = None

        self.img_dir_box = None
        self.img_fmt_box = None

        self.lbl_dir_box = None
        self.lbl_fmt_box = None

        self.build_layout()
        self.set_connections()

    def check_ready(f):
        @wraps(f)
        def func(this, *args, **kwargs):
            if (
                    this.base_dir_box is None or
                    this.base_dir_browse is None or
                    this.img_dir_box is None or
                    this.img_fmt_box is None or
                    this.lbl_dir_box is None or
                    this.lbl_fmt_box is None
            ):
                return

            return f(this, *args, **kwargs)
        return func

    def build_layout(self):
        self.base_dir_box = QLineEdit(self.base_dir)
        self.base_dir_browse = QPushButton("...")
        self.base_dir_browse.setMaximumWidth(30)

        base_dir_layout = QHBoxLayout()
        base_dir_layout.addWidget(self.base_dir_box)
        base_dir_layout.addWidget(self.base_dir_browse)
        base_dir_widget = QWidget()
        base_dir_widget.setLayout(base_dir_layout)

        img_dir_lbl = QLabel("Image path: ")
        self.img_dir_box = QLineEdit(self.img_dir)

        img_dir_layout = QHBoxLayout()
        img_dir_layout.addWidget(img_dir_lbl)
        img_dir_layout.addWidget(self.img_dir_box)
        img_dir_widget = QWidget()
        img_dir_widget.setLayout(img_dir_layout)

        img_fmt_lbl = QLabel("Image data format: ")
        self.img_fmt_box = QLineEdit(self.img_fmt)

        img_fmt_layout = QHBoxLayout()
        img_fmt_layout.addWidget(img_fmt_lbl)
        img_fmt_layout.addWidget(self.img_fmt_box)
        img_fmt_widget = QWidget()
        img_fmt_widget.setLayout(img_fmt_layout)

        lbl_dir_lbl = QLabel("Label path: ")
        self.lbl_dir_box = QLineEdit(self.lbl_dir)

        lbl_dir_layout = QHBoxLayout()
        lbl_dir_layout.addWidget(lbl_dir_lbl)
        lbl_dir_layout.addWidget(self.lbl_dir_box)
        lbl_dir_widget = QWidget()
        lbl_dir_widget.setLayout(lbl_dir_layout)

        lbl_fmt_lbl = QLabel("Label data format: ")
        self.lbl_fmt_box = QLineEdit(self.lbl_fmt)

        lbl_fmt_layout = QHBoxLayout()
        lbl_fmt_layout.addWidget(lbl_fmt_lbl)
        lbl_fmt_layout.addWidget(self.lbl_fmt_box)
        lbl_fmt_widget = QWidget()
        lbl_fmt_widget.setLayout(lbl_fmt_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Disk Output Options"))
        layout.addWidget(base_dir_widget)
        layout.addWidget(img_dir_widget)
        layout.addWidget(img_fmt_widget)
        layout.addWidget(lbl_dir_widget)
        layout.addWidget(lbl_fmt_widget)
        self.setLayout(layout)

    def set_connections(self):
        self.base_dir_box.returnPressed.connect(self.on_base_dir_box)
        self.base_dir_browse.pressed.connect(self.on_base_dir_browse)
        self.img_dir_box.returnPressed.connect(self.on_img_dir_box)
        self.img_fmt_box.returnPressed.connect(self.on_img_fmt_box)
        self.lbl_dir_box.returnPressed.connect(self.on_lbl_dir_box)
        self.lbl_fmt_box.returnPressed.connect(self.on_lbl_fmt_box)

    @check_ready
    def on_base_dir_box(self):
        new_base_dir = self.base_dir_box.text()
        if os.path.isdir(new_base_dir):
            self.base_dir = new_base_dir
        else:
            self.base_dir_box.setText(self.base_dir)

    @check_ready
    def on_base_dir_browse(self):
        dialog = QFileDialog(self, "Base Output Directory", self.base_dir)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec_() == QFileDialog.Accepted:
            self.base_dir = dialog.selectedFiles()[0]
            self.base_dir_box.setText(self.base_dir)

    @check_ready
    def on_img_dir_box(self):
        self.img_dir = self.img_dir_box.text()

    @check_ready
    def on_img_fmt_box(self):
        new_img_fmt = self.img_fmt_box.text()
        if valid_fmt(new_img_fmt):
            self.img_fmt = new_img_fmt
        else:
            self.img_fmt_box.setText(self.img_fmt)

    @check_ready
    def on_lbl_dir_box(self):
        self.lbl_dir = self.lbl_dir_box.text()

    @check_ready
    def on_lbl_fmt_box(self):
        new_lbl_fmt = self.lbl_fmt_box.text()
        if valid_fmt(new_lbl_fmt):
            self.lbl_fmt = new_lbl_fmt
        else:
            self.lbl_fmt_box.setText(self.lbl_fmt)

    def get_config(self):
        return {
            "type": "Disk",
            "base_dir": self.base_dir,
            "img_dir": self.img_dir,
            "img_fmt": self.img_fmt,
            "lbl_dir": self.lbl_dir,
            "lbl_fmt": self.lbl_fmt
        }

    def create_serializer(self) -> Serializer:
        pass


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

    def create_serializer(self) -> Serializer:
        pass


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
        self.current_config = ""
        for e in os.listdir(os.path.join(self.disk_dir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                if not self.current_config:
                    self.current_config = e[:-5]
                with open(os.path.join(self.disk_dir, "DataOutputConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.config_select = QComboBox()
        self.config_select.setMinimumWidth(100)
        # self.configCombos.removeItem()
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
        self.name_label.setMaximumWidth(100)
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
        layout.addWidget(selection_widget)
        layout.addWidget(name_widget)
        layout.addWidget(target_widget)
        layout.addWidget(self.target_options)
        layout.setAlignment(Qt.AlignTop)
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
        if self.current_config:
            self.configs[self.current_config] = self.target_options.get_config()

        # Deleting old configurations
        for e in os.listdir(os.path.join(self.disk_dir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                os.remove(os.path.join(self.disk_dir, "DataOutputConfigurations", e))

        # Serializing the new configurations
        for k in self.configs:
            with open(os.path.join(self.disk_dir, "DataOutputConfigurations", k + ".json"), "w") as f:
                json.dump(self.configs[k], f, indent=4)

    def check_ready(f):
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

    def set_connections(self):
        """
        Sets up all the connections between the components of the DataOutputOptions widget
        """
        self.config_select.currentIndexChanged.connect(self.on_config_select)
        self.new_config.pressed.connect(self.on_new_config)
        self.del_config.pressed.connect(self.on_del_config)
        self.name_box.returnPressed.connect(self.on_name_box)
        self.target_select.currentIndexChanged.connect(self.on_target_select)

    @check_ready
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
            self.target_select.setEnabled(False)
            self.layout().removeWidget(self.target_options)
            self.target_options.setHidden(True)
            self.target_options.destroy()
            self.target_options = QWidget()
            self.layout().addWidget(self.target_options)
            self.update()
            return

        if self.current_config:
            self.configs[self.current_config] = self.target_options.get_config()

        self.current_config = self.config_select.itemText(i)
        self.del_config.setEnabled(True)
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

    @check_ready
    def on_name_box(self) -> None:
        """
        Called when a new name is set for the current configuration
        """
        nName = self.name_box.text()
        self.configs[nName] = self.configs[self.current_config]
        del self.configs[self.current_config]
        self.current_config = nName
        self.config_select.setItemText(self.config_select.currentIndex(), nName)

    @check_ready
    def on_new_config(self) -> None:
        """
        Called when a new configuration is to be created by pressing the + button at the top of the widget
        """
        new_config = "configuration-" + str(len(self.configs) + 1)
        self.configs[new_config] = self.target_widgets[0]().get_config()
        self.config_select.addItem(new_config)
        self.config_select.setCurrentIndex(len(self.configs) - 1)

    @check_ready
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

    @check_ready
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

    def create_serializer(self) -> Serializer:
        if not self.current_config:
            raise ValueError("A configuration is not selected")
        return self.target_options.create_serializer()
