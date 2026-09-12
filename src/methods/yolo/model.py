"""YOLO26 wrapper for the zero-shot COCO-pretrained sanity check.

Unlike SAM3/YOLO-World (src/methods/sam3_zeroshot/), this is a fixed-class
detector, not open-vocabulary — it only ever looks for COCO class 0
("person"), which happens to already be our target class. No prompt.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

PERSON_COCO_CLASS_ID = 0


@dataclass(frozen=True)
class Detection:
    bbox_xywh: tuple[float, float, float, float]
    score: float


class Yolo26Detector:
    """Zero-shot COCO-pretrained YOLO26, filtered to the 'person' class.

    CPU-friendly by design (nano variant + Ultralytics' CPU-optimized
    YOLO26 build) — meant to run locally on the M1, no Colab/GPU needed.

    `imgsz` defaults to 1920: our source video is nadir-view drone
    footage with small people, and the Ultralytics default (640) would
    shrink them well below what a nano CNN backbone can represent. CNNs
    (unlike SAM3's ViT) scale roughly linearly with resolution, not
    quadratically, so this is a much smaller risk than it was for SAM3 —
    still worth confirming inference time is reasonable on first run.
    """

    def __init__(self, checkpoint: str = "yolo26n.pt", conf: float = 0.25, imgsz: int = 1920) -> None:
        from ultralytics import YOLO

        self._model = YOLO(checkpoint)
        self._conf = conf
        self._imgsz = imgsz

    def detect(self, image: np.ndarray) -> list[Detection]:
        result = self._model.predict(
            image, conf=self._conf, imgsz=self._imgsz, classes=[PERSON_COCO_CLASS_ID], verbose=False
        )[0]
        boxes_xyxy = result.boxes.xyxy.tolist()
        scores = result.boxes.conf.tolist()
        return [
            Detection(bbox_xywh=(x1, y1, x2 - x1, y2 - y1), score=float(score))
            for (x1, y1, x2, y2), score in zip(boxes_xyxy, scores)
        ]
