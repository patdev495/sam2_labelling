from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QPaintEvent, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle

from auto_labelling.models.track import Track
from auto_labelling.app.theme import icon as theme_icon


class TimelineWidget(QWidget):
    frame_changed = Signal(int)
    play_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame_count: int = 0
        self._current_frame: int = 0
        self._tracks: list[Track] = []
        self._playing: bool = False
        self._play_fps: int = 10
        self._reviewed_frames: set[int] = set()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._play_btn = QPushButton()
        self._play_btn.setIcon(theme_icon("play"))
        self._play_btn.setFixedSize(32, 32)
        self._play_btn.clicked.connect(self._on_play)
        layout.addWidget(self._play_btn)

        self._frame_label = QLabel("0 / 0")
        self._frame_label.setFixedWidth(80)
        layout.addWidget(self._frame_label)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(0)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.valueChanged.connect(self._on_slider)
        layout.addWidget(self._slider, 1)

    def set_frame_count(self, count: int):
        self._frame_count = max(0, count - 1)
        self._slider.setMaximum(self._frame_count)
        self._update_label()

    def set_current_frame(self, frame: int):
        self._current_frame = frame
        self._slider.blockSignals(True)
        self._slider.setValue(frame)
        self._slider.blockSignals(False)
        self._update_label()

    def set_tracks(self, tracks: list[Track]):
        self._tracks = tracks

    def mark_reviewed(self, frame: int):
        self._reviewed_frames.add(frame)

    def _on_slider(self, value: int):
        if value != self._current_frame:
            self._current_frame = value
            self._update_label()
            self.frame_changed.emit(value)

    def toggle_play(self):
        self._on_play()

    def _on_play(self):
        self._playing = not self._playing
        if self._playing:
            self._play_btn.setIcon(theme_icon("pause"))
            interval = int(1000 / self._play_fps)
            self._timer.start(interval)
        else:
            self._play_btn.setIcon(theme_icon("play"))
            self._timer.stop()
        self.play_toggled.emit(self._playing)

    def _tick(self):
        if self._current_frame < self._frame_count:
            self._current_frame += 1
            self._slider.setValue(self._current_frame)
            self.frame_changed.emit(self._current_frame)
        else:
            self._on_play()

    def _update_label(self):
        self._frame_label.setText(f"{self._current_frame} / {self._frame_count}")
