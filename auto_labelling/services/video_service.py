from pathlib import Path
from typing import Callable

import cv2


class VideoService:
    @staticmethod
    def extract_frames(
        video_path: str | Path,
        output_dir: str | Path,
        frame_skip: int = 1,
        start_sec: float = 0.0,
        end_sec: float | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[str]:
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        start_frame = int(start_sec * fps) if start_sec > 0 else 0
        end_frame = total_frames
        if end_sec is not None and end_sec > 0:
            end_frame = min(int(end_sec * fps), total_frames)

        frame_names: list[str] = []
        frame_idx = 0
        saved_count = 0

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        for f in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break

            if (f - start_frame) % frame_skip == 0:
                name = f"frame_{saved_count:06d}.jpg"
                out_path = output_dir / name
                cv2.imwrite(str(out_path), frame)
                frame_names.append(name)
                saved_count += 1

            frame_idx += 1
            if progress_callback:
                progress_callback(f - start_frame + 1, end_frame - start_frame)

        cap.release()
        return frame_names

    @staticmethod
    def get_video_info(video_path: str | Path) -> dict:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration_sec": 0,
        }
        if info["fps"] > 0:
            info["duration_sec"] = info["frame_count"] / info["fps"]

        cap.release()
        return info
