"""Draw ground-truth + prediction boxes on the same image for visual QA.

Used for the presentation's qualitative comparison, not just the
quantitative metrics in metrics.py.
"""
from __future__ import annotations

import cv2
import numpy as np

GT_COLOR = (0, 0, 255)  # red, BGR
PRED_COLOR = (0, 255, 0)  # green, BGR


def draw_comparison(
    image: np.ndarray,
    gt_boxes: list[list[float]],
    predictions: list[tuple[list[float], float]],
) -> np.ndarray:
    """gt_boxes: list of [x, y, w, h]. predictions: list of ([x, y, w, h], score)."""
    annotated = image.copy()

    for x, y, w, h in gt_boxes:
        x, y, w, h = int(x), int(y), int(w), int(h)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), GT_COLOR, 2)

    for (x, y, w, h), score in predictions:
        x, y, w, h = int(x), int(y), int(w), int(h)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), PRED_COLOR, 2)
        cv2.putText(
            annotated, f"{score:.2f}", (x, max(0, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, PRED_COLOR, 2,
        )

    # legend
    cv2.rectangle(annotated, (10, 10), (30, 30), GT_COLOR, -1)
    cv2.putText(annotated, "ground truth", (36, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.rectangle(annotated, (10, 40), (30, 60), PRED_COLOR, -1)
    cv2.putText(annotated, "prediction", (36, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return annotated
