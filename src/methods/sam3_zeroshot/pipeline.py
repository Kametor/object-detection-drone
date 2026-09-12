"""Core auto-labeling pipeline: video + prompt + fps -> detections per frame.

Reused for two purposes: (1) our own train/val pseudo-label generation and
background-video verification, (2) an end-to-end tool for a reviewer's own
uploaded video, run the same way from a notebook or scripts/04_label_video.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.data.sampling import read_frame, sample_diverse_frames
from src.methods.sam3_zeroshot.model import Detection, PromptableDetector


@dataclass(frozen=True)
class LabeledFrame:
    frame_idx: int
    timestamp_s: float
    image: np.ndarray
    detections: list[Detection]


def label_video(
    video_path: Path,
    prompt: str,
    fps: float,
    detector: PromptableDetector,
    dedup_threshold: float = 8.0,
    max_gap_seconds: float = 2.0,
    confidence_threshold: float = 0.3,
) -> list[LabeledFrame]:
    """Sample diverse frames from `video_path` and run `detector` on each.

    Detections below `confidence_threshold` are dropped. This is the single
    entry point used both for our own train/val videos and for an arbitrary
    video a reviewer points the tool at.
    """
    sampled = sample_diverse_frames(
        video_path=video_path,
        fps=fps,
        dedup_threshold=dedup_threshold,
        max_gap_seconds=max_gap_seconds,
    )

    labeled_frames = []
    for frame in sampled:
        image = read_frame(video_path, frame.frame_idx)
        detections = [
            d for d in detector.detect(image, prompt) if d.score >= confidence_threshold
        ]
        labeled_frames.append(
            LabeledFrame(
                frame_idx=frame.frame_idx,
                timestamp_s=frame.timestamp_s,
                image=image,
                detections=detections,
            )
        )
    return labeled_frames


def draw_detections(image: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Return a copy of `image` with boxes + confidence scores drawn on it."""
    annotated = image.copy()
    for det in detections:
        x, y, w, h = (int(round(v)) for v in det.bbox_xywh)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{det.score:.2f}"
        cv2.putText(
            annotated,
            label,
            (x, max(0, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
    return annotated


def to_coco(labeled_frames: list[LabeledFrame], video_name: str, category_name: str) -> dict:
    """Build a COCO-style annotation dict for one video's labeled frames."""
    images = []
    annotations = []
    annotation_id = 1
    for image_id, frame in enumerate(labeled_frames, start=1):
        h, w = frame.image.shape[:2]
        images.append(
            {
                "id": image_id,
                "file_name": f"{Path(video_name).stem}/frame_{frame.frame_idx:06d}.jpg",
                "width": w,
                "height": h,
                "video": video_name,
                "frame_idx": frame.frame_idx,
                "timestamp_s": frame.timestamp_s,
            }
        )
        for det in frame.detections:
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": list(det.bbox_xywh),
                    "score": det.score,
                    "area": det.bbox_xywh[2] * det.bbox_xywh[3],
                    "iscrowd": 0,
                }
            )
            annotation_id += 1

    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": category_name}],
    }
