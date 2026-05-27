from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QToolBar, QFileDialog,
    QSplitter, QMessageBox, QWidget, QVBoxLayout,
    QProgressBar, QLabel,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QPixmap, QImage

from auto_labelling.app.constants import (
    APP_NAME, APP_VERSION, DEFAULT_CLASSES,
    MASK_CACHE_DIR, SUPPORTED_IMAGE_EXTS,
)
from auto_labelling.models.project import ProjectState
from auto_labelling.models.track import Track
from auto_labelling.models.annotation import Annotation, BBox
from auto_labelling.services.sam_service import SAM2Service
from auto_labelling.services.export_service import ExportService
from auto_labelling.utils.commands import (
    CommandHistory, AddBoxCommand, DeleteBoxCommand,
    MoveBoxCommand, ResizeBoxCommand, ChangeClassCommand,
)
from auto_labelling.utils.shortcuts import ShortcutManager
from auto_labelling.utils.session import SessionManager
from auto_labelling.widgets.canvas import CanvasWidget, CanvasMode
from auto_labelling.widgets.timeline import TimelineWidget
from auto_labelling.widgets.track_list import TrackListPanel
from auto_labelling.widgets.properties import PropertiesPanel
from auto_labelling.widgets.extract_dialog import ExtractDialog
from auto_labelling.widgets.shortcuts_dialog import ShortcutSettingsDialog
from auto_labelling.app.theme import icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(1280, 800))

        self._project = ProjectState()
        self._history = CommandHistory()
        self._sam = SAM2Service()
        self._shortcuts = ShortcutManager()
        self._session = SessionManager()

        self._prompt_mode: str = "click"

        self._setup_actions()
        self._setup_ui()
        self._setup_statusbar()
        self._connect_signals()
        self._restore_session()

    # ---- UI Setup ----

    def _setup_actions(self):
        sc = self._shortcuts

        self.action_open_folder = self._make_action("Open Folder", "open_video", "folder")
        self.action_extract_frames = self._make_action("Extract Frames", "extract_frames", "extract")
        self.action_auto_label = self._make_action("Auto Label", "auto_label", "auto_label")
        self.action_auto_label.setEnabled(False)
        self.action_export = self._make_action("Export Labels", "save", "export")
        self.action_export.setEnabled(False)

        self.action_undo = self._make_action("Undo", "undo", "undo")
        self.action_undo.setEnabled(False)
        self.action_redo = self._make_action("Redo", "redo", "redo")
        self.action_redo.setEnabled(False)

        self.action_toggle_masks = QAction(icon("mask"), "Show Masks", self)
        self.action_toggle_masks.setCheckable(True)
        self.action_toggle_masks.setChecked(False)

        # Frame navigation
        self.action_next_frame = self._make_action("Next Frame", "next_frame", "next")
        self.action_prev_frame = self._make_action("Prev Frame", "prev_frame", "prev")
        self.action_play_pause = self._make_action("Play/Pause", "play_pause", "play")

        # Box editing
        self.action_delete_box = self._make_action("Delete Box", "delete_box", "trash")
        self.action_draw_box = self._make_action("Draw Box", "draw_box", "edit")

        self.action_shortcuts = QAction(icon("settings"), "Shortcuts...", self)
        self.action_quit = QAction("Quit", self)
        self.action_quit.setShortcut(QKeySequence.Quit)

    def _make_action(self, text: str, shortcut_key: str, icon_key: str = "") -> QAction:
        action = QAction(icon(icon_key), text, self) if icon_key else QAction(text, self)
        seq = self._shortcuts.get(shortcut_key)
        if seq:
            action.setShortcut(seq)
        self.addAction(action)
        return action

    def _refresh_all_shortcuts(self):
        self.action_open_folder.setShortcut(self._shortcuts.get("open_video"))
        self.action_extract_frames.setShortcut(self._shortcuts.get("extract_frames"))
        self.action_auto_label.setShortcut(self._shortcuts.get("auto_label"))
        self.action_export.setShortcut(self._shortcuts.get("save"))
        self.action_undo.setShortcut(self._shortcuts.get("undo"))
        self.action_redo.setShortcut(self._shortcuts.get("redo"))
        self.action_next_frame.setShortcut(self._shortcuts.get("next_frame"))
        self.action_prev_frame.setShortcut(self._shortcuts.get("prev_frame"))
        self.action_play_pause.setShortcut(self._shortcuts.get("play_pause"))
        self.action_delete_box.setShortcut(self._shortcuts.get("delete_box"))
        self.action_draw_box.setShortcut(self._shortcuts.get("draw_box"))

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(2, 2, 2, 2)

        # Toolbar
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addAction(self.action_open_folder)
        toolbar.addAction(self.action_extract_frames)
        toolbar.addSeparator()
        toolbar.addAction(self.action_auto_label)
        toolbar.addAction(self.action_export)
        toolbar.addSeparator()
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.action_shortcuts)

        self._mode_label = QLabel("  Mode: View  ")
        toolbar.addWidget(self._mode_label)
        toolbar.addAction(self.action_toggle_masks)
        self.addToolBar(toolbar)

        # Prompt toolbar
        prompt_toolbar = QToolBar("Prompt")
        prompt_toolbar.setMovable(False)
        prompt_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.action_prompt_click = QAction(icon("crosshair"), "Click Prompt", self)
        self.action_prompt_click.setCheckable(True)
        self.action_prompt_box = QAction(icon("box_select"), "Box Prompt", self)
        self.action_prompt_box.setCheckable(True)
        self.action_edit_mode = QAction(icon("edit"), "Edit Mode", self)
        self.action_edit_mode.setCheckable(True)
        self.action_edit_mode.setChecked(True)
        prompt_toolbar.addAction(self.action_prompt_click)
        prompt_toolbar.addAction(self.action_prompt_box)
        prompt_toolbar.addSeparator()
        prompt_toolbar.addAction(self.action_edit_mode)
        self.addToolBar(prompt_toolbar)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._track_list = TrackListPanel()
        self._track_list.setMinimumWidth(180)
        self._track_list.setMaximumWidth(300)
        splitter.addWidget(self._track_list)

        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self._canvas = CanvasWidget()
        canvas_layout.addWidget(self._canvas)

        self._timeline = TimelineWidget()
        self._timeline.setFixedHeight(50)
        canvas_layout.addWidget(self._timeline)

        splitter.addWidget(canvas_container)

        self._properties = PropertiesPanel()
        self._properties.setMinimumWidth(200)
        self._properties.setMaximumWidth(300)
        splitter.addWidget(self._properties)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        root.addWidget(splitter)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._status_label = QLabel("Ready")
        self._frame_label = QLabel("")
        self._track_label = QLabel("")

        self.status_bar.addWidget(self._status_label, 1)
        self.status_bar.addPermanentWidget(self._track_label)
        self.status_bar.addPermanentWidget(self._frame_label)

        self._update_status("Ready")

    def _connect_signals(self):
        self.action_open_folder.triggered.connect(self._on_open_folder)
        self.action_extract_frames.triggered.connect(self._on_extract_frames)
        self.action_auto_label.triggered.connect(self._on_auto_label)
        self.action_export.triggered.connect(self._on_export)
        self.action_undo.triggered.connect(self._on_undo)
        self.action_redo.triggered.connect(self._on_redo)
        self.action_toggle_masks.toggled.connect(self._canvas.set_show_masks)
        self.action_shortcuts.triggered.connect(self._on_shortcuts_dialog)
        self.action_quit.triggered.connect(self.close)

        self.action_next_frame.triggered.connect(lambda: self._on_frame_step(1))
        self.action_prev_frame.triggered.connect(lambda: self._on_frame_step(-1))
        self.action_play_pause.triggered.connect(self._on_play_pause)
        self.action_delete_box.triggered.connect(self._on_delete_selected_box)
        self.action_draw_box.triggered.connect(self._on_draw_box)

        self.action_prompt_click.triggered.connect(lambda: self._set_prompt_mode("click"))
        self.action_prompt_box.triggered.connect(lambda: self._set_prompt_mode("box"))
        self.action_edit_mode.triggered.connect(lambda: self._set_edit_mode())

        self._canvas.mode_changed.connect(self._on_canvas_mode_changed)
        self._canvas.prompt_created.connect(self._on_prompt_created)
        self._canvas.box_selected.connect(self._on_box_selected)
        self._canvas.box_modified.connect(self._on_box_modified)

        self._timeline.frame_changed.connect(self._on_frame_changed)

        self._track_list.track_selected.connect(self._on_track_selected)
        self._track_list.add_track_requested.connect(self._on_add_track)

        self._properties.class_changed.connect(self._on_property_class_changed)
        self._properties.box_changed.connect(self._on_property_box_changed)
        self._properties.go_to_frame.connect(self._on_go_to_frame)

        self._history.set_on_change(self._update_undo_redo_state)
        self._shortcuts.shortcuts_changed.connect(self._refresh_all_shortcuts)

    # ---- Session ----

    def _restore_session(self):
        last = self._session.last_folder
        if last:
            self._load_project(Path(last), restore_frame=True)

    # ---- Project Loading ----

    def _on_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Image Folder")
        if not folder:
            return
        self._load_project(Path(folder))

    def _load_project(self, folder: Path, restore_frame: bool = False):
        image_files = sorted([
            f.name for f in folder.iterdir()
            if f.suffix.lower() in SUPPORTED_IMAGE_EXTS
        ])

        if not image_files:
            QMessageBox.warning(self, "Error", "No images found in folder.")
            return

        # Read first image for size
        first = QPixmap(str(folder / image_files[0]))
        img_size = (first.width(), first.height())

        # Check for existing labels
        tracks = self._load_existing_labels(folder, len(image_files), img_size)

        # Check for cached masks
        mask_dir = folder / MASK_CACHE_DIR
        if mask_dir.exists():
            cached = self._sam.load_cached_masks(mask_dir, [t.id for t in tracks])
            # masks loaded but we already have boxes from labels, skip re-conversion

        self._project = ProjectState(
            image_dir=folder,
            image_files=image_files,
            frame_count=len(image_files),
            current_frame=0,
            tracks=tracks,
            classes=list(DEFAULT_CLASSES),
            image_size=img_size,
        )

        self._canvas.load_project(folder, image_files, img_size, tracks)
        self._timeline.set_frame_count(len(image_files))

        # Restore last frame for this folder
        start_frame = 0
        if restore_frame:
            cached = self._session.get_frame(folder)
            if cached is not None and 0 <= cached < len(image_files):
                start_frame = cached

        self._timeline.set_current_frame(start_frame)
        self._project.current_frame = start_frame

        self._track_list.set_tracks(tracks)
        self._properties.set_classes(self._project.classes)
        self._properties.set_annotation(None, None)
        self._history.clear()

        self.action_auto_label.setEnabled(True)
        self.action_export.setEnabled(True)

        self._session.set_last_folder(folder)
        self._update_status(f"Loaded {len(image_files)} frames")

    def _load_existing_labels(self, folder: Path, frame_count: int,
                              img_size: tuple[int, int]) -> list[Track]:
        """Parse existing YOLO .txt files and create tracks."""
        tracks: list[Track] = []
        track_map: dict[int, Track] = {}  # class_id → track for simple case

        for f in range(frame_count):
            label_file = folder / f"frame_{f:06d}.txt"
            if not label_file.exists():
                continue

            for line in label_file.read_text().strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                class_id = int(parts[0])
                x, y, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

                if class_id not in track_map:
                    from auto_labelling.app.constants import TRACK_COLORS
                    track = Track(
                        name=f"Class {class_id}",
                        class_id=class_id,
                        color=TRACK_COLORS[class_id % len(TRACK_COLORS)],
                    )
                    track_map[class_id] = track
                    tracks.append(track)

                track = track_map[class_id]
                ann = Annotation(frame_idx=f, class_id=class_id,
                                 bbox=BBox(x=x, y=y, w=w, h=h), reviewed=True)
                track.add_annotation(ann)

        return tracks

    # ---- Frame Extraction ----

    def _on_extract_frames(self):
        dialog = ExtractDialog(self)
        dialog.extraction_complete.connect(
            lambda folder: self._load_project(Path(folder))
        )
        dialog.exec()

    # ---- Auto Label (SAM 2) ----

    def _on_auto_label(self):
        if not self._project.tracks:
            QMessageBox.information(
                self, "Auto Label",
                "Add tracks first: switch to Click or Box prompt mode, "
                "then click/draw on a person in the canvas."
            )
            return
        self._run_sam_propagation()

    def _on_add_track(self):
        self._set_prompt_mode("click")

    def _set_prompt_mode(self, mode: str):
        self._prompt_mode = mode
        self.action_prompt_click.setChecked(mode == "click")
        self.action_prompt_box.setChecked(mode == "box")
        self.action_edit_mode.setChecked(False)

        if mode == "click":
            self._canvas.set_mode(CanvasMode.PROMPT_CLICK)
        else:
            self._canvas.set_mode(CanvasMode.PROMPT_BOX)

    def _set_edit_mode(self):
        self.action_prompt_click.setChecked(False)
        self.action_prompt_box.setChecked(False)
        self.action_edit_mode.setChecked(True)
        self._canvas.set_mode(CanvasMode.EDIT)

    def _on_prompt_created(self, prompt_data: dict):
        from auto_labelling.app.constants import TRACK_COLORS

        color_idx = len(self._project.tracks) % len(TRACK_COLORS)
        track = Track(
            name=f"Person {len(self._project.tracks) + 1}",
            class_id=0,
            color=TRACK_COLORS[color_idx],
            prompt_frame=prompt_data["frame_idx"],
            prompt_type=prompt_data["type"],
        )

        if prompt_data["type"] == "box":
            track.prompt_box = prompt_data["box"]
        elif prompt_data["type"] == "click":
            track.prompt_point = prompt_data["point"]

        self._project.tracks.append(track)
        self._track_list.set_tracks(self._project.tracks)
        self._update_status(f"Track '{track.name}' created. Click 'Auto Label' to propagate.")

    def _run_sam_propagation(self):
        if not self._project.tracks:
            return

        if not self._sam.is_loaded:
            self._update_status("Loading SAM 2 model (tiny)...")
            self.status_bar.repaint()
            try:
                self._sam.load_model("tiny")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load SAM 2 model:\n{e}")
                return

        prompts = []
        for track in self._project.tracks:
            p = {
                "track_id": track.id,
                "frame_idx": track.prompt_frame,
            }
            if track.prompt_type == "box" and track.prompt_box:
                p["box"] = track.prompt_box
            elif track.prompt_type == "click" and track.prompt_point:
                p["point"] = track.prompt_point
            else:
                continue
            prompts.append(p)

        if not prompts:
            QMessageBox.warning(self, "Error", "No valid prompts to propagate.")
            return

        self._update_status("Running SAM 2 propagation...")

        try:
            mask_dir = self._project.image_dir / MASK_CACHE_DIR
            results = self._sam.propagate(
                self._project.image_dir,
                prompts,
                self._project.frame_count,
                progress_callback=None,
                cache_dir=mask_dir,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"SAM 2 propagation failed:\n{e}")
            return

        self._masks_to_annotations(results)
        self._track_list.set_tracks(self._project.tracks)
        self._canvas.set_frame(self._project.current_frame)
        self._update_status("Auto-labeling complete. Review and correct boxes.")

    def _masks_to_annotations(self, results: dict[str, list]):
        img_w, img_h = self._project.image_size

        for track in self._project.tracks:
            masks = results.get(track.id, [])
            if not masks:
                continue

            boxes = ExportService.masks_to_boxes(masks, track.class_id, img_w, img_h)

            for frame_idx, bbox in boxes:
                if bbox is not None:
                    # Don't overwrite manually reviewed annotations
                    existing = track.get_annotation(frame_idx)
                    if existing and existing.reviewed:
                        continue
                    ann = Annotation(frame_idx=frame_idx, class_id=track.class_id,
                                     bbox=bbox, reviewed=False)
                    track.add_annotation(ann)

    # ---- Review / Edit ----

    def _on_frame_step(self, delta: int):
        new_frame = self._project.current_frame + delta
        if 0 <= new_frame < self._project.frame_count:
            self._timeline.set_current_frame(new_frame)
            self._on_frame_changed(new_frame)

    def _on_play_pause(self):
        self._timeline.toggle_play()

    def _on_delete_selected_box(self):
        if self._canvas.mode == CanvasMode.EDIT:
            self._canvas.delete_selected_boxes()

    def _on_draw_box(self):
        pass  # In Edit mode, just drag on canvas to draw a new box

    def _on_frame_changed(self, frame: int):
        self._project.current_frame = frame
        self._canvas.set_frame(frame)

        self._frame_label.setText(f"Frame {frame}/{self._project.frame_count - 1}")

        selected_track = self._project.selected_track()
        if selected_track:
            ann = selected_track.get_annotation(frame)
            self._properties.set_annotation(selected_track, ann)
        else:
            self._properties.set_annotation(None, None)

        self._auto_save_current_frame()

    def _on_box_selected(self, box_item):
        if box_item:
            ann = box_item.track.get_annotation(box_item.frame_idx)
            self._properties.set_annotation(box_item.track, ann)
        else:
            self._properties.set_annotation(None, None)

    def _on_box_modified(self, track, annotation):
        self._project.is_modified = True
        self._track_list.set_tracks(self._project.tracks)

    def _on_track_selected(self, track_id: str):
        for t in self._project.tracks:
            t._selected = (t.id == track_id)

    def _on_property_class_changed(self, track, annotation, new_class_id):
        cmd = ChangeClassCommand(annotation, annotation.class_id, new_class_id)
        self._history.execute(cmd)
        self._project.is_modified = True

    def _on_property_box_changed(self, track, annotation, new_bbox):
        old_bbox = annotation.bbox
        if old_bbox and old_bbox.is_close_to(new_bbox):
            return
        cmd = ResizeBoxCommand(annotation, old_bbox, new_bbox)
        self._history.execute(cmd)
        self._canvas.set_frame(self._project.current_frame)
        self._project.is_modified = True

    def _on_go_to_frame(self, frame: int):
        self._timeline.set_current_frame(frame)
        self._on_frame_changed(frame)

    def _auto_save_current_frame(self):
        if not self._project.image_dir:
            return
        annotations = ExportService.build_annotations_from_tracks(
            self._project.tracks, self._project.frame_count)
        # Only write current frame
        frame_data = {self._project.current_frame:
                      annotations.get(self._project.current_frame, [])}
        ExportService.save_yolo_labels(
            self._project.image_dir, frame_data, self._project.classes)

    # ---- Undo / Redo ----

    def _on_undo(self):
        self._history.undo()
        self._canvas.set_frame(self._project.current_frame)
        self._track_list.set_tracks(self._project.tracks)

    def _on_redo(self):
        self._history.redo()
        self._canvas.set_frame(self._project.current_frame)
        self._track_list.set_tracks(self._project.tracks)

    def _update_undo_redo_state(self):
        self.action_undo.setEnabled(self._history.can_undo)
        self.action_redo.setEnabled(self._history.can_redo)
        if self._history.can_undo:
            self.action_undo.setText(f"Undo {self._history.undo_description}")
        else:
            self.action_undo.setText("Undo")
        if self._history.can_redo:
            self.action_redo.setText(f"Redo {self._history.redo_description}")
        else:
            self.action_redo.setText("Redo")

    # ---- Export ----

    def _on_export(self):
        if not self._project.image_dir:
            return

        annotations = ExportService.build_annotations_from_tracks(
            self._project.tracks, self._project.frame_count)

        total_boxes = sum(len(boxes) for boxes in annotations.values())
        reply = QMessageBox.question(
            self, "Export Labels",
            f"Export {self._project.frame_count} frames with {total_boxes} total boxes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ExportService.save_yolo_labels(
            self._project.image_dir, annotations, self._project.classes)
        self._project.is_modified = False
        self._update_status(f"Exported {total_boxes} boxes across {self._project.frame_count} frames")

    # ---- Helpers ----

    def _on_canvas_mode_changed(self, mode: CanvasMode):
        labels = {
            CanvasMode.VIEW: "Mode: View",
            CanvasMode.PROMPT_CLICK: "Mode: Click Prompt",
            CanvasMode.PROMPT_BOX: "Mode: Box Prompt",
            CanvasMode.EDIT: "Mode: Edit",
        }
        self._mode_label.setText(f"  {labels.get(mode, 'Mode: View')}  ")

    def _update_status(self, msg: str):
        self._status_label.setText(msg)
        self.status_bar.showMessage(msg, 5000)

    def _on_shortcuts_dialog(self):
        dialog = ShortcutSettingsDialog(self._shortcuts, self)
        dialog.exec()

    def closeEvent(self, event):
        # Save current position before closing
        if self._project.image_dir:
            self._session.set_frame(self._project.image_dir, self._project.current_frame)

        if self._project.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Export before closing?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._on_export()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()
