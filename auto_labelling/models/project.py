from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from auto_labelling.models.track import Track


@dataclass
class ProjectState:
    image_dir: Optional[Path] = None
    image_files: list[str] = field(default_factory=list)
    frame_count: int = 0
    current_frame: int = 0
    tracks: list[Track] = field(default_factory=list)
    classes: list[str] = field(default_factory=lambda: ["person"])
    image_size: tuple[int, int] = (0, 0)
    is_modified: bool = False
    video_path: Optional[Path] = None

    @property
    def frame_names(self) -> list[str]:
        return self.image_files

    def selected_track(self) -> Optional[Track]:
        for t in self.tracks:
            if hasattr(t, '_selected') and t._selected:
                return t
        return self.tracks[0] if self.tracks else None
