# Implementation Plan: SAM 2 Video Labeling Tool

## Context

Build a PySide6 desktop app that uses SAM 2 to accelerate bounding-box labeling for YOLO person detection training. Input: warehouse camera video → Output: YOLO-format `.txt` labels alongside extracted frames in the same folder.

Goal: reduce annotation time from hours (frame-by-frame) to minutes (1-3 prompts per video + review).

## Architecture

```
MainWindow
├── MenuBar / Toolbar
├── CentralSplitter (horizontal)
│   ├── TrackListPanel (left sidebar)
│   ├── CanvasWidget (center, image + boxes + masks)
│   └── PropertiesPanel (right sidebar, selected box info)
├── TimelineWidget (bottom, frame scrubber + play/pause)
└── StatusBar
```

**Data flow:**
```
Video → VideoService.extract_frames() → folder of JPEGs
User opens folder → FrameLoader loads images on-demand
User prompts on frame N → SAMService.propagate() → masks[N tracks × F frames]
Mask → BoxConverter → AnnotationStore (mutable box list per frame per track)
User reviews/corrects → AnnotationStore updates (with Command history for undo)
Export → YOLO txt writer (one .txt per frame, same folder)
```

**Key design decisions:**
- Lazy frame loading: load images only when displaying/scrolling (don't keep all frames in RAM)
- SAM 2 runs once per track → masks cached to disk (`.mask/` subfolder) for reload without re-inference
- Command pattern for undo/redo (each box edit is a Command)
- Keyboard shortcuts stored in `~/.auto_labelling/shortcuts.json`
- No project file; folder = project state

## Tech Stack
- PySide6, OpenCV (cv2), numpy, torch, segment-anything-2 (SAM 2), Pillow

## Implementation Phases

### Phase 1 — Project Scaffold
- Create `pyproject.toml` with dependencies
- Create package structure:
  ```
  auto_labelling/
  ├── __init__.py
  ├── main.py              # entry point, QApplication, MainWindow
  ├── app/
  │   ├── __init__.py
  │   ├── main_window.py   # QMainWindow subclass, layout setup
  │   └── constants.py     # app-wide constants
  ├── services/
  │   ├── __init__.py
  │   ├── video_service.py # Video → frame extraction (OpenCV VideoCapture)
  │   ├── sam_service.py   # SAM 2 model load, prompt, propagate
  │   └── export_service.py# Mask → YOLO txt, annotation export
  ├── models/
  │   ├── __init__.py
  │   ├── annotation.py    # Annotation dataclass (frame_idx, class_id, bbox)
  │   ├── track.py         # Track dataclass (id, color, prompts, annotations)
  │   └── project.py       # ProjectState dataclass (tracks, current_frame, folder)
  ├── widgets/
  │   ├── __init__.py
  │   ├── canvas.py        # CanvasWidget — image display, box drawing/editing, prompt
  │   ├── timeline.py      # TimelineWidget — frame scrubber
  │   ├── track_list.py    # TrackListPanel — sidebar track list
  │   ├── properties.py    # PropertiesPanel — selected box properties
  │   └── extract_dialog.py# Video extract dialog (fps, skip, output)
  └── utils/
      ├── __init__.py
      ├── commands.py      # Command pattern for undo/redo
      └── shortcuts.py     # Keyboard shortcut manager + config
  ```

### Phase 2 — Video Service & Frame Extraction
- `video_service.py`:
  - `extract_frames(video_path, output_dir, frame_skip=1)` → extracts JPEGs via OpenCV `VideoCapture`
  - Returns list of frame filenames
  - Progress callback for UI
- Basic test: extract 10 frames from a test video, verify files exist

### Phase 3 — SAM 2 Service (Core Engine)
- `sam_service.py`:
  - `load_model(variant="tiny")` → download + load SAM 2 model
  - `propagate(image_dir, prompts, frame_count)` → runs SAM 2 batch inference
    - Input: directory of frames, list of prompts (frame_idx, point/box coords, track_id)
    - Output: mask per frame per track (numpy arrays)
  - Masks cached to `image_dir/.masks/track_{id}/frame_{n}.npy`
  - Returns `dict[track_id, list[masks]]`
- `export_service.py`:
  - `masks_to_boxes(masks)` → convert mask to tight bounding box (xyxy → normalized yolo)
  - `save_yolo_labels(frame_dir, annotations)` → write one `.txt` per frame

### Phase 4 — Data Models
- `annotation.py`: `Annotation(frame_idx, class_id, bbox_xyxy, bbox_yolo)`
- `track.py`: `Track(id, name, color, prompts, annotations: dict[frame_idx, Annotation])`
- `project.py`: `ProjectState(tracks, current_frame, frame_count, image_dir)`

### Phase 5 — Canvas Widget (Core UI)
- Display current frame image
- Mouse interactions:
  - **Prompt mode**: Click = add point, Drag = draw box → creates prompt for SAM 2
  - **Edit mode**: Click box = select, drag to move, drag corners to resize, Del = delete, B+click+drag = new box
- Keyboard: ←/→ = prev/next frame
- Zoom: Ctrl+scroll wheel
- Pan: middle mouse drag
- Overlay: toggle mask/box-only via toolbar button

### Phase 6 — Timeline Widget
- Horizontal slider: 0 to frame_count-1
- Tick marks at reviewed frames
- Play/pause button (auto-advance frames, configurable FPS)
- Track-colored dots on frames that have annotations

### Phase 7 — Track List Panel
- List of tracks: name, color swatch, frame range, annotation count
- Buttons: Add Track (enter prompt mode), Delete Track, Toggle Visibility
- Click track → select it, highlight its boxes on canvas

### Phase 8 — Properties Panel
- Shows selected box: class dropdown, bbox coordinates (x, y, w, h)
- Editable fields update annotation in real-time
- "Go to frame" button

### Phase 9 — Undo/Redo (Command Pattern)
- `commands.py`:
  - `Command` base class (execute, undo)
  - `AddBoxCommand`, `DeleteBoxCommand`, `MoveBoxCommand`, `ResizeBoxCommand`, `ChangeClassCommand`
- `CommandHistory` stack per project (undo_stack, redo_stack)
- Ctrl+Z / Ctrl+Y

### Phase 10 — Keyboard Shortcuts Manager
- `shortcuts.py`:
  - Read `~/.auto_labelling/shortcuts.json` (create defaults if missing)
  - Map action names → QKeySequence
  - Settings dialog to customize shortcuts (table: Action | Shortcut | Reset button)

### Phase 11 — Extract Dialog
- PySide6 QDialog
- Fields: Video file (browse), Output directory (browse), Frame skip (spinbox), Start/End time (optional)
- Progress bar during extraction
- "Open folder after extract" checkbox

### Phase 12 — Integration & Polish
- Wire all widgets together in MainWindow
- Toolbar actions: Open Video, Extract Frames, Auto-Label (SAM 2), Export Labels, Review Mode toggle
- Status: frame number, track count, annotation count
- Error handling: SAM 2 model missing, invalid video, folder exists warning
- Auto-save: on frame change, write current frame's YOLO txt

### Phase 13 — Export
- "Export All Labels" button → write YOLO txt for every annotated frame
- "Export Reviewed Only" → skip unreviewed frames
- Confirmation dialog with summary (N frames, M boxes exported)

## Verification
1. Unit tests: VideoService.extract_frames, ExportService.masks_to_boxes, Command undo/redo
2. Integration test: pass a 30-frame folder through full pipeline (prompt → propagate → review → edit → export)
3. Manual test: load real warehouse video, extract frames, auto-label with SAM 2, review 10 frames, export, verify YOLO txt format correct
4. Edge cases: empty frame (no person), person appears mid-video, 2 people overlapping
