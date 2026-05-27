# Auto Labelling

SAM 2 video labeling tool — accelerates bounding-box annotation for YOLO detection training.

## Install

```bash
# 1. Base deps (UI, video, image)
uv sync

# 2. ML deps (torch) — only needed for SAM 2 auto-labeling
uv sync --extra ml

# 3. SAM 2 — not on PyPI, install from GitHub
pip install git+https://github.com/facebookresearch/sam2.git

# 4. Download SAM 2 checkpoint (tiny variant, ~47M params)
#    Place it in the project root or let the SAM 2 API download it.
```

## Run

```bash
uv run auto-label
```

## Workflow

1. **Extract frames** — Open video → set frame skip → extract to folder
2. **Add tracks** — Switch to Click or Box prompt mode, click/drag on a person
3. **Auto label** — Click "Auto Label" to run SAM 2 propagation
4. **Review** — Scrub timeline, correct bad boxes (drag/resize/delete/redraw)
5. **Export** — Write YOLO-format `.txt` labels alongside frames

Labels export to the same folder as the extracted frames, one `.txt` per frame.

## Keyboard Shortcuts

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

Customize via `~/.auto_labelling/shortcuts.json`.
