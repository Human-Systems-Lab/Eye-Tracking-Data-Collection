import os
import json

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtCore import Qt


class AdminWidget(QWidget):
    """
    Widget for admin related tasks
    """

    def __init__(self, disk_dir: str):
        super(AdminWidget, self).__init__()

        self.disk_dir = disk_dir

        self.credentials = dict()
        self.current_credentials = ""
        for e in os.listdir(os.path.join(self.disk_dir, "IAM-Accounts")):
            if e.split(".")[-1] == "json":
                if not self.current_credentials:
                    self.current_credentials = e[:-5]
                with open(os.path.join(self.disk_dir, "IAM-Accounts", e)) as f:
                    self.credentials[e[:-5]] = json.load(f)  # e[:-5] will remove the .json extension from the file name

        generate_IAM_layout = QVBoxLayout()
        self.generate_IAM_button = QPushButton("Generate IAM")
        self.generate_IAM_button.setMaximumWidth(200)
        self.generate_IAM_button.setMaximumHeight(100)

        self.generated_access_label = QLabel("Generated Access:")
        self.generated_secret_label = QLabel("Generated Secret:")
        self.current_access_label = QLabel("Selected Access:")
        self.current_secret_label = QLabel("Selected Secret:")

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
        self.generated_IAM_users.setMinimumWidth(100)
        for k in self.credentials.keys():
            self.generated_IAM_users.addItem(k)

        self.account_name_field = QLineEdit("Account Name")
        self.account_name_field.setMaximumWidth(1000)
        self.account_name_field.setMinimumWidth(200)

        generated_access_layout = QHBoxLayout()
        generated_access_layout.addWidget(self.generated_access_label)
        generated_access_layout.addWidget(self.generate_IAM_access_key)
        generated_access_widget = QWidget()
        generated_access_widget.setLayout(generated_access_layout)

        generated_secret_layout = QHBoxLayout()
        generated_secret_layout.addWidget(self.generated_secret_label)
        generated_secret_layout.addWidget(self.generate_IAM_secret_access_key)
        generated_secret_widget = QWidget()
        generated_secret_widget.setLayout(generated_secret_layout)

        self.delete_button = QPushButton("Delete IAM")
        self.delete_button.setMaximumWidth(200)

        generate_IAM_layout.addWidget(self.generate_IAM_button)
        generate_IAM_layout.addWidget(generated_access_widget)
        generate_IAM_layout.addWidget(generated_secret_widget)
        generate_IAM_layout.setAlignment(Qt.AlignCenter)

        generate_IAM_widget = QWidget()
        generate_IAM_widget.setLayout(generate_IAM_layout)

        selected_access_layout = QHBoxLayout()
        selected_access_layout.addWidget(self.current_access_label)
        selected_access_layout.addWidget(self.current_IAM_account_access_key)
        selected_access_widget = QWidget()
        selected_access_widget.setLayout(selected_access_layout)

        selected_secret_layout = QHBoxLayout()
        selected_secret_layout.addWidget(self.current_secret_label)
        selected_secret_layout.addWidget(self.current_IAM_account_secret_key)
        selected_secret_widget = QWidget()
        selected_secret_widget.setLayout(selected_secret_layout)

        select_IAM_layout = QVBoxLayout()
        select_IAM_layout.addWidget(self.list_label)
        select_IAM_layout.addWidget(self.generated_IAM_users)
        select_IAM_layout.addWidget(selected_access_widget)
        select_IAM_layout.addWidget(selected_secret_widget)
        select_IAM_layout.addWidget(self.delete_button)

        select_IAM_widget = QWidget()
        select_IAM_widget.setLayout(select_IAM_layout)

        layout = QVBoxLayout()
        layout.addWidget(generate_IAM_widget)
        layout.addWidget(select_IAM_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.set_connections()

    def get_credentials(self):
        return {
            'access_id': 'NewlyGeneratedAccessID',
            'secret_id': 'NewlyGeneratedSecretID'
        }

    def shutdown(self):
        # remove the old files
        for e in os.listdir(os.path.join(self.disk_dir, "IAM-Accounts")):
            if e.split(".")[-1] == "json":
                os.remove(os.path.join(self.disk_dir, "IAM-Accounts", e))

        # serialize the updated accounts
        for k in self.credentials:
            with open(os.path.join(self.disk_dir, "IAM-Accounts", k + ".json"), 'w') as f:
                json.dump(self.credentials[k], f, indent=4)

    def set_connections(self):
        self.generate_IAM_button.pressed.connect(self.on_generate_IAM)
        self.delete_button.pressed.connect(self.on_delete_IAM)
        self.generated_IAM_users.currentIndexChanged.connect(self.on_account_select)

    def on_generate_IAM(self):
        # generate the new IAM account
        # add it to the list of active accounts
        # fill it into the generated text fields
        new_IAM = {
            'access_id': 'test 1',
            'secret_id': 'test 2'
        }

        self.generate_IAM_access_key.setText("testkey1")
        self.generate_IAM_secret_access_key.setText("testkey2")

        new_credentials = "account-" + str(len(self.credentials) + 1)

        self.credentials[new_credentials] = new_IAM

        self.generated_IAM_users.addItem(new_credentials)
        self.generated_IAM_users.setCurrentIndex(len(self.credentials) - 1)

    def on_delete_IAM(self) -> None:
        current_credentials = self.current_credentials
        current_index = self.generated_IAM_users.currentIndex()
        self.generated_IAM_users.removeItem(current_index)
        self.credentials.pop(current_credentials, None)

        if len(self.generated_IAM_users) == 0:
            self.current_credentials = ""
            self.current_IAM_account_access_key.setText("")
            self.current_IAM_account_secret_key.setText("")
            return

        if current_index != 0:
            current_index -= 1

        self.current_credentials = self.generated_IAM_users.itemText(current_index)
        self.generated_IAM_users.setCurrentIndex(current_index)

    def on_account_select(self, i: int) -> None:
        if i == -1:
            self.current_credentials = ""
            self.delete_button.setEnabled(False)
            self.current_IAM_account_access_key.setText("")
            self.current_IAM_account_secret_key.setText("")
            self.current_IAM_account_access_key.setEnabled(False)
            self.current_IAM_account_secret_key.setEnabled(False)
            self.update()
            return

        self.current_credentials = self.generated_IAM_users.itemText(i)
        self.delete_button.setEnabled(True)
        self.current_IAM_account_access_key.setText(self.credentials[self.current_credentials]["access_id"])
        self.current_IAM_account_secret_key.setText(self.credentials[self.current_credentials]["secret_id"])
        self.current_IAM_account_access_key.setEnabled(True)
        self.current_IAM_account_secret_key.setEnabled(True)



