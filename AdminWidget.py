import os
import json
import random

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

        """ 
        Stores all of the pre-existing active accounts into the credentials dict
        """
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

        self.generate_IAM_access_key = QLineEdit("")
        self.generate_IAM_access_key.setMinimumWidth(200)
        self.generate_IAM_access_key.setMaximumWidth(1000)

        self.generate_IAM_secret_access_key = QLineEdit("")
        self.generate_IAM_secret_access_key.setMinimumWidth(200)
        self.generate_IAM_secret_access_key.setMaximumWidth(1000)

        self.current_IAM_account_access_key = QLineEdit("")
        self.current_IAM_account_access_key.setMinimumWidth(200)
        self.current_IAM_account_access_key.setMaximumWidth(1000)

        self.current_IAM_account_secret_key = QLineEdit("")
        self.current_IAM_account_secret_key.setMinimumWidth(200)
        self.current_IAM_account_secret_key.setMaximumWidth(1000)

        self.list_label = QLabel("Active IAM Accounts: ")

        self.generated_IAM_users = QComboBox()
        self.generated_IAM_users.setMinimumWidth(100)
        """
        Fills the generated_IAM_users list with the items in the credentials dict
        """
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

        self.account_name_label = QLabel("Account Name:")
        self.account_name_field = QLineEdit("")
        account_name_layout = QHBoxLayout()
        account_name_layout.addWidget(self.account_name_label)
        account_name_layout.addWidget(self.account_name_field)
        account_name_widget = QWidget()
        account_name_widget.setLayout(account_name_layout)

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
        select_IAM_layout.addWidget(account_name_widget)
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
        """
        Disables the current and selected account features if there are no active accounts
        """
        if not self.current_credentials:
            self.delete_button.setEnabled(False)
            self.account_name_field.setEnabled(False)
            self.current_IAM_account_access_key.setEnabled(False)
            self.current_IAM_account_secret_key.setEnabled(False)
            self.update()

    def shutdown(self):
        """
        Called when the program is closed --> Saves the active accounts to respective .json
        """
        # remove the old files
        for e in os.listdir(os.path.join(self.disk_dir, "IAM-Accounts")):
            if e.split(".")[-1] == "json":
                os.remove(os.path.join(self.disk_dir, "IAM-Accounts", e))

        # serialize the updated accounts
        for k in self.credentials:
            with open(os.path.join(self.disk_dir, "IAM-Accounts", k + ".json"), 'w') as f:
                json.dump(self.credentials[k], f, indent=4)

    def set_connections(self):
        """
        Sets up all of the connections between the components of the AdminWidget
        """
        self.generate_IAM_button.pressed.connect(self.on_generate_IAM)
        self.delete_button.pressed.connect(self.on_delete_IAM)
        self.generated_IAM_users.currentIndexChanged.connect(self.on_account_select)
        self.account_name_field.returnPressed.connect(self.on_name_change)

    def on_generate_IAM(self):
        """
        Called when the Generate IAM button is pressed
        """
        new_IAM = {
            'access_id': 'test' + str(random.randint(10000, 99999)),
            'secret_id': 'test' + str(random.randint(10000, 99999))
        }

        new_credentials = "account-" + str(len(self.credentials) + 1)

        self.credentials[new_credentials] = new_IAM
        self.generate_IAM_access_key.setText(self.credentials[new_credentials]["access_id"])
        self.generate_IAM_secret_access_key.setText(self.credentials[new_credentials]["secret_id"])

        self.generated_IAM_users.addItem(new_credentials)
        self.generated_IAM_users.setCurrentIndex(len(self.credentials) - 1)

    def on_name_change(self) -> None:
        """
        Called when the name of an account is changed
        """
        nName = self.account_name_field.text()
        self.credentials[nName] = self.credentials[self.current_credentials]
        del self.credentials[self.current_credentials]
        self.current_credentials = nName
        self.generated_IAM_users.setItemText(self.generated_IAM_users.currentIndex(), nName)

    def on_delete_IAM(self) -> None:
        """
        Called when the delete button is pressed
        """
        current_credentials = self.current_credentials
        current_index = self.generated_IAM_users.currentIndex()
        self.generated_IAM_users.removeItem(current_index)
        self.credentials.pop(current_credentials, None)

        if len(self.generated_IAM_users) == 0:
            self.current_credentials = ""
            self.current_IAM_account_access_key.setText("")
            self.current_IAM_account_secret_key.setText("")
            self.generate_IAM_access_key.setText("")
            self.generate_IAM_secret_access_key.setText("")
            self.account_name_field.setText("")
            return

        if current_index != 0:
            current_index -= 1

        self.current_credentials = self.generated_IAM_users.itemText(current_index)
        self.generated_IAM_users.setCurrentIndex(current_index)

    def on_account_select(self, i: int) -> None:
        """
        Called when an account is selected from the list of the current accounts
        """
        if i == -1:
            self.current_credentials = ""
            self.delete_button.setEnabled(False)
            self.account_name_field.setText("")
            self.current_IAM_account_access_key.setText("")
            self.current_IAM_account_secret_key.setText("")
            self.current_IAM_account_access_key.setEnabled(False)
            self.current_IAM_account_secret_key.setEnabled(False)
            self.account_name_field.setEnabled(False)
            self.update()
            return

        self.current_credentials = self.generated_IAM_users.itemText(i)
        self.delete_button.setEnabled(True)
        self.account_name_field.setText(self.current_credentials)
        self.current_IAM_account_access_key.setText(self.credentials[self.current_credentials]["access_id"])
        self.current_IAM_account_secret_key.setText(self.credentials[self.current_credentials]["secret_id"])
        self.current_IAM_account_access_key.setEnabled(True)
        self.current_IAM_account_secret_key.setEnabled(True)
        self.account_name_field.setEnabled(True)



