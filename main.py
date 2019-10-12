# -*- coding: utf-8 -*-

import os
import re
import struct
import sys
import uuid

from PySide2.QtCore import QFile, QFileDevice, QTextStream, Qt, QByteArray
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QFileDialog, QTextEdit
from PySide2.QtWidgets import QMainWindow, QMessageBox

from file_menu import FileMenu

WINDOW_TITLE = "FileHookπ"


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(WINDOW_TITLE)

        self.file = None
        self.stream = None

        self.blue_sky_mode = QCheckBox("Blue sky mode")
        # keep this for saving
        self.blue_sky_text = None

        self.window_on_top_button = QCheckBox("Leave window on top")
        self.window_on_top_button.clicked.connect(self.window_on_top)

        text_button = QPushButton("Next line")
        text_button.clicked.connect(self.advance_line)

        self.menuBar().addMenu(FileMenu(self))

        self.text_line = QTextEdit()
        self.text_line.setReadOnly(True)

        self.widget = QWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.blue_sky_mode)
        layout.addWidget(self.window_on_top_button)
        layout.addWidget(text_button)
        layout.addWidget(self.text_line)

        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setAcceptDrops(True)

    SAVE_STRUCT = struct.Struct(">q")

    def window_on_top(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.window_on_top_button.isChecked())
        self.show()

    def dragEnterEvent(self, event):
        if event.mimeData().urls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # this allows for other type of files to be opened
        # but I don't really care
        path = event.mimeData().urls().pop(0).path()

        self._set_file(path)

    def save_file(self):
        if self.file is None or self.stream is None:
            return QMessageBox.warning(self, "Cannot save file", "No file currently open.")

        saves_folder = os.path.expanduser("~/FileHookSaves")
        if not os.path.exists(saves_folder):
            try:
                os.mkdir(saves_folder)
            except OSError as e:
                return QMessageBox.critical(self, "Failed to create saves directory", str(e))

        file_name = f"{saves_folder}/filehook_{uuid.uuid4().hex}.save"

        if os.path.exists(file_name):
            return QMessageBox.critical(self, "Cannot save file", f"File {os.path.abspath(file_name)} already exists.")

        f = QFile(file_name)
        f.open(QFileDevice.WriteOnly)
        try:
            # hack so when it's loaded it's actually on the current line instead of the next
            # also avoids negative seeking lol
            text = self.blue_sky_text if self.blue_sky_text is not None else self.text_line.toPlainText()
            last_pos = max(0, self.stream.pos() - (len(text.encode()) + 1))

            if self.blue_sky_text:
                # I don't get why this makes it work
                # but it does so :'
                last_pos -= 1

            f.write(QByteArray(self.SAVE_STRUCT.pack(last_pos)))
            f.write(QByteArray(b"\x00"))
            f.write(QByteArray(self.file.fileName().encode()))
        except Exception as e:
            return QMessageBox.critical(self, "Failed to save", str(e))
        finally:
            f.close()

        QMessageBox.information(self, "Succesfully saved", f"Saved at {file_name}")

    def load_file(self):
        dialog = QFileDialog(filter="TextHook save (*.save)")
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_():
            file = dialog.selectedFiles().pop(0)

            try:
                with open(file, "rb") as f:
                    size = self.SAVE_STRUCT.unpack(f.read(self.SAVE_STRUCT.size))[0]

                    assert f.read(1) == b"\x00"

                    path = f.read().decode()
            except (struct.error, AssertionError, IndexError, UnicodeError):
                return QMessageBox.critical(self, "Failed to load progress", "Invalid file structure")

            self.cleanup()
            self._set_file(path, seek=size)

    def advance_line(self):
        self.text_line.clear()

        if self.stream is None or self.file is None or self.stream.atEnd():
            return

        clip = QApplication.clipboard()
        line = self.stream.readLine()

        if self.blue_sky_mode.isChecked():
            self.blue_sky_text = line
            line = self.clean_text(line)
        else:
            self.blue_sky_text = None

        clip.setText(line)

        self.text_line.append(line)

    @staticmethod
    def clean_text(line):
        cleaned = re.sub(
            r"\[%([pe])\]|\[(margin|color|evaluate expr).+?(?=\])\]|\[(ruby-base|center)\]|\[ruby-text-start\]"
            r".*\[ruby-text-end\]",
            "", line
        ).replace("③⑤", "-").replace("[...]", "…")

        return re.sub(r"\[name\](.+)\[line\]", r"\1: ", cleaned)

    def _set_file(self, path, *, seek=None):
        self.file = file = QFile(path)
        file.open(QFileDevice.ReadOnly | QFileDevice.Text)
        self.stream = QTextStream(file)

        if seek:
            self.stream.seek(seek)

        self.setWindowFilePath(path)
        self.setWindowTitle(f"{WINDOW_TITLE} - {path}")

        self.advance_line()

    def cleanup(self):
        if self.file is not None and self.stream is not None:
            self.text_line.clear()
            self.stream.flush()
            self.file.close()

            self.file = None
            self.stream = None

            self.setWindowTitle(WINDOW_TITLE)
            self.setWindowFilePath("")

    def select_file(self):
        dialog = QFileDialog(filter="Plain text (*.txt)")
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_():
            self.cleanup()

            path = dialog.selectedFiles().pop(0)

            self._set_file(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
