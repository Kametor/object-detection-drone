"""Temporal-diversity frame sampling for a single video.

Pure functions only — no file I/O beyond reading the video itself, no CLI.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

DIFF_THUMBNAIL_SIZE = (64, 64)


@dataclass(frozen=True)
class SampledFrame:
    frame_idx: int
    timestamp_s: float


def _thumbnail_gray(frame: np.ndarray) -> np.ndarray:
    small = cv2.resize(frame, DIFF_THUMBNAIL_SIZE, interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)


def _mean_abs_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).mean())


def sample_diverse_frames(
    video_path: Path,
    fps: float,
    dedup_threshold: float,
    max_gap_seconds: float,
) -> list[SampledFrame]:
    """Select temporally-diverse frame indices from a video.

    Candidates are drawn at a uniform `fps` rate, then a candidate is dropped
    if it looks like a near-duplicate of the last KEPT frame (mean abs
    difference on a small grayscale thumbnail below `dedup_threshold`) —
    unless `max_gap_seconds` has elapsed since the last kept frame, in which
    case it is force-kept to preserve temporal coverage.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"could not open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, round(video_fps / fps))

    kept: list[SampledFrame] = []
    last_kept_thumb: np.ndarray | None = None
    last_kept_timestamp: float = -float("inf")

    for frame_idx in range(0, frame_count, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        timestamp_s = frame_idx / video_fps
        thumb = _thumbnail_gray(frame)

        is_duplicate = (
            last_kept_thumb is not None
            and _mean_abs_diff(thumb, last_kept_thumb) < dedup_threshold
        )
        gap_exceeded = (timestamp_s - last_kept_timestamp) >= max_gap_seconds

        if is_duplicate and not gap_exceeded:
            continue

        kept.append(SampledFrame(frame_idx=frame_idx, timestamp_s=timestamp_s))
        last_kept_thumb = thumb
        last_kept_timestamp = timestamp_s

    cap.release()
    return kept


def read_frame(video_path: Path, frame_idx: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"could not open video: {video_path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"could not read frame {frame_idx} from {video_path}")
    return frame
