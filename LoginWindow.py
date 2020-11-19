import os
import json
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt



class LoginWidget(QWidget):
    """
    Widget for login fields
    """

    def __init__(self, disk_dir: str):
        super(LoginWidget, self).__init__()

        self.disk_dir = disk_dir


        login_fields_layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.password_label = QLabel("Password:")

        self.username_text_field = QLineEdit("")
        self.username_text_field.setMinimumWidth(200)
        self.username_text_field.setMaximumWidth(1000)

        self.password_text_field = QLineEdit("")
        self.password_text_field.setMinimumWidth(200)
        self.password_text_field.setMaximumWidth(1000)

        # username label and text field
        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_text_field)
        username_widget = QWidget()
        username_widget.setLayout(username_layout)

        # password label and text field
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_text_field)
        password_widget = QWidget()
        password_widget.setLayout(password_layout)

        self.login_button = QPushButton("LOGIN")
        self.login_button.setMaximumWidth(200)

        login_fields_layout.addWidget(username_widget)
        login_fields_layout.addWidget(password_widget)
        login_fields_layout.addWidget(self.login_button)
        login_fields_layout.setAlignment(Qt.AlignCenter)

        self.setLayout(login_fields_layout)

        self.set_connections()


    def shutdown(self):
        raise NotImplemented

    def set_connections(self):
        """
        Sets up all of the connections between the components of the Widget
        """
        self.login_button.pressed.connect(self.login)

    def login(self):
        print("Login button pressed")
        self.close()







