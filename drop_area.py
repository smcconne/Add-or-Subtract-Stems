# drop_area.py
#
# Drop area widget

import os
from PyQt5 import QtWidgets, QtCore
from audio_io import ACCEPT_EXTS


class DropArea(QtWidgets.QLabel):
    files_changed = QtCore.pyqtSignal()

    def __init__(self, text, allow_multiple, parent=None):
        super().__init__(text, parent)
        self.default_text = text
        self.allow_multiple = allow_multiple
        self.paths = []

        self.setObjectName("drop")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        self.setLineWidth(2)
        self.setMinimumHeight(160)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(ACCEPT_EXTS) for u in urls):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        files = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        picked = [f for f in files if f.lower().endswith(ACCEPT_EXTS)]
        if not picked:
            event.ignore()
            return

        if self.allow_multiple:
            existing = set(self.paths)
            self.paths.extend([f for f in picked if f not in existing])
        else:
            self.paths = [picked[-1]]

        self._update_label()
        self.files_changed.emit()
        event.acceptProposedAction()

    def clear_files(self):
        self.paths = []
        self.setText(self.default_text)
        self.files_changed.emit()

    def _update_label(self):
        if not self.paths:
            self.setText(self.default_text)
        else:
            if self.allow_multiple:
                lines = ["Loaded files:"] + [os.path.basename(p) for p in self.paths]
                self.setText("\n".join(lines))
            else:
                self.setText("Loaded:\n" + os.path.basename(self.paths[-1]))
