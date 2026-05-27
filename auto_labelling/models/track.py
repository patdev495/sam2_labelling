from dataclasses import dataclass, field
from uuid import uuid4
from typing import Optional

from auto_labelling.models.annotation import Annotation, BBox


@dataclass
class Track:
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    name: str = ""
    color: str = "#FF6B6B"
    class_id: int = 0
    visible: bool = True
    prompt_frame: int = 0
    prompt_type: str = "click"  # "click" or "box"
    prompt_point: Optional[dict] = None  # {"x": px, "y": px} for click
    prompt_box: Optional[dict] = None  # {"x1": px, "y1": px, "x2": px, "y2": px} for box
    annotations: dict[int, Annotation] = field(default_factory=dict)

    def get_annotation(self, frame_idx: int) -> Optional[Annotation]:
        return self.annotations.get(frame_idx)

    def add_annotation(self, annotation: Annotation):
        self.annotations[annotation.frame_idx] = annotation

    def remove_annotation(self, frame_idx: int):
        self.annotations.pop(frame_idx, None)

    @property
    def frame_range(self) -> tuple[int, int]:
        if not self.annotations:
            return 0, 0
        indices = sorted(self.annotations.keys())
        return indices[0], indices[-1]

    @property
    def annotation_count(self) -> int:
        return len(self.annotations)
