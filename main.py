import os
import sys
import platform
import ctypes

from PyQt5 import QtGui

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDockWidget

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt


from OutputConfigWidget import OutputConfigWidget
from PromptConfigWidget import PromptConfigWidget
from Prompter import create_prompter

disk_dir = ""


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setCursor(Qt.ArrowCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowIcon(QtGui.QIcon(resource_path("assets/HSL-logo.png")))
        self.setWindowTitle("HSL | Eye Tracking Data Collection")
        self.setGeometry(100, 100, 900, 900)

        # output configurations widget
        self.output_config_widget = OutputConfigWidget(disk_dir)
        output_config = QDockWidget("Data Output", self)
        output_config.setWidget(self.output_config_widget)
        output_config.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, output_config)

        # prompter configurations widget
        self.prompt_config_widget = PromptConfigWidget(disk_dir)
        prompt_config = QDockWidget("Prompter Configuration", self)
        prompt_config.setWidget(self.prompt_config_widget)
        prompt_config.setFloating(False)
        self.setCentralWidget(prompt_config)

    def shutdown(self):
        self.output_config_widget.shutdown()
        self.prompt_config_widget.shutdown()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        modifiers = QApplication.keyboardModifiers()
        if k == Qt.Key_R and modifiers == Qt.ControlModifier:
            config = self.prompt_config_widget.get_config()
            serializer = self.output_config_widget.create_serializer()
            if config is None:
                return super().keyPressEvent(e)
            prompter = create_prompter(config, serializer)
            prompter.showFullScreen()
            prompter.start_prompts()
        else:
            return super().keyPressEvent(e)


# used to include the icon in the pyinstall build
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def main():
    global disk_dir
    plat = platform.system()
    if plat == "Windows":
        disk_dir = os.path.join(os.getenv("APPDATA"), "HSL")
        my_app_id = u'HSL.EyeTracking.DataCollector'  # arbitrary string
        # set taskbar icon to same as the window app icon
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

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
