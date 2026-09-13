"""Detect-then-verify cascade (item 1b): crop handling and candidate labeling.

YOLO runs at a deliberately low confidence so it proposes far more boxes
than it should; a small classifier then re-examines each proposed box as
a crop and rejects the ones that aren't people. This module holds the
pure pieces — expanding/cropping a candidate box, and deciding what
label a mined candidate should carry.
"""
from __future__ import annotations

import cv2
import numpy as np

PERSON = "person"
NOT_PERSON = "not_person"


def expand_box(
    bbox_xywh: tuple[float, float, float, float],
    padding_ratio: float,
    image_width: int,
    image_height: int,
) -> tuple[int, int, int, int]:
    """Grow a box by `padding_ratio` on each side, clipped to the image.

    A tight crop of a distant person is close to a featureless blob;
    including surrounding context is often what separates "person on a
    trail" from "rock on a trail" for the verifier.
    """
    x, y, w, h = bbox_xywh
    pad_w, pad_h = w * padding_ratio, h * padding_ratio
    x1 = max(0, int(round(x - pad_w)))
    y1 = max(0, int(round(y - pad_h)))
    x2 = min(image_width, int(round(x + w + pad_w)))
    y2 = min(image_height, int(round(y + h + pad_h)))
    return x1, y1, x2, y2


def crop_candidate(
    image: np.ndarray,
    bbox_xywh: tuple[float, float, float, float],
    padding_ratio: float,
    size: int,
) -> np.ndarray | None:
    """Expanded, square-resized crop for the verifier. None if degenerate."""
    h, w = image.shape[:2]
    x1, y1, x2, y2 = expand_box(bbox_xywh, padding_ratio, w, h)
    if x2 - x1 < 2 or y2 - y1 < 2:
        return None
    return cv2.resize(image[y1:y2, x1:x2], (size, size), interpolation=cv2.INTER_LINEAR)


def label_candidate(
    max_iou: float, positive_iou: float, negative_iou: float
) -> str | None:
    """Label a mined candidate, or None for the ignore zone.

    Reference boxes on train/val are SAM3 pseudo-labels, not human truth,
    so anything in the ambiguous middle is dropped rather than guessed:
    a partial overlap is as likely to be a real person the teacher
    mislocalized as it is to be a genuine false positive.
    """
    if max_iou >= positive_iou:
        return PERSON
    if max_iou <= negative_iou:
        return NOT_PERSON
    return None
