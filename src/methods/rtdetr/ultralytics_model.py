"""Ultralytics' own RT-DETR (HGNetv2 backbone, not the paper authors' R18)
for a second RT-DETR data point — same `Detection`/`.detect()` interface
as `Yolo26Detector` and `RtDetrV2Detector`.

Ultralytics only ships `rtdetr-l` (32.97M params) and `rtdetr-x`
(larger still) — no ResNet18-backbone variant, unlike the HF `transformers`
checkpoint used in `src.methods.rtdetr.model`. Kept as a separate class
(not a competing "the" RT-DETR) since it's a meaningfully different,
bigger backbone — see docs/decision_log.md for the comparison.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

PERSON_COCO_CLASS_ID = 0


@dataclass(frozen=True)
class Detection:
    bbox_xywh: tuple[float, float, float, float]
    score: float


class RtDetrUltralyticsDetector:
    """Zero-shot COCO-pretrained RT-DETR (Ultralytics), filtered to 'person'.

    RT-DETR has no NMS at inference (see docs/decision_log.md,
    2026-09-13's resolution-sensitivity finding for the HF R18 checkpoint)
    — `imgsz` here defaults to 640, this model's own native training
    resolution, for the same reason: forcing it higher broke the HF
    checkpoint catastrophically, and there is no reason to expect this
    differently-backboned checkpoint to be immune to the same failure
    mode without first checking.
    """

    def __init__(self, checkpoint: str = "rtdetr-l.pt", conf: float = 0.25, imgsz: int = 640) -> None:
        from ultralytics import RTDETR

        self._model = RTDETR(checkpoint)
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
