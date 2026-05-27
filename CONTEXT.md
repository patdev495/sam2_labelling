# CONTEXT

A video annotation tool that uses SAM 2 to accelerate bounding-box labeling for YOLO object detection training.

## Glossary

- **Project** — a labeling session centered on one video. Not persisted as a file; project state is the folder of extracted frames + YOLO label files.
- **Video** — raw MP4 footage from the warehouse door camera. User opens a video in the app.
- **Frame extraction** — the process of converting a video into a sequence of image files (`.jpg`) in a dedicated folder. User-configurable frame skip (e.g., keep every Nth frame).
- **Annotation / Label** — a bounding box in YOLO format (`class x_center y_center width height`, normalized). One `.txt` file per frame, stored alongside the source images in the same folder.
- **Class** — object category for labeling. Starts with a single class `person` (class id 0). Class list is user-extensible for future objects.
- **Track** — SAM 2's identity-preserving propagation of a single person's mask across all video frames. Each track has a unique color. Multiple tracks can coexist for multiple people.
- **Prompt** — user input that tells SAM 2 which object to track. Two modes: **click** (center point on the person) or **box** (bounding box drawn around the person). Can be placed at any frame in the video.
- **Propagation (forward + backward)** — SAM 2 runs batch inference from the prompted frame outward in both temporal directions, producing a mask for every frame. Runs offline with a progress bar.
- **Mask** — SAM 2's raw segmentation output (pixel-level region). Converted to a tight bounding box before export.
- **Auto-labeling** — the end-to-end pipeline: prompt → SAM 2 propagate → mask → bounding box. Produces initial labels without manual frame-by-frame work.
- **Review** — manual inspection of auto-labeled frames. User scrubs through the timeline, toggles between box-only and box+mask overlay views, and corrects erroneous boxes.
- **Correction** — editing a bad box during review. Three operations: **drag/resize** an existing box, **delete** a box and redraw, or **draw a new box** from scratch.
- **Timeline / Scrubber** — horizontal slider navigating through frames. Shows which frames have been reviewed.
- **Track list** — sidebar panel showing all tracks (one per prompted person), each with a unique color and identifier.
- **Undo/Redo** — reversible box edit operations, per track, via `Ctrl+Z` / `Ctrl+Y`.

## What this project is NOT

- Not a real-time inference system — batch offline labeling only.
- Not a model training pipeline — only produces YOLO-format labels.
- Not a video management system — one video at a time, folder-based.
