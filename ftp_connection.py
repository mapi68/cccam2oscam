import configparser
import ftplib
import os
import sys
import inspect
from datetime import datetime
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                             QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, 
                             QHBoxLayout, QDialog, QGridLayout, QMessageBox, 
                             QStyleFactory)
from PyQt5.QtCore import Qt

class OscamServerWindow(QDialog):
    def __init__(self, file_data):
        super().__init__()
        self.setWindowTitle("oscam.server Viewer")
        self.resize(500, 650)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.text_edit.setPlainText("\n".join(file_data))

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #646464;
                border-radius: 3px;
                padding: 2px;
            }
        """)

class FTPConnectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTP Connection Enigma2")

        current_file = inspect.getfile(inspect.currentframe())
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.resize(380, 500)

        self.default_host = ""
        self.default_username = "root"
        self.default_password = ""
        self.default_directory = "/etc/tuxbox/config/"

        self.setup_ui()
        self.load_configuration()

        self.setStyle(QStyleFactory.create('Fusion'))
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #646464;
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QTextEdit, QLineEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #646464;
                border-radius: 3px;
                padding: 2px;
            }
            QLabel {
                color: #d4d4d4;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        form_layout = QGridLayout()

        host_label = QLabel("IP Address or Hostname:")
        self.host_input = QLineEdit(self.default_host)
        form_layout.addWidget(host_label, 0, 0)
        form_layout.addWidget(self.host_input, 0, 1)

        username_label = QLabel("Username:")
        self.username_input = QLineEdit(self.default_username)
        form_layout.addWidget(username_label, 1, 0)
        form_layout.addWidget(self.username_input, 1, 1)

        password_label = QLabel("Password:")
        self.password_input = QLineEdit(self.default_password)
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label, 2, 0)
        form_layout.addWidget(self.password_input, 2, 1)

        directory_label = QLabel("Directory:")
        self.directory_dropdown = QComboBox()
        directories = [
            "/etc/tuxbox/config/",
            "/etc/tuxbox/config/oscam/",
            "/etc/tuxbox/config/oscam-emu/",
            "/hdd/oscam/",
            "/home/oscam/",
            "/usr/local/etc/",
            "/usr/local/oscam/config/",
            "/usr/share/oscam/config/",
            "/var/tuxbox/config/",
            "/var/etc/",
            "/var/oscam/config/"
        ]
        self.directory_dropdown.addItems(directories)
        self.directory_dropdown.setCurrentText(self.default_directory)
        form_layout.addWidget(directory_label, 3, 0)
        form_layout.addWidget(self.directory_dropdown, 3, 1)

        layout.addLayout(form_layout)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(100)
        layout.addWidget(self.console)

        button_layout1 = QHBoxLayout()
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(self.test_connection)
        button_layout1.addWidget(test_button)

        upload_button = QPushButton("Upload oscam.server")
        upload_button.clicked.connect(self.upload_oscam_server)
        button_layout1.addWidget(upload_button)
        layout.addLayout(button_layout1)

        button_layout2 = QHBoxLayout()
        view_button = QPushButton("View Remote oscam.server")
        view_button.clicked.connect(self.view_oscam_server)
        button_layout2.addWidget(view_button)

        download_button = QPushButton("Download oscam.server")
        download_button.clicked.connect(self.download_oscam_server)
        button_layout2.addWidget(download_button)
        layout.addLayout(button_layout2)

        button_layout3 = QHBoxLayout()
        backup_button = QPushButton("Backup Configuration")
        backup_button.clicked.connect(self.backup_configuration)
        button_layout3.addWidget(backup_button)

        restart_button = QPushButton("Restart Oscam")
        restart_button.clicked.connect(self.restart_oscam)
        button_layout3.addWidget(restart_button)
        layout.addLayout(button_layout3)

        button_layout4 = QHBoxLayout()
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        button_layout4.addWidget(save_button)
        layout.addLayout(button_layout4)

    def load_configuration(self):
        config = configparser.ConfigParser()
        try:
            config.read("cccam2oscam.conf")
            self.host_input.setText(config.get("FTP", "host"))
            self.username_input.setText(config.get("FTP", "username"))
            self.password_input.setText(config.get("FTP", "password"))
            self.directory_dropdown.setCurrentText(config.get("FTP", "directory"))
        except configparser.Error:
            pass

    def save_configuration(self):
        config = configparser.ConfigParser()
        config["FTP"] = {
            "host": self.host_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "directory": self.directory_dropdown.currentText()
        }
        with open("cccam2oscam.conf", "w") as config_file:
            config.write(config_file)
        self.console.append("Configuration saved successfully.")

    def test_connection(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                response = ftp.getwelcome()
                ftp.quit()
                self.console.append("Connection successful!")
                self.console.append(response)
            except ftplib.all_errors as e:
                self.console.append("Error connecting to FTP: " + str(e))

    def upload_oscam_server(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            directory = self.directory_dropdown.currentText()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)
                
                try:
                    backup_name = f"oscam.server.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    ftp.rename("oscam.server", backup_name)
                    self.console.append(f"Created backup of remote file as {backup_name}")
                except ftplib.error_perm:
                    self.console.append("No existing remote file to backup")

                with open("oscam.server", "rb") as file:
                    ftp.storbinary("STOR oscam.server", file)
                ftp.quit()
                self.console.append(f"File 'oscam.server' uploaded successfully to {directory}")
            except ftplib.all_errors as e:
                self.console.append("Error uploading file: " + str(e))

    def download_oscam_server(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            directory = self.directory_dropdown.currentText()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)

                if os.path.exists("oscam.server"):
                    backup_name = f"oscam.server.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.rename("oscam.server", backup_name)
                    self.console.append(f"Created backup of local file as {backup_name}")

                with open("oscam.server", "wb") as file:
                    ftp.retrbinary("RETR oscam.server", file.write)

                ftp.quit()
                self.console.append("File 'oscam.server' downloaded successfully")
            except ftplib.all_errors as e:
                self.console.append("Error downloading file: " + str(e))

    def view_oscam_server(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            directory = self.directory_dropdown.currentText()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)
                file_data = []
                ftp.retrlines('RETR oscam.server', file_data.append)
                ftp.quit()

                oscam_server_window = OscamServerWindow(file_data)
                oscam_server_window.exec_()

                self.console.append(f"File 'oscam.server' viewed successfully from {directory}")
            except ftplib.all_errors as e:
                self.console.append("Error viewing file: " + str(e))

    def backup_configuration(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            username = self.username_input.text()
            password = self.password_input.text()
            directory = self.directory_dropdown.currentText()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)

                backup_dir = "oscam_backups"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_subdir = os.path.join(backup_dir, f"backup_{timestamp}")
                os.makedirs(backup_subdir)

                file_list = []
                ftp.retrlines('LIST', file_list.append)

                files_to_backup = []
                for file_info in file_list:
                    if file_info.startswith('d'):
                        continue
                    filename = file_info.split()[-1]
                    files_to_backup.append(filename)

                for filename in files_to_backup:
                    try:
                        with open(os.path.join(backup_subdir, filename), "wb") as local_file:
                            ftp.retrbinary(f"RETR {filename}", local_file.write)
                            self.console.append(f"Backed up {filename}")
                    except ftplib.error_perm as e:
                        self.console.append(f"Error backing up {filename}: {str(e)}")

                ftp.quit()
                self.console.append(f"Backup completed successfully in {backup_subdir}")
                self.console.append(f"Total files backed up: {len(files_to_backup)}")

            except ftplib.all_errors as e:
                self.console.append(f"FTP Error during backup: {str(e)}")
            except Exception as e:
                self.console.append(f"Error during backup: {str(e)}")

    def restart_oscam(self):
        if self.check_ftp_configuration():
            host = self.host_input.text()
            directory = self.directory_dropdown.currentText()

            try:
                ftp = ftplib.FTP(host)
                ftp.login(self.username_input.text(), self.password_input.text())
                ftp.cwd(directory)

                conf_data = []
                ftp.retrlines('RETR oscam.conf', conf_data.append)
                ftp.quit()

                http_port = None
                for line in conf_data:
                    if 'httpport' in line:
                        try:
                            http_port = line.split()[2]
                            break
                        except IndexError:
                            continue

                if not http_port:
                    self.console.append("Error: Could not find httpport in oscam.conf")
                    return
                restart_url = f"http://{host}:{http_port}/shutdown.html?action=Restart"
                try:
                    response = requests.get(restart_url, timeout=5)
                    if response.status_code == 200:
                        self.console.append("Oscam restart command sent successfully")
                    else:
                        self.console.append(f"Error restarting Oscam (Status code: {response.status_code})")
                except requests.exceptions.RequestException as e:
                    self.console.append(f"Error sending restart command: {str(e)}")

            except ftplib.all_errors as e:
                self.console.append(f"FTP Error: {str(e)}")
            except Exception as e:
                self.console.append(f"Error: {str(e)}")

    def check_ftp_configuration(self):
        if (
            self.host_input.text() == "" or
            self.username_input.text() == "" or
            self.password_input.text() == ""
        ):
            QMessageBox.warning(
                self,
                "Warning",
                "FTP configuration is missing. Please enter all FTP details."
            )
            return False
        return True

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_success_message(self, message):
        QMessageBox.information(self, "Success", message)

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    window = FTPConnectionWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()