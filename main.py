import sys

from PySide2.QtWidgets import QApplication

from filehook import MainWindow

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
