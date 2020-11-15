import os
import json

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QComboBox

from PyQt5.QtCore import Qt


class AdminWidget(QWidget):
    """
    Widget for admin related tasks
    """

    def __init__(self, disk_dir: str):
        super(AdminWidget, self).__init__()

        self.disk_dir = disk_dir

        self.IAM_accounts = dict()

        for e in os.listdir(os.path.join(self.disk_dir, "IAM-accounts")):
            if e.split(".")[-1] == "json":
                with open(os.path.join(self.disk_dir, "IAM-accounts", e)) as f:
                    self.IAM_accounts[e[:-5]] = json.load(f)

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

        self.current_IAM_account_access_key = QLineEdit("Selected Access ID")
        self.current_IAM_account_access_key.setMinimumWidth(200)
        self.current_IAM_account_access_key.setMaximumWidth(1000)

        self.current_IAM_account_secret_key = QLineEdit("Selected Secret ID")
        self.current_IAM_account_secret_key.setMinimumWidth(200)
        self.current_IAM_account_secret_key.setMaximumWidth(1000)

        self.list_label = QLabel("Active IAM Accounts: ")

        self.generated_IAM_users = QComboBox()
        for k in self.IAM_accounts.keys():
            self.generated_IAM_users.addItem(k)

        self.delete_button = QPushButton("Delete IAM")
        self.delete_button.setMaximumWidth(200)

        generate_IAM_layout.addWidget(self.generate_IAM_button)
        generate_IAM_layout.addWidget(self.generate_IAM_access_key)
        generate_IAM_layout.addWidget(self.generate_IAM_secret_access_key)

        generate_IAM_widget = QWidget()
        generate_IAM_widget.setLayout(generate_IAM_layout)

        select_IAM_layout = QVBoxLayout()
        select_IAM_layout.addWidget(self.list_label)
        select_IAM_layout.addWidget(self.generated_IAM_users)
        select_IAM_layout.addWidget(self.current_IAM_account_access_key)
        select_IAM_layout.addWidget(self.current_IAM_account_secret_key)
        select_IAM_layout.addWidget(self.delete_button)

        select_IAM_widget = QWidget()
        select_IAM_widget.setLayout(select_IAM_layout)

        layout = QVBoxLayout()
        layout.addWidget(generate_IAM_widget)
        layout.addWidget(select_IAM_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def shutdown(self):
        raise NotImplemented()

    def set_connections(self):
        self.generate_IAM_button.pressed.connect(self.on_generate_IAM())
        self.delete_button.pressed.connect(self.on_delete_IAM())
        self.generated_IAM_users.currentIndexChanged.connect(self.on_account_select())

    def on_generate_IAM(self):
        # generate the new IAM account
        # add it to the list of active accounts
        # fill it into the generated text fields
        new_IAM = {
            'access_id': 'NewlyGeneratedAccessID',
            'secret_id': 'NewlyGeneratedSecretID'
        }

        self.generated_IAM_users.addItem(self, "account-" + str(len(self.IAM_accounts)))
        self.generated_IAM_users.setCurrentIndex(len(self.IAM_accounts) - 1)
        self.generated_IAM_users.setCurrentText("account-" + str(len(self.IAM_accounts)))

    def on_delete_IAM(self):
        raise NotImplemented()

    def on_account_select(self):
        raise NotImplemented()

    def on_active_IAM_select(self):
        raise NotImplemented()



