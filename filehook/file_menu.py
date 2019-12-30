# -*- encoding: utf-8 -*-

from PySide2.QtWidgets import QMenu, QAction


class FileMenu(QMenu):
    ACTION_MAPPING = (
        ("Open File", "select_file"),
        ("Close file", "cleanup"),
    )

    def __init__(self, main_window):
        super().__init__("&File", main_window)

        for text, function_name in self.ACTION_MAPPING:
            action = QAction(text, self)
            action.triggered.connect(getattr(main_window, function_name))
            self.addAction(action)
