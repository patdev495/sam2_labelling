from pathlib import Path
from typing import Optional, Callable

import numpy as np
import cv2


class SAM2Service:
    def __init__(self):
        self._predictor = None
        self._model_variant: str = "tiny"
        self._device: str = "cpu"

    def _detect_device(self) -> str:
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    @property
    def is_loaded(self) -> bool:
        return self._predictor is not None

    @property
    def device(self) -> str:
        return self._device

    def load_model(self, variant: str = "tiny") -> None:
        from sam2.build_sam import build_sam2_video_predictor

        self._device = self._detect_device()

        model_cfg = {
            "tiny": "sam2_hiera_t.yaml",
            "small": "sam2_hiera_s.yaml",
            "base_plus": "sam2_hiera_b+.yaml",
            "large": "sam2_hiera_l.yaml",
        }

        if variant not in model_cfg:
            raise ValueError(f"Unknown variant: {variant}. Use: {list(model_cfg.keys())}")

        cfg_file = model_cfg[variant]
        checkpoint = f"sam2_hiera_{variant}.pt"

        if self._device == "cuda":
            self._predictor = build_sam2_video_predictor(cfg_file, checkpoint, device="cuda")
        else:
            self._predictor = build_sam2_video_predictor(cfg_file, checkpoint, device="cpu")

        self._model_variant = variant

    def propagate(
        self,
        image_dir: str | Path,
        prompts: list[dict],
        frame_count: int,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        cache_dir: Optional[Path] = None,
    ) -> dict[str, list[np.ndarray]]:
        if self._predictor is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        image_dir = Path(image_dir)

        inference_state = self._predictor.init_state(video_path=str(image_dir))

        for i, prompt in enumerate(prompts):
            track_id = prompt.get("track_id", f"track_{i}")
            frame_idx = prompt["frame_idx"]
            obj_id = i + 1

            if "box" in prompt and prompt["box"] is not None:
                box = prompt["box"]
                _, _, _, out_mask_logits = self._predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=frame_idx,
                    obj_id=obj_id,
                    box=[box["x1"], box["y1"], box["x2"], box["y2"]],
                )
            elif "point" in prompt and prompt["point"] is not None:
                pt = prompt["point"]
                points = np.array([[pt["x"], pt["y"]]], dtype=np.float32)
                labels = np.array([1], dtype=np.int32)
                _, _, _, out_mask_logits = self._predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=frame_idx,
                    obj_id=obj_id,
                    points=points,
                    labels=labels,
                )
            else:
                raise ValueError(f"Prompt {i} must have 'box' or 'point'")

            prompt["obj_id"] = obj_id

        results: dict[str, list[np.ndarray]] = {
            prompt.get("track_id", f"track_{i}"): []
            for i, prompt in enumerate(prompts)
        }

        video_segments = {}
        for out_frame_idx, out_obj_ids, out_mask_logits in self._predictor.propagate_in_video(
            inference_state, start_frame_idx=0
        ):
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()[0]
                for i, out_obj_id in enumerate(out_obj_ids)
            }

            for prompt in prompts:
                track_id = prompt.get("track_id", f"track_{prompts.index(prompt)}")
                obj_id = prompt["obj_id"]
                mask = video_segments[out_frame_idx].get(obj_id, np.zeros((1, 1), dtype=bool))
                results[track_id].append(mask)

            if progress_callback:
                progress_callback(out_frame_idx + 1, frame_count)

        if cache_dir:
            self._cache_masks(results, cache_dir)

        return results

    def _cache_masks(self, results: dict[str, list[np.ndarray]], cache_dir: Path):
        cache_dir.mkdir(parents=True, exist_ok=True)
        for track_id, masks in results.items():
            track_cache = cache_dir / track_id
            track_cache.mkdir(exist_ok=True)
            for i, mask in enumerate(masks):
                np.save(str(track_cache / f"frame_{i:06d}.npy"), mask)

    def load_cached_masks(self, cache_dir: Path, track_ids: list[str]) -> dict[str, list[np.ndarray]]:
        results = {}
        for track_id in track_ids:
            track_cache = cache_dir / track_id
            masks = []
            if track_cache.exists():
                for npy in sorted(track_cache.glob("frame_*.npy")):
                    masks.append(np.load(str(npy)))
            if masks:
                results[track_id] = masks
        return results
