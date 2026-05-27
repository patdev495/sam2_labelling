# Auto Labelling

SAM 2 video labeling tool — accelerates bounding-box annotation for YOLO detection training.

## Features

**Video & Frames**
- Open video (mp4/avi/mov/mkv/webm), extract frames with configurable frame skip
- Start/end time range, progress bar during extraction
- Lazy frame loading — works with large frame sets without high RAM usage

**Auto Labeling (SAM 2)**
- Click or box prompt on any frame, SAM 2 propagates masks bidirectionally
- Multi-track support for multiple people in the same video
- Mask cache (`.masks/`) — no re-inference if you reopen the folder
- Mask overlay toggle to visually verify SAM 2 output

**Review & Edit**
- Timeline scrubber with play/pause
- Box operations: drag to move, corner handles to resize, delete, draw new
- Track sidebar with per-track colors and annotation counts
- Properties panel: class dropdown, editable bbox coordinates, go-to-frame

**Export**
- YOLO format: one `.txt` per frame (`class x y w h`, normalized)
- Auto-save: writes current frame on frame change
- Batch export all labels with confirmation dialog

**Undo/Redo**
- Full command history (add, delete, move, resize, change class)
- Ctrl+Z / Ctrl+Y or toolbar buttons

**Customizable Keyboard Shortcuts**
- GUI dialog: double-click to rebind, per-action reset, reset all to defaults
- Stored in `~/.auto_labelling/shortcuts.json`, persists across sessions

**Session Memory**
- Remembers last opened folder, auto-reopens on app launch
- Remembers last frame per folder, auto-jumps to it

**UI**
- Purple dark theme with custom SVG icons (17 icons)
- Toolbar with icon + text, rounded buttons, styled scrollbar/slider/menu

## Install

```bash
# 1. Base deps (UI, video, image)
uv sync

# 2. ML deps (torch) — only needed for SAM 2 auto-labeling
uv sync --extra ml

# 3. SAM 2 — not on PyPI, install from GitHub
pip install git+https://github.com/facebookresearch/sam2.git
```

## Run

```bash
uv run python -m auto_labelling.main
# or double-click: run.bat
```

## Workflow

1. **Extract frames** — Open video via `Ctrl+E`, set frame skip, extract to folder
2. **Add tracks** — Switch to Click or Box prompt mode, click/drag on a person
3. **Auto label** — `Ctrl+L` runs SAM 2 propagation (batch, offline)
4. **Review** — Scrub timeline, toggle mask overlay, correct bad boxes
5. **Export** — `Ctrl+S` writes all YOLO `.txt` labels alongside frames

## Keyboard Shortcuts (defaults)

| Key | Action |
|-----|--------|
| `→` / `←` | Next / previous frame |
| `Space` | Play / pause |
| `Del` | Delete selected box |
| `B` | Draw new box (in Edit mode) |
| `Ctrl+Z` / `Ctrl+Y` | Undo / redo |
| `Ctrl+O` | Open folder |
| `Ctrl+E` | Extract frames |
| `Ctrl+L` | Auto label (SAM 2) |
| `Ctrl+S` | Export labels |

Customize via **Toolbar → Shortcuts...** or edit `~/.auto_labelling/shortcuts.json`.
