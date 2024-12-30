import datetime
import os
import sys
from PyQt5.QtGui import QIcon, QIntValidator, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QFileDialog, QHBoxLayout, QDialog, QMessageBox, 
                             QScrollArea, QComboBox, QLineEdit, QStyle, QStyleFactory)
from PyQt5.QtCore import Qt
from ftp_connection import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CCcam2OSCam Converter by mapi68")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(700, 700)
        self.setupUI()
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
        """)

    def setupUI(self):
        layout = QVBoxLayout(self)

        self.textEdit = QTextEdit("")
        layout.addWidget(self.textEdit)

        fileButton = QPushButton("Select CCcam.cfg")
        fileButton.clicked.connect(self.openFile)
        layout.addWidget(fileButton)

        filterLayout = QHBoxLayout()
        showLinesButton = QPushButton("Show only C-lines and N-lines")
        showLinesButton.clicked.connect(self.filterLines)
        filterLayout.addWidget(showLinesButton)
        layout.addLayout(filterLayout)

        inactivityLayout = QHBoxLayout()
        inactivityLabel1 = QLabel("Inactivity timeout C-lines (seconds):")
        self.inactivityEdit1 = QLineEdit()
        self.inactivityEdit1.setValidator(QIntValidator(-1, 9999))
        self.inactivityEdit1.setText("600")
        self.inactivityEdit1.setFixedWidth(50)
        inactivityLayout.addWidget(inactivityLabel1)
        inactivityLayout.addWidget(self.inactivityEdit1)

        inactivityLabel2 = QLabel("Inactivity timeout N-lines (seconds):")
        self.inactivityEdit2 = QLineEdit()
        self.inactivityEdit2.setValidator(QIntValidator(-1, 9999))
        self.inactivityEdit2.setText("-1")
        self.inactivityEdit2.setFixedWidth(50)
        inactivityLayout.addWidget(inactivityLabel2)
        inactivityLayout.addWidget(self.inactivityEdit2)
        layout.addLayout(inactivityLayout)

        groupLayout = QHBoxLayout()
        groupLabel1 = QLabel("C-lines group (1-64):")
        self.groupComboBox1 = QComboBox()
        self.groupComboBox1.addItems([str(i) for i in range(1, 65)])
        self.groupComboBox1.setCurrentText("1")
        groupLayout.addWidget(groupLabel1)
        groupLayout.addWidget(self.groupComboBox1)

        groupLabel2 = QLabel("N-lines group (1-64):")
        self.groupComboBox2 = QComboBox()
        self.groupComboBox2.addItems([str(i) for i in range(1, 65)])
        self.groupComboBox2.setCurrentText("1")
        groupLayout.addWidget(groupLabel2)
        groupLayout.addWidget(self.groupComboBox2)
        layout.addLayout(groupLayout)

        convertButton = QPushButton("Convert to oscam.server")
        convertButton.clicked.connect(self.convert)
        layout.addWidget(convertButton)

        viewButton = QPushButton("View oscam.server")
        viewButton.clicked.connect(self.viewContent)
        layout.addWidget(viewButton)

        ftpButton = QPushButton("FTP Connection Enigma2")
        ftpButton.clicked.connect(self.openWindowFTP)
        layout.addWidget(ftpButton)

        helpButton = QPushButton("Help")
        helpButton.clicked.connect(self.showHelp)
        layout.addWidget(helpButton)

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select CCcam.cfg", "", "File CCcam.cfg (*.cfg)", options=options
        )

        if fileName:
            with open(fileName, "r", encoding="utf-8") as file:
                cccam_cfg = file.read()
                self.textEdit.setText(cccam_cfg)
                self.filterLines()

    def filterLines(self):
        cccam_cfg = self.textEdit.toPlainText().splitlines()
        filtered_lines = [line for line in cccam_cfg if line.startswith(("C:", "N:"))]
        self.textEdit.setText("\n".join(filtered_lines))

    def convert(self):
        cccam_cfg = self.textEdit.toPlainText().splitlines()
        output = self.generate_header()

        for line in cccam_cfg:
            if line.strip():
                config = self.process_line(line)
                if config:
                    output += config

        if output:
            self.save_oscam_server(output)

    def generate_header(self):
        return f"# Created with CCcam2OSCam Converter\n\n\n[reader]\nlabel\t\t= DELETE ME\nprotocol\t\t= cccam\ndevice\t\t= dummy.com,8888\n"

    def process_line(self, line):
        parts = line.split()
        if len(parts) < 5:
            QMessageBox.warning(self, "Format Error", f"Line is incomplete: {line}")
            return None

        protocol, server, port, user, password = parts[:5]
        
        if protocol == "N:":
            return self.process_n_line(parts)
        elif protocol == "C:":
            return self.process_c_line(parts)
        else:
            return None

    def process_n_line(self, parts):
        server, port, user, password = parts[1:5]
        key = "".join(parts[5:20]).replace(" ", "")
        ident = ""
        caid = ""

        if "#" in key:
            ident = parts[20].replace(" ", "")
            caid = ident.split(":")[0]
            key = key.replace("#", "")

        config = f"\n[reader]\n"
        config += f"label\t\t= {user}@{server}:{port} {ident}\n"
        config += f"description\t\t= {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        config += f"protocol\t\t= newcamd\n"
        config += f"device\t\t= {server},{port}\n"
        config += f"key\t\t= {key}\n"
        config += f"user\t\t= {user}\n"
        config += f"password\t\t= {password}\n"
        config += f"inactivitytimeout\t\t= {self.inactivityEdit2.text()}\n"
        config += f"disableserverfilter\t= 1\n"
        config += f"connectoninit\t\t= 1\n"
        config += f"caid\t\t= {caid}\n"
        config += f"ident\t\t= {ident}\n"
        config += f"group\t\t= {self.groupComboBox2.currentText()}\n"
        config += f"audisabled\t\t= 1\n"

        return config

    def process_c_line(self, parts):
        server, port, user, password = parts[1:5]

        config = f"\n[reader]\n"
        config += f"label\t\t= {user}@{server}:{port}\n"
        config += f"description\t\t= {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        config += f"protocol\t\t= cccam\n"
        config += f"device\t\t= {server},{port}\n"
        config += f"user\t\t= {user}\n"
        config += f"password\t\t= {password}\n"
        config += f"inactivitytimeout\t\t= {self.inactivityEdit1.text()}\n"
        config += f"group\t\t= {self.groupComboBox1.currentText()}\n"
        config += f"cccversion\t\t= 2.3.2\n"
        config += f"audisabled\t\t= 1\n"

        return config

    def save_oscam_server(self, output):
        defaultFileName = "oscam.server"
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save oscam.server file", defaultFileName, "File oscam.server (*.server)"
        )

        if fileName:
            output = self.validateOscamServer(output)
            with open(fileName, "w", encoding="utf-8") as file:
                file.write(output)
            QMessageBox.information(self, "Success", f"File saved successfully: {fileName}")

    def validateOscamServer(self, content):
        lines = content.splitlines()
        return "\n".join(line.strip() for line in lines if not line.strip().endswith("="))

    def viewContent(self):
        executable_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.argv[0]))
        file_paths = [
            os.path.join(executable_dir, "oscam.server"),
            "oscam.server"
        ]

        found_file = next((path for path in file_paths if os.path.exists(path)), None)

        if found_file:
            with open(found_file, "r", encoding="utf-8") as file:
                content = file.read()
            if content:
                self.showContentDialog(content)
        else:
            QMessageBox.information(self, "Information", "oscam.server does not exist.")

    def showContentDialog(self, content):
        dialog = QDialog(self)
        dialog.setWindowTitle("View oscam.server")
        dialog.resize(500, 800)
        dialog.move(self.x() + self.width() + 10, self.y())

        layout = QVBoxLayout(dialog)
        scrollArea = QScrollArea(dialog)
        scrollArea.setWidgetResizable(True)
        contentLabel = QLabel(content)
        contentLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scrollArea.setWidget(contentLabel)
        layout.addWidget(scrollArea)

        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def openWindowFTP(self):
        self.finestraFTP = FTPConnectionWindow()
        self.finestraFTP.show()

    def showHelp(self):
        QMessageBox.information(self, "Help", "<html><body style='text-align: center;'><p><h2>Select CCcam.cfg or paste from clipboard<br></p>"
                           "<p><h2>Supported lines:<br>C-lines<br>Normal N-lines<br>Extended N-lines<br></p>"
                           "<p><h3>C-line example:</h3><i>C: host_name_ip port username password</i></p>"
                           "<p><h3>Normal N-line example:</h3><i>N: host_name_ip port username password des_key</i></p>"
                           "<p><h3>Extended N-line example:</h3><i>N: host_name_ip port usename password des_key # caid:ident</i><br></p>"
                           "<p><h3>When you export to oscam.server...</h3>...the first account created will be call <i>'DELETE ME'</i>.<br>"
                           "Please, upload the file to OSCam and delete the account <i>'DELETE ME'</i>:<br>"
                           "this will restore the right formatted standard of oscam.server.<br><br></p><p>CCcam2OSCam Converter by mapi68</p></body></html>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    