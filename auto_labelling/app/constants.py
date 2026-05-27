from pathlib import Path

APP_NAME = "Auto Labelling"
APP_VERSION = "0.1.0"
ORG_NAME = "auto_labelling"

DEFAULT_CLASSES = ["person"]

SUPPORTED_VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm")
SUPPORTED_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp")

MASK_CACHE_DIR = ".masks"
YOLO_LABEL_DIR = ""

SHORTCUTS_CONFIG_DIR = Path.home() / ".auto_labelling"
SHORTCUTS_CONFIG_FILE = SHORTCUTS_CONFIG_DIR / "shortcuts.json"

DEFAULT_FRAME_SKIP = 3

CANVAS_BG_COLOR = 40, 40, 40
TRACK_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#BB8FCE", "#85C1E9", "#F8C471", "#82E0AA",
]

MIN_ZOOM = 0.1
MAX_ZOOM = 10.0
ZOOM_STEP = 0.1
