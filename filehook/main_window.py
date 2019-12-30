import os

from PySide2.QtWidgets import (
    QMainWindow, QSizePolicy, QWidget, QPlainTextEdit, QHBoxLayout, QPushButton, QVBoxLayout,
    QLineEdit, QApplication, QFileDialog, QMessageBox
)

from .file_menu import FileMenu

__all__ = [
    "MainWindow"
]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("main_window")
        self.setEnabled(True)
        self.resize(608, 248)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setAcceptDrops(True)
        self.setWindowTitle("FileHookPi")

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.horizontalLayout = QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.text_box = QPlainTextEdit(self.central_widget)
        self.text_box.setAcceptDrops(False)
        self.text_box.setReadOnly(True)
        self.text_box.setObjectName("text_box")

        self.horizontalLayout.addWidget(self.text_box)

        self.buttons_vertical_layout = QVBoxLayout()
        self.buttons_vertical_layout.setObjectName("buttons_vertical_layout")

        self.open_file_button = QPushButton(self.central_widget)
        self.open_file_button.setText("Open File")
        self.open_file_button.setObjectName("open_file_button")
        self.open_file_button.clicked.connect(self.select_file)

        self.buttons_vertical_layout.addWidget(self.open_file_button)

        self.line_counter = QLineEdit(self.central_widget)
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.line_counter.sizePolicy().hasHeightForWidth())
        self.line_counter.setSizePolicy(size_policy)
        self.line_counter.setAcceptDrops(False)
        self.line_counter.setReadOnly(True)
        self.line_counter.setObjectName("line_counter")

        self.buttons_vertical_layout.addWidget(self.line_counter)

        self.next_line_button = QPushButton(self.central_widget)
        self.next_line_button.setText("Next Line")
        self.next_line_button.setObjectName("next_line_button")
        self.next_line_button.clicked.connect(self.advance_line)

        self.buttons_vertical_layout.addWidget(self.next_line_button)

        self.horizontalLayout.addLayout(self.buttons_vertical_layout)

        self.menuBar().addMenu(FileMenu(self))

        self.setCentralWidget(self.central_widget)

        self.current_file = None
        self.line_count = 0

    def select_file(self, *, advance=True):
        path, *_ = QFileDialog.getOpenFileName(self, "Open File", filter="Text Files (*.txt)")

        if not path:
            return

        self.open_file(path, advance=advance)

    def open_file(self, path, *, advance=True):
        if self.current_file is not None:
            self.cleanup()

        self.current_file = open(path, "r", encoding="utf-8")
        self.setWindowFilePath(path)

        if advance:
            self.advance_line()

    def advance_line(self):
        if self.current_file is None:
            return

        try:
            line = self.current_file.readline()
        except Exception as exc:
            message_box = QMessageBox(
                parent=self, text=f"Failed to read:\n{type(exc).__name__}: {exc}", icon=QMessageBox.Critical
            )
            message_box.setInformativeText("Close the file?")
            message_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            message_box.setDefaultButton(QMessageBox.Yes)

            if message_box.exec_() == QMessageBox.Yes:
                self.cleanup()

            return

        if not line:
            return

        self.line_count += 1
        self.line_counter.setText(str(self.line_count))
        QApplication.clipboard().setText(line.rstrip("\n"))
        self.text_box.setPlainText(line + self.text_box.toPlainText())

    def cleanup(self):
        if self.current_file is not None:
            self.current_file.close()
            self.current_file = None

        self.text_box.clear()
        self.line_count = 0
        self.line_counter.clear()
        self.setWindowFilePath("")

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()

        if urls and os.path.isfile(urls[0].path()):
            event.accept()

    def dropEvent(self, event):
        self.open_file(event.mimeData().urls()[0].path())

    def closeEvent(self, event):
        self.cleanup()
        event.accept()
