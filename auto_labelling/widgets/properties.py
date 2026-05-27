from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox,
    QDoubleSpinBox, QLabel, QPushButton, QGroupBox,
)

from auto_labelling.models.annotation import Annotation, BBox
from auto_labelling.models.track import Track


class PropertiesPanel(QWidget):
    class_changed = Signal(Track, Annotation, int)
    box_changed = Signal(Track, Annotation, BBox)
    go_to_frame = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._annotation: Optional[Annotation] = None
        self._track: Optional[Track] = None
        self._classes: list[str] = ["person"]
        self._suppress_updates: bool = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel("<b>Properties</b>")
        layout.addWidget(title)

        # Class
        class_group = QGroupBox("Class")
        class_form = QFormLayout(class_group)
        self._class_combo = QComboBox()
        self._class_combo.currentIndexChanged.connect(self._on_class_changed)
        class_form.addRow("Class:", self._class_combo)
        layout.addWidget(class_group)

        # Box coords
        box_group = QGroupBox("Bounding Box")
        box_form = QFormLayout(box_group)

        self._x_spin = QDoubleSpinBox()
        self._x_spin.setRange(0.0, 1.0)
        self._x_spin.setDecimals(6)
        self._x_spin.setSingleStep(0.01)
        self._x_spin.valueChanged.connect(self._on_box_field_changed)
        box_form.addRow("X center:", self._x_spin)

        self._y_spin = QDoubleSpinBox()
        self._y_spin.setRange(0.0, 1.0)
        self._y_spin.setDecimals(6)
        self._y_spin.setSingleStep(0.01)
        self._y_spin.valueChanged.connect(self._on_box_field_changed)
        box_form.addRow("Y center:", self._y_spin)

        self._w_spin = QDoubleSpinBox()
        self._w_spin.setRange(0.0, 1.0)
        self._w_spin.setDecimals(6)
        self._w_spin.setSingleStep(0.01)
        self._w_spin.valueChanged.connect(self._on_box_field_changed)
        box_form.addRow("Width:", self._w_spin)

        self._h_spin = QDoubleSpinBox()
        self._h_spin.setRange(0.0, 1.0)
        self._h_spin.setDecimals(6)
        self._h_spin.setSingleStep(0.01)
        self._h_spin.valueChanged.connect(self._on_box_field_changed)
        box_form.addRow("Height:", self._h_spin)

        layout.addWidget(box_group)

        # Frame info
        info_group = QGroupBox("Frame")
        info_form = QFormLayout(info_group)
        self._frame_label = QLabel("-")
        info_form.addRow("Frame:", self._frame_label)
        self._go_btn = QPushButton("Go to frame")
        self._go_btn.clicked.connect(self._on_go_to_frame)
        info_form.addRow(self._go_btn)
        layout.addWidget(info_group)

        layout.addStretch()

        self.setEnabled(False)

    def set_classes(self, classes: list[str]):
        self._classes = classes
        self._class_combo.clear()
        self._class_combo.addItems(classes)

    def set_annotation(self, track: Optional[Track], annotation: Optional[Annotation]):
        self._suppress_updates = True
        self._track = track
        self._annotation = annotation

        if track and annotation:
            self.setEnabled(True)
            self._class_combo.setCurrentIndex(annotation.class_id)
            if annotation.bbox:
                self._x_spin.setValue(annotation.bbox.x)
                self._y_spin.setValue(annotation.bbox.y)
                self._w_spin.setValue(annotation.bbox.w)
                self._h_spin.setValue(annotation.bbox.h)
            self._frame_label.setText(str(annotation.frame_idx))
        else:
            self.setEnabled(False)
            self._class_combo.setCurrentIndex(-1)
            self._x_spin.setValue(0)
            self._y_spin.setValue(0)
            self._w_spin.setValue(0)
            self._h_spin.setValue(0)
            self._frame_label.setText("-")

        self._suppress_updates = False

    def _on_class_changed(self, idx: int):
        if self._suppress_updates or not self._track or not self._annotation:
            return
        self.class_changed.emit(self._track, self._annotation, idx)

    def _on_box_field_changed(self):
        if self._suppress_updates or not self._track or not self._annotation:
            return
        new_bbox = BBox(
            x=self._x_spin.value(),
            y=self._y_spin.value(),
            w=self._w_spin.value(),
            h=self._h_spin.value(),
        )
        self.box_changed.emit(self._track, self._annotation, new_bbox)

    def _on_go_to_frame(self):
        if self._annotation:
            self.go_to_frame.emit(self._annotation.frame_idx)
