import os
import json
from typing import Dict, Any

from PyQt5 import QtGui

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import Qt


class DiskTargetOptions(QWidget):
    pass


class S3TargetOptions(QWidget):
    pass


class DataOutputOptions(QWidget):
    def __init__(self, diskDir: str):
        super(DataOutputOptions, self).__init__()

        self.diskDir = diskDir

        # Loading configurations and selecting a current configuration
        self.configs = dict()
        self.currentConfig = None
        for e in os.listdir(os.path.join(self.diskDir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                if self.currentConfig is None:
                    self.currentConfig = e[:-5]
                with open(os.path.join(self.diskDir, "DataOutputConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.configCombos = None
        self.newConfig = None
        self.nameLabel = None
        self.nameBox = None
        self.optionsLabel = None

        self.buildLayout()
        self.rebuildLayout = False

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if self.rebuildLayout:
            self.buildLayout()
            self.rebuildLayout = False
        super().paintEvent(a0)

    def buildLayout(self):
        layout = QVBoxLayout()

        self.configCombos = QComboBox()
        self.configCombos.setMinimumWidth(100)
        for k in self.configs.keys():
            self.configCombos.addItem(k)
        self.newConfig = QPushButton("+")
        self.newConfig.setMaximumWidth(20)

        selectionLayout = QHBoxLayout()
        selectionLayout.addWidget(self.configCombos)
        selectionLayout.addWidget(self.newConfig)
        selectionWidget = QWidget()
        selectionWidget.setLayout(selectionLayout)

        self.nameLabel = QLabel("Configuration Name: ")
        self.nameLabel.setMinimumWidth(100)
        self.nameLabel.setMaximumWidth(100)
        self.nameBox = QLineEdit(self.currentConfig)
        self.nameBox.setMaxLength(50)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.nameLabel)
        nameLayout.addWidget(self.nameBox)
        nameWidget = QWidget()
        nameWidget.setLayout(nameLayout)

        if self.currentConfig is not None:
            self.optionsLabel = QLabel("%s Output Options:" % self.configs[self.currentConfig]["type"])
        else:
            self.optionsLabel = QLabel("")

        layout.addWidget(selectionWidget)
        layout.addWidget(nameWidget)
        layout.addWidget(self.optionsLabel)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.setConnections()

    def setConnections(self):
        self.configCombos.currentIndexChanged.connect(self.onSelect)
        self.nameBox.returnPressed.connect(self.onNameChange)

    def onSelect(self, i: int) -> None:
        if self.nameBox is None:
            return

        self.currentConfig = self.configCombos.itemText(i)
        self.nameBox.setText(self.currentConfig)
        self.optionsLabel.setText("%s Output Options:" % self.configs[self.currentConfig]["type"])

    def onNameChange(self):
        nName = self.nameBox.text()
        self.configs[nName] = self.configs[self.currentConfig]
        del self.configs[self.currentConfig]
        self.currentConfig = nName
        self.configCombos.setItemText(self.configCombos.currentIndex(), nName)
