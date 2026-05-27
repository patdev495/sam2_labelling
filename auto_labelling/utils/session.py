import json
from pathlib import Path

from auto_labelling.app.constants import SHORTCUTS_CONFIG_DIR

SESSION_FILE = SHORTCUTS_CONFIG_DIR / "session.json"


class SessionManager:
    def __init__(self):
        self._data: dict = {"last_folder": None, "folder_frames": {}}
        self._load()

    def _load(self):
        if SESSION_FILE.exists():
            try:
                self._data = {
                    "last_folder": None,
                    "folder_frames": {},
                    **json.loads(SESSION_FILE.read_text()),
                }
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self):
        SHORTCUTS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        SESSION_FILE.write_text(json.dumps(self._data, indent=2))

    @property
    def last_folder(self) -> str | None:
        path = self._data.get("last_folder")
        if path and Path(path).exists():
            return path
        return None

    def set_last_folder(self, folder: str | Path):
        self._data["last_folder"] = str(folder)
        self._save()

    def get_frame(self, folder: str | Path) -> int | None:
        key = str(folder)
        return self._data.get("folder_frames", {}).get(key)

    def set_frame(self, folder: str | Path, frame_idx: int):
        key = str(folder)
        self._data.setdefault("folder_frames", {})[key] = frame_idx
        self._save()
