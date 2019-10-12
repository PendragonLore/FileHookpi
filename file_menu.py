# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtGui import QKeySequence


class FileMenu(QMenu):
    def __init__(self, main_window):
        super().__init__("&File")

        open_action = QAction(text="Open file", parent=self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(main_window.select_file)

        save_action = QAction(text="Save progress", parent=self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(main_window.save_file)

        load_action = QAction(text="Load progress", parent=self)
        load_action.triggered.connect(main_window.load_file)

        close_action = QAction(text="Close file", parent=self)
        close_action.triggered.connect(main_window.cleanup)

        for action in [open_action, save_action, load_action, close_action]:
            self.addAction(action)
