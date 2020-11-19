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
from AdminWidget import AdminWidget
from Prompter import EyePrompt
from MenuBar import MenuBar
from LoginWindow import LoginWidget

disk_dir = ""


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setCursor(Qt.ArrowCursor)

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

        # admin tools widget
        self.admin_tools_widget = AdminWidget(disk_dir)
        admin_widget = QDockWidget("Admin Tools", self)
        admin_widget.setWidget(self.admin_tools_widget)
        admin_widget.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, admin_widget)

        # menu bar
        self.menu_bar = MenuBar(disk_dir, self)

    def shutdown(self):
        self.output_config_widget.shutdown()
        self.prompt_config_widget.shutdown()
        self.admin_tools_widget.shutdown()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        k = e.key()
        modifiers = QApplication.keyboardModifiers()
        if k == Qt.Key_R and modifiers == Qt.ControlModifier:
            try:
                prompter = EyePrompt()
                prompter.showFullScreen()
                prompter.cycleLength = 2
                prompter.serializer = self.output_config_widget.create_serializer()
                prompter.startPrompts()
            except ValueError:
                pass

    # function to create login window
    @staticmethod
    def drawLoginPopup(self):
        self.admin_login_widget = LoginWidget(disk_dir)
        login_widget = QDockWidget("Administrator Login", self)
        login_widget.setWidget(self.admin_login_widget)
        login_widget.setFloating(True)
        self.addDockWidget(Qt.LeftDockWidgetArea, login_widget)


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
    IAM_path = os.path.join(disk_dir, "IAM-Accounts")
    if not os.path.isdir(IAM_path):
        os.mkdir(IAM_path)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    e_code = app.exec_()
    window.shutdown()
    sys.exit(e_code)


if __name__ == "__main__":
    main()
