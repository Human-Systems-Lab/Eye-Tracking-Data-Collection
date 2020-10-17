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
    def getConfig(self):
        raise NotImplementedError()


class DiskTargetOptions(TargetOptions):
    def __init__(self, data=None):
        super(DiskTargetOptions, self).__init__()

        if data is None:
            self.textBox = QLineEdit("init")
        else:
            self.textBox = QLineEdit(data["data"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Disk"))
        layout.addWidget(self.textBox)
        self.setLayout(layout)

    def getConfig(self):
        return {"type": "Disk", "data": self.textBox.text()}


class S3TargetOptions(TargetOptions):
    def __init__(self, data=None):
        super(S3TargetOptions, self).__init__()

        if data is None:
            self.textBox = QLineEdit("init")
        else:
            self.textBox = QLineEdit(data["data"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("S3"))
        layout.addWidget(self.textBox)
        self.setLayout(layout)

    def getConfig(self):
        return {"type": "S3", "data": self.textBox.text()}


def checkReady(f):
    @wraps(f)
    def func(self, *args, **kwargs):
        if (
                self.configSelect is None or
                self.newConfig is None or
                self.delConfig is None or
                self.nameLabel is None or
                self.nameBox is None or
                self.targetSelect is None or
                self.targetOptions is None
        ):
            return

        return f(self, *args, **kwargs)
    return func


class DataOutputOptions(QWidget):
    def __init__(self, diskDir: str):
        super(DataOutputOptions, self).__init__()

        self.diskDir = diskDir
        self.targets = ["Disk", "S3"]
        self.targetWidgets = [DiskTargetOptions, S3TargetOptions]

        # Loading configurations and selecting a current configuration
        self.configs = dict()
        self.currentConfig = None
        for e in os.listdir(os.path.join(self.diskDir, "DataOutputConfigurations")):
            if e.split(".")[-1] == "json":
                if self.currentConfig is None:
                    self.currentConfig = e[:-5]
                with open(os.path.join(self.diskDir, "DataOutputConfigurations", e)) as f:
                    self.configs[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        self.configSelect = None
        self.newConfig = None
        self.delConfig = None
        self.nameLabel = None
        self.nameBox = None
        self.targetSelect = None

        self.targetOptions = None

        self.buildLayout()
        self.setConnections()

    def buildLayout(self):
        self.configSelect = QComboBox()
        self.configSelect.setMinimumWidth(100)
        # self.configCombos.removeItem()
        for k in self.configs.keys():
            self.configSelect.addItem(k)
        self.newConfig = QPushButton("+")
        self.newConfig.setMaximumWidth(20)
        self.delConfig = QPushButton("-")
        self.delConfig.setMaximumWidth(20)

        selectionLayout = QHBoxLayout()
        selectionLayout.addWidget(self.configSelect)
        selectionLayout.addWidget(self.newConfig)
        selectionLayout.addWidget(self.delConfig)
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

        targetLabel = QLabel("Output target: ")
        self.targetSelect = QComboBox()
        for e in self.targets:
            self.targetSelect.addItem(e)
        self.targetSelect.setCurrentIndex(self.targets.index(self.configs[self.currentConfig]["type"]))

        targetLayout = QHBoxLayout()
        targetLayout.addWidget(targetLabel)
        targetLayout.addWidget(self.targetSelect)
        targetWidget = QWidget()
        targetWidget.setLayout(targetLayout)

        self.targetOptions = self.targetWidgets[self.targets.index(self.configs[self.currentConfig]["type"])](
            self.configs[self.currentConfig])

        layout = QVBoxLayout()
        layout.addWidget(selectionWidget)
        layout.addWidget(nameWidget)
        layout.addWidget(targetWidget)
        layout.addWidget(self.targetOptions)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def setConnections(self):
        self.configSelect.currentIndexChanged.connect(self.onConfigSelect)
        self.newConfig.pressed.connect(self.onNewConfig)
        self.delConfig.pressed.connect(self.onDelConfig)
        self.nameBox.returnPressed.connect(self.onNameBox)
        self.targetSelect.currentIndexChanged.connect(self.onTargetSelect)

    @checkReady
    def onConfigSelect(self, i: int) -> None:
        if i == -1:
            self.currentConfig = ""
            self.nameBox.setText("")
            self.nameBox.setEnabled(False)
            self.targetSelect.setEnabled(False)
            self.layout().removeWidget(self.targetOptions)
            self.targetOptions.setHidden(True)
            self.targetOptions.destroy()
            self.targetOptions = QWidget()
            self.layout().addWidget(self.targetOptions)
            self.update()
            return

        self.currentConfig = self.configSelect.itemText(i)
        self.nameBox.setText(self.currentConfig)
        self.targetSelect.setCurrentIndex(self.targets.index(self.configs[self.currentConfig]["type"]))
        self.layout().removeWidget(self.targetOptions)
        self.targetOptions.setHidden(True)
        self.targetOptions.destroy()
        self.targetOptions = self.targetWidgets[self.targets.index(self.configs[self.currentConfig]["type"])](
            self.configs[self.currentConfig])
        self.layout().addWidget(self.targetOptions)

        self.nameBox.setEnabled(True)
        self.targetSelect.setEnabled(True)

    @checkReady
    def onNameBox(self) -> None:
        nName = self.nameBox.text()
        self.configs[nName] = self.configs[self.currentConfig]
        del self.configs[self.currentConfig]
        self.currentConfig = nName
        self.configSelect.setItemText(self.configSelect.currentIndex(), nName)

    @checkReady
    def onNewConfig(self) -> None:
        self.currentConfig = "configuration-" + str(len(self.configs) + 1)
        self.configs[self.currentConfig] = self.targetWidgets[0]().getConfig()
        self.nameBox.setText(self.currentConfig)
        self.configSelect.addItem(self.currentConfig)
        self.configSelect.setCurrentIndex(len(self.configs) - 1)

    @checkReady
    def onDelConfig(self) -> None:
        i = list(self.configs).index(self.currentConfig)
        del self.configs[self.currentConfig]
        self.configSelect.removeItem(i)
        if i != 0:
            i -= 1
        elif len(self.configSelect) == 0:
            self.currentConfig = ""
            self.nameBox.setText("")
            self.targetSelect.setEnabled(False)
            self.layout().removeWidget(self.targetOptions)
            self.targetOptions.setHidden(True)
            self.targetOptions.destroy()
            self.targetOptions = QWidget()
            self.layout().addWidget(self.targetOptions)
            return

        self.currentConfig = list(self.configs)[i]

    @checkReady
    def onTargetSelect(self, i: int) -> None:
        if self.configs[self.currentConfig]["type"] != self.targets[i]:
            self.layout().removeWidget(self.targetOptions)
            self.targetOptions.setHidden(True)
            self.targetOptions.destroy()
            self.targetOptions = self.targetWidgets[i]()
            self.layout().addWidget(self.targetOptions)
            self.configs[self.currentConfig] = self.targetOptions.getConfig()
