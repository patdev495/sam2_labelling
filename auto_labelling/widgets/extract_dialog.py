from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QProgressBar, QFileDialog, QLabel,
    QDialogButtonBox, QGroupBox, QMessageBox,
)

from auto_labelling.app.constants import DEFAULT_FRAME_SKIP
from auto_labelling.services.video_service import VideoService


class ExtractDialog(QDialog):
    extraction_complete = Signal(str)  # output directory path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extract Frames from Video")
        self.setMinimumWidth(500)
        self._video_path: str = ""
        self._output_dir: str = ""
        self._extracting: bool = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Video file
        video_group = QGroupBox("Video")
        video_form = QFormLayout(video_group)
        video_row = QHBoxLayout()
        self._video_edit = QLineEdit()
        self._video_edit.setReadOnly(True)
        video_row.addWidget(self._video_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_video)
        video_row.addWidget(browse_btn)
        video_form.addRow("Video file:", video_row)
        layout.addWidget(video_group)

        # Output
        output_group = QGroupBox("Output")
        output_form = QFormLayout(output_group)
        output_row = QHBoxLayout()
        self._output_edit = QLineEdit()
        self._output_edit.setReadOnly(True)
        output_row.addWidget(self._output_edit)
        browse_out_btn = QPushButton("Browse...")
        browse_out_btn.clicked.connect(self._browse_output)
        output_row.addWidget(browse_out_btn)
        output_form.addRow("Output folder:", output_row)
        layout.addWidget(output_group)

        # Options
        opt_group = QGroupBox("Options")
        opt_form = QFormLayout(opt_group)

        self._skip_spin = QSpinBox()
        self._skip_spin.setRange(1, 1000)
        self._skip_spin.setValue(DEFAULT_FRAME_SKIP)
        self._skip_spin.setToolTip("Extract every Nth frame (1 = extract all)")
        opt_form.addRow("Frame skip:", self._skip_spin)

        self._start_spin = QDoubleSpinBox()
        self._start_spin.setRange(0.0, 99999.0)
        self._start_spin.setValue(0.0)
        self._start_spin.setSuffix(" sec")
        opt_form.addRow("Start time:", self._start_spin)

        self._end_spin = QDoubleSpinBox()
        self._end_spin.setRange(0.0, 99999.0)
        self._end_spin.setValue(0.0)
        self._end_spin.setSuffix(" sec")
        self._end_spin.setSpecialValueText("End")
        opt_form.addRow("End time:", self._end_spin)

        layout.addWidget(opt_group)

        # Progress
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Buttons
        button_box = QDialogButtonBox()
        self._extract_btn = QPushButton("Extract")
        self._extract_btn.clicked.connect(self._extract)
        button_box.addButton(self._extract_btn, QDialogButtonBox.ButtonRole.ActionRole)
        cancel_btn = button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video",
            filter="Videos (*.mp4 *.avi *.mov *.mkv *.webm);;All files (*.*)",
        )
        if path:
            self._video_path = path
            self._video_edit.setText(path)
            name = Path(path).stem
            parent = str(Path(path).parent / name)
            self._output_edit.setText(parent)
            self._output_dir = parent
            self._update_video_info(path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self._output_dir = path
            self._output_edit.setText(path)

    def _update_video_info(self, path: str):
        try:
            info = VideoService.get_video_info(path)
            self._start_spin.setMaximum(info["duration_sec"])
            self._end_spin.setMaximum(info["duration_sec"])
        except Exception:
            pass

    def _extract(self):
        if not self._video_path:
            QMessageBox.warning(self, "Error", "Select a video file first.")
            return
        if not self._output_dir:
            QMessageBox.warning(self, "Error", "Select an output folder first.")
            return

        out = Path(self._output_dir)
        if out.exists() and list(out.iterdir()):
            reply = QMessageBox.question(
                self, "Folder not empty",
                "Output folder is not empty. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._extract_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        try:
            end_sec = self._end_spin.value()
            if end_sec == 0.0:
                end_sec = None

            frame_names = VideoService.extract_frames(
                video_path=self._video_path,
                output_dir=self._output_dir,
                frame_skip=self._skip_spin.value(),
                start_sec=self._start_spin.value(),
                end_sec=end_sec,
                progress_callback=lambda cur, total: self._progress.setValue(
                    int(cur / total * 100) if total > 0 else 0
                ),
            )
            self._progress.setValue(100)
            QMessageBox.information(
                self, "Done",
                f"Extracted {len(frame_names)} frames to:\n{self._output_dir}",
            )
            self.extraction_complete.emit(self._output_dir)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed:\n{e}")
        finally:
            self._extract_btn.setEnabled(True)
