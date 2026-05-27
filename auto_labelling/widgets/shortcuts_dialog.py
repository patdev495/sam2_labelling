from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView,
    QDialogButtonBox, QLabel, QKeySequenceEdit,
)

ACTION_LABELS = {
    "open_video": "Open Video",
    "extract_frames": "Extract Frames",
    "auto_label": "Auto Label",
    "save": "Export Labels",
    "undo": "Undo",
    "redo": "Redo",
    "next_frame": "Next Frame",
    "prev_frame": "Previous Frame",
    "play_pause": "Play / Pause",
    "delete_box": "Delete Box",
    "draw_box": "Draw Box",
}


class ShortcutSettingsDialog(QDialog):
    def __init__(self, shortcut_manager, parent=None):
        super().__init__(parent)
        self._shortcuts = shortcut_manager
        self._editing = False

        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._populate()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Double-click a shortcut to edit it."))

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Action", "Shortcut", "Reset"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(1, 140)
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(2, 80)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self._table)

        reset_all_btn = QPushButton("Reset All to Defaults")
        reset_all_btn.clicked.connect(self._on_reset_all)
        layout.addWidget(reset_all_btn)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _populate(self):
        shortcuts = self._shortcuts.all_shortcuts()
        # Show only action keys that exist in our labels
        actions = [k for k in ACTION_LABELS if k in shortcuts]
        self._table.setRowCount(len(actions))

        for row, action_key in enumerate(actions):
            label = ACTION_LABELS.get(action_key, action_key)
            keystr = shortcuts[action_key]

            # Action name
            name_item = QTableWidgetItem(label)
            name_item.setData(Qt.ItemDataRole.UserRole, action_key)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, name_item)

            # Shortcut
            shortcut_item = QTableWidgetItem(keystr)
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 1, shortcut_item)

            # Reset button
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(
                lambda checked=False, ak=action_key, r=row: self._reset_action(ak, r))
            self._table.setCellWidget(row, 2, reset_btn)

    def _on_cell_double_clicked(self, row: int, col: int):
        if col != 1:
            return

        action_key = self._table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        old_keystr = self._table.item(row, 1).text()

        editor = QKeySequenceEdit()
        editor.setKeySequence(QKeySequence(old_keystr))
        editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._table.setCellWidget(row, 1, editor)
        editor.setFocus()
        editor.editingFinished.connect(
            lambda r=row, ak=action_key, e=editor: self._finish_edit(r, ak, e))

    def _finish_edit(self, row: int, action_key: str, editor: QKeySequenceEdit):
        new_seq = editor.keySequence()
        new_keystr = new_seq.toString(QKeySequence.SequenceFormat.PortableText)

        if new_keystr:
            self._shortcuts.set(action_key, new_keystr)
            item = QTableWidgetItem(new_keystr)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setCellWidget(row, 1, None)
            self._table.setItem(row, 1, item)
        else:
            self._table.setCellWidget(row, 1, None)

    def _reset_action(self, action_key: str, row: int):
        self._shortcuts.reset(action_key)
        keystr = self._shortcuts.all_shortcuts()[action_key]
        item = QTableWidgetItem(keystr)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table.setItem(row, 1, item)

    def _on_reset_all(self):
        self._shortcuts.reset_all()
        self._populate()
