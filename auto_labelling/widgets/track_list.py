from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QLabel,
)

from auto_labelling.models.track import Track


class TrackListPanel(QWidget):
    track_selected = Signal(str)  # track_id
    track_deleted = Signal(str)
    track_visibility_changed = Signal(str, bool)
    add_track_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: list[Track] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        title = QLabel("<b>Tracks</b>")
        header.addWidget(title)
        header.addStretch()

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(24, 24)
        self._add_btn.setToolTip("Add new track (enter prompt mode)")
        self._add_btn.clicked.connect(self.add_track_requested.emit)
        header.addWidget(self._add_btn)

        layout.addLayout(header)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

    def set_tracks(self, tracks: list[Track]):
        self._tracks = tracks
        self._refresh()

    def _refresh(self):
        self._list.blockSignals(True)
        self._list.clear()
        for track in self._tracks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, track.id)
            item.setText(f"{track.name or f'Track {track.id}'}  [{track.annotation_count} boxes]")

            color = QColor(track.color)
            color.setAlpha(120)
            item.setForeground(QBrush(color))
            item.setToolTip(
                f"ID: {track.id}\n"
                f"Prompt: {track.prompt_type} @ frame {track.prompt_frame}\n"
                f"Annotations: {track.annotation_count}\n"
                f"Range: frames {track.frame_range[0]}-{track.frame_range[1]}"
            )
            self._list.addItem(item)

        self._list.blockSignals(False)

    def _on_selection_changed(self, current, previous):
        if current:
            track_id = current.data(Qt.ItemDataRole.UserRole)
            self.track_selected.emit(track_id)

    def select_track(self, track_id: str):
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == track_id:
                self._list.setCurrentItem(item)
                break
