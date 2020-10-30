import os
import sys
import platform

from PyQt5 import QtGui

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QTextEdit

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt


from OutputConfigWidget import OutputConfigWidget
from Prompter import EyePrompt

disk_dir = ""


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setCursor(Qt.ArrowCursor)

        self.setWindowIcon(QtGui.QIcon("assets/HSL-logo.png"))
        self.setWindowTitle("HSL | Eye Tracking Data Collection")
        self.setGeometry(100, 100, 900, 900)

        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("Save")

        # Building the Data Output widget
        self.data_output = QDockWidget("Data Output", self)
        self.data_output_options = OutputConfigWidget(disk_dir)
        self.data_output.setWidget(self.data_output_options)
        self.data_output.setFloating(False)

        self.setCentralWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, self.data_output)

    def shutdown(self):
        self.data_output_options.shutdown()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        if k == Qt.Key_R:
            try:
                prompter = EyePrompt()
                prompter.showFullScreen()
                prompter.cycleLength = 2
                prompter.serializer = self.data_output_options.create_serializer()
                prompter.startPrompts()
            except ValueError:
                pass


def main():
    global disk_dir
    plat = platform.system()
    if plat == "Windows":
        disk_dir = os.path.join(os.getenv("APPDATA"), "HSL")
    elif plat == "Linux":
        disk_dir = os.path.join(os.path.expanduser("~"), ".HSL")
    else:
        print("Unsupported operating system: %s" % plat)
        print("This software only supports Windows and Linux")
        exit(1)

    if not os.path.isdir(disk_dir):
        os.mkdir(disk_dir)
    disk_dir = os.path.join(disk_dir, "EyeTracking-DataCollection")
    if not os.path.isdir(disk_dir):
        os.mkdir(disk_dir)

    output_configs_path = os.path.join(disk_dir, "DataOutputConfigurations")
    if not os.path.isdir(output_configs_path):
        os.mkdir(output_configs_path)
    prompt_configs_path = os.path.join(disk_dir, "PromptConfigurations")
    if not os.path.isdir(prompt_configs_path):
        os.mkdir(prompt_configs_path)
    cache_path = os.path.join(disk_dir, "cache")
    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    e_code = app.exec_()
    window.shutdown()
    sys.exit(e_code)


if __name__ == "__main__":
    main()
