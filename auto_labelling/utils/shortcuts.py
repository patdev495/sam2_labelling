import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence

from auto_labelling.app.constants import SHORTCUTS_CONFIG_FILE

DEFAULT_SHORTCUTS = {
    "next_frame": "Right",
    "prev_frame": "Left",
    "play_pause": "Space",
    "delete_box": "Del",
    "draw_box": "B",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Y",
    "save": "Ctrl+S",
    "auto_label": "Ctrl+L",
    "open_video": "Ctrl+O",
    "extract_frames": "Ctrl+E",
}


class ShortcutManager(QObject):
    shortcuts_changed = Signal()

    def __init__(self):
        super().__init__()
        self._shortcuts: dict[str, str] = {}
        self._load()

    def _load(self):
        SHORTCUTS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if SHORTCUTS_CONFIG_FILE.exists():
            try:
                saved = json.loads(SHORTCUTS_CONFIG_FILE.read_text())
                self._shortcuts = {**DEFAULT_SHORTCUTS, **saved}
            except (json.JSONDecodeError, KeyError):
                self._shortcuts = dict(DEFAULT_SHORTCUTS)
        else:
            self._shortcuts = dict(DEFAULT_SHORTCUTS)
            self._save()

    def _save(self):
        SHORTCUTS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        SHORTCUTS_CONFIG_FILE.write_text(json.dumps(self._shortcuts, indent=2))

    def get(self, action: str) -> Optional[QKeySequence]:
        keystr = self._shortcuts.get(action)
        if keystr:
            return QKeySequence(keystr)
        return None

    def set(self, action: str, keystr: str):
        self._shortcuts[action] = keystr
        self._save()
        self.shortcuts_changed.emit()

    def reset(self, action: str):
        default = DEFAULT_SHORTCUTS.get(action)
        if default:
            self._shortcuts[action] = default
            self._save()
            self.shortcuts_changed.emit()

    def reset_all(self):
        self._shortcuts = dict(DEFAULT_SHORTCUTS)
        self._save()
        self.shortcuts_changed.emit()

    def all_shortcuts(self) -> dict[str, str]:
        return dict(self._shortcuts)
