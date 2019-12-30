import sys
from filehook import MainWindow

from PySide2.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
