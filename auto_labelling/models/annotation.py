from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BBox:
    x: float
    y: float
    w: float
    h: float

    def to_xyxy(self, img_w: float = 1.0, img_h: float = 1.0) -> tuple[float, float, float, float]:
        x1 = self.x * img_w
        y1 = self.y * img_h
        x2 = (self.x + self.w) * img_w
        y2 = (self.y + self.h) * img_h
        return x1, y1, x2, y2

    def to_yolo_str(self) -> str:
        return f"{self.x:.6f} {self.y:.6f} {self.w:.6f} {self.h:.6f}"

    @classmethod
    def from_xyxy(cls, x1: float, y1: float, x2: float, y2: float,
                  img_w: float = 1.0, img_h: float = 1.0) -> "BBox":
        if img_w > 1.0:
            x1, x2 = x1 / img_w, x2 / img_w
        if img_h > 1.0:
            y1, y2 = y1 / img_h, y2 / img_h
        return cls(
            x=min(x1, x2),
            y=min(y1, y2),
            w=abs(x2 - x1),
            h=abs(y2 - y1),
        )

    def is_close_to(self, other: "BBox", threshold: float = 0.02) -> bool:
        return (
            abs(self.x - other.x) < threshold
            and abs(self.y - other.y) < threshold
            and abs(self.w - other.w) < threshold
            and abs(self.h - other.h) < threshold
        )


@dataclass
class Annotation:
    frame_idx: int
    class_id: int = 0
    bbox: Optional[BBox] = None
    reviewed: bool = False
