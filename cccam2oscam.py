import datetime
import os
import sys

from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QHBoxLayout, QDialog, QMessageBox, QScrollArea, QComboBox, QLineEdit
from ftp_connection import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"CCcam2OSCam Converter by mapi68")

        # Get the full path of the "icon.ico" file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.ico")
        # Set the window icon
        self.setWindowIcon(QIcon(icon_path))

        self.resize(600, 600)
        self.setupUI()

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

        # Add text boxes for entering InactivityTimeout values
        inactivityLayout = QHBoxLayout()

        inactivityLabel1 = QLabel("Inactivity timeout C-lines (seconds):")
        self.inactivityEdit1 = QLineEdit()
        self.inactivityEdit1.setValidator(QIntValidator(-1, 9999))  # Set validation for numbers from -1 to 9999
        self.inactivityEdit1.setText("600")  # Default value "600"
        self.inactivityEdit1.setFixedWidth(50)  # Set fixed width for the input box
        inactivityLayout.addWidget(inactivityLabel1)
        inactivityLayout.addWidget(self.inactivityEdit1)

        inactivityLabel2 = QLabel("Inactivity timeout N-lines (seconds):")
        self.inactivityEdit2 = QLineEdit()
        self.inactivityEdit2.setValidator(QIntValidator(-1, 9999))  # Set validation for numbers from -1 to 9999
        self.inactivityEdit2.setText("-1")  # Default value "-1"
        self.inactivityEdit2.setFixedWidth(50)  # Set fixed width for the input box
        inactivityLayout.addWidget(inactivityLabel2)
        inactivityLayout.addWidget(self.inactivityEdit2)

        layout.addLayout(inactivityLayout)

        # Add dropdown menus for selecting groups
        groupLayout = QHBoxLayout()
        groupLabel1 = QLabel("C-lines group (1-64):")
        self.groupComboBox1 = QComboBox()
        self.groupComboBox1.addItems([str(i) for i in range(1, 65)])  # Numbering from 1 to 64
        self.groupComboBox1.setCurrentText("1")  # Default value "1"
        groupLayout.addWidget(groupLabel1)
        groupLayout.addWidget(self.groupComboBox1)

        groupLabel2 = QLabel("N-lines group (1-64):")
        self.groupComboBox2 = QComboBox()
        self.groupComboBox2.addItems([str(i) for i in range(1, 65)])  # Numbering from 1 to 64
        self.groupComboBox2.setCurrentText("1")  # Default value "1"
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
        filterText = "Show only C-lines and N-lines"
        cccam_cfg = self.textEdit.toPlainText().splitlines()

        filtered_lines = []

        for line in cccam_cfg:
            if line.startswith("C:") or line.startswith("N:"):
                filtered_lines.append(line)

        self.textEdit.setText("\n".join(filtered_lines))

    def convert(self):
        cccam_cfg = self.textEdit.toPlainText().splitlines()

        output = f"# Created with CCcam2OSCam Converter\n\n\n \
            [reader]\nlabel\t\t= DELETE\nprotocol\t\t= cccam\ndevice\t\t= dummy.com\n"

        current_reader = ""
        ignore_lines = False

        for line in cccam_cfg:
            if line.strip():
                if line.startswith("#"):
                    ignore_lines = False
                elif line.startswith("C: ") or line.startswith("N: "):
                    current_reader = line
                    ignore_lines = False
                elif not ignore_lines:
                    current_reader += line

                parts = current_reader.split()
                if len(parts) < 5:
                    QMessageBox.warning(self, "Format Error", "One or more lines are incomplete.")
                    return
                OPROTOCOL = parts[0]
                OSERVER = parts[1]
                OPORT = parts[2]
                OUSER = parts[3]
                OPASS = parts[4]

                config = ""

                if OPROTOCOL == "N:":
                    OKEY = "".join(parts[5:20]).replace(" ", "")
                    if "#" in OKEY:
                        OIDENT = parts[20].replace(" ", "")
                        OCAID = OIDENT.split(":")[0]
                        OKEY = OKEY.replace("#", "")
                    else:
                        OIDENT = ""
                        OCAID = ""

                    config += "\n[reader]\n"
                    config += f"label\t\t= {OUSER}@{OSERVER}:{OPORT} {OIDENT}\n"
                    config += f"description\t= {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    config += f"protocol\t\t= newcamd\n"
                    config += f"device\t\t= {OSERVER},{OPORT}\n"
                    config += f"key\t\t= {OKEY}\n"
                    config += f"user\t\t= {OUSER}\n"
                    config += f"password\t\t= {OPASS}\n"
                    config += f"inactivitytimeout\t= {self.inactivityEdit2.text()}\n"  # Use the value entered in the text box
                    config += f"disableserverfilter\t= 1\n"
                    config += f"connectoninit\t= 1\n"
                    config += f"caid\t\t= {OCAID}\n"
                    config += f"ident\t\t= {OIDENT}\n"
                    config += f"group\t\t= {self.groupComboBox2.currentText()}\n"  # Use the selected value from the drop-down menu
                    config += f"audisabled\t= 1\n"
                elif OPROTOCOL == "C:":
                    config += "\n[reader]\n"
                    config += f"label\t\t= {OUSER}@{OSERVER}:{OPORT}\n"
                    config += f"description\t= {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    config += f"protocol\t\t= cccam\n"
                    config += f"device\t\t= {OSERVER},{OPORT}\n"
                    config += f"user\t\t= {OUSER}\n"
                    config += f"password\t\t= {OPASS}\n"
                    config += f"inactivitytimeout\t= {self.inactivityEdit1.text()}\n"  # Use the value entered in the text box
                    config += f"group\t\t= {self.groupComboBox1.currentText()}\n"  # Use the selected value from the drop-down menu
                    config += f"cccversion\t= 2.3.2\n"
                    config += f"audisabled\t= 1\n"

                output += config

        if output:
            defaultFileName = "oscam.server"
            fileName, _ = QFileDialog.getSaveFileName(
                self, "Save oscam.server file", defaultFileName, "File oscam.server (*.server)"
            )

            if fileName:
                output = self.validateOscamServer(output)
                with open(fileName, "w", encoding="utf-8") as file:
                    file.write(output)

    def validateOscamServer(self, content):
        lines = content.splitlines()
        valid_lines = []

        for line in lines:
            line = line.strip()
            if line.endswith("="):
                continue
            valid_lines.append(line)

        return "\n".join(valid_lines)

    def viewContent(self):
            executable_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.argv[0]))
            file_paths = [
                os.path.join(executable_dir, "oscam.server"),  # Path in the executable folder
                "oscam.server"  # Path in the same folder as the current Python file
            ]

            found_file = None
            for file_path in file_paths:
                if os.path.exists(file_path):
                    found_file = file_path
                    break

            if found_file:
                with open(found_file, "r", encoding="utf-8") as file:
                    content = file.read()
                if content:
                    dialog = QDialog(self)
                    dialog.setWindowTitle("View oscam.server")
                    dialog.resize(450, 800)
                    dialog.move(self.x() - 455, self.y() - 100)

                    layout = QVBoxLayout(dialog)

                    scrollArea = QScrollArea(dialog)
                    scrollArea.setWidgetResizable(True)

                    contentLabel = QLabel(content)
                    scrollArea.setWidget(contentLabel)

                    layout.addWidget(scrollArea)

                    dialog.exec()
            else:
                QMessageBox.information(self, "Information", "oscam.server does not exist.")

    def openWindowFTP(self):
        self.finestraFTP = FTPConnectionWindow()
        self.finestraFTP.show()

    def showHelp(self):
        QMessageBox.information(self, "Help", "<html><body style='text-align: center;'><p><h2>Select CCcam.cfg or paste from clipboard<br></p>"
                           "<p><h2>Supported lines:<br>C-lines<br>Normal N-lines<br>Extended N-lines<br></p>"
                           "<p><h3>C-line example:</h3><i>C: host_name_ip port username password</i></p>"
                           "<p><h3>Normal N-line example:</h3><i>N: host_name_ip port username password des_key</i></p>"
                           "<p><h3>Extended N-line example:</h3><i>N: host_name_ip port usename password des_key # caid:ident</i><br></p>"
                           "<p><h3>When you export to oscam.server...</h3>...the first account created will be <i>DELETE</i>.<br>"
                           "Please, upload the file to OSCam and delete the account <i>DELETE</i>:<br>"
                           "this will restore the right formatted standard of oscam.server.<br><br></p><p>CCcam2OSCam Converter by mapi68</p></body></html>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
