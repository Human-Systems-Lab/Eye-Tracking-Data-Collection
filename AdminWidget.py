import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListView

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize


class AdminWidget(QWidget):
    """
    Widget for admin related tasks
    """

    def __init__(self):
        super(AdminWidget, self).__init__()

        generate_IAM_layout = QVBoxLayout()
        self.generate_IAM_button = QPushButton("Generate IAM")
        self.generate_IAM_button.setMaximumWidth(200)
        self.generate_IAM_button.setMaximumHeight(100)

        self.generate_IAM_access_key = QLineEdit("Generated Access ID")
        self.generate_IAM_access_key.setMinimumWidth(200)
        self.generate_IAM_access_key.setMaximumWidth(1000)

        self.generate_IAM_secret_access_key = QLineEdit("Generated Secret Access ID")
        self.generate_IAM_secret_access_key.setMinimumWidth(200)
        self.generate_IAM_secret_access_key.setMaximumWidth(1000)

        self.list_label = QLabel("Active IAM Accounts: ")

        self.generated_IAM_users = QListView()
        self.generated_IAM_users.gridSize()
        self.generated_IAM_users.setGridSize(QSize(100, 200))

        self.delete_button = QPushButton("Delete IAM")
        self.delete_button.setMaximumWidth(200)

        generate_IAM_layout.addWidget(self.generate_IAM_button)
        generate_IAM_layout.addWidget(self.generate_IAM_access_key)
        generate_IAM_layout.addWidget(self.generate_IAM_secret_access_key)
        generate_IAM_layout.addWidget(self.list_label)
        generate_IAM_layout.addWidget(self.generated_IAM_users)
        generate_IAM_layout.addWidget(self.delete_button)
        generate_IAM_widget = QWidget()
        generate_IAM_widget.setLayout(generate_IAM_layout)

        layout = QVBoxLayout()
        layout.addWidget(generate_IAM_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def shutdown(self):
        raise NotImplemented()

    def set_connections(self):
        self.generate_IAM_button.pressed.connect(self.on_generate_IAM())
        self.delete_button.pressed.connect(self.on_delete_IAM())
        self.generated_IAM_users.pressed.connect(self.on_active_IAM_select())

    def on_generate_IAM(self):
        raise NotImplemented()

    def on_delete_IAM(self):
        raise NotImplemented()

    def on_active_IAM_select(self):
        raise NotImplemented()



