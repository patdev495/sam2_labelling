from pathlib import Path

import numpy as np
import cv2

from auto_labelling.models.track import Track
from auto_labelling.models.annotation import Annotation, BBox


class ExportService:
    @staticmethod
    def masks_to_boxes(
        masks: list[np.ndarray],
        class_id: int = 0,
        img_w: int = 1,
        img_h: int = 1,
        min_area: int = 100,
    ) -> list[tuple[int, BBox | None]]:
        results: list[tuple[int, BBox | None]] = []
        for frame_idx, mask in enumerate(masks):
            if mask.sum() < min_area:
                results.append((frame_idx, None))
                continue

            contours, _ = cv2.findContours(
                mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if not contours:
                results.append((frame_idx, None))
                continue

            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)

            bbox = BBox.from_xyxy(x, y, x + w, y + h, img_w, img_h)
            results.append((frame_idx, bbox))

        return results

    @staticmethod
    def save_yolo_labels(
        output_dir: str | Path,
        annotations: dict[int, list[tuple[int, BBox]]],
        classes: list[str],
    ):
        output_dir = Path(output_dir)
        for frame_idx, boxes in annotations.items():
            lines = []
            for class_id, bbox in boxes:
                if bbox is not None:
                    lines.append(f"{class_id} {bbox.to_yolo_str()}")

            if lines:
                name = f"frame_{frame_idx:06d}.txt"
                (output_dir / name).write_text("\n".join(lines))

    @staticmethod
    def build_annotations_from_tracks(
        tracks: list[Track],
        frame_count: int,
    ) -> dict[int, list[tuple[int, BBox]]]:
        result: dict[int, list[tuple[int, BBox]]] = {}
        for f in range(frame_count):
            result[f] = []
            for track in tracks:
                ann = track.get_annotation(f)
                if ann and ann.bbox is not None:
                    result[f].append((ann.class_id, ann.bbox))
        return result

    @staticmethod
    def save_masks_as_images(
        masks: list[np.ndarray],
        output_dir: str | Path,
        prefix: str = "mask",
    ):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for i, mask in enumerate(masks):
            img = (mask.astype(np.uint8) * 255)
            cv2.imwrite(str(output_dir / f"{prefix}_{i:06d}.png"), img)
