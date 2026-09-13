"""RT-DETRv2-R18 wrapper for the zero-shot COCO-pretrained sanity check
and, later, pseudo-label fine-tuning (Tier 1 item 2).

Same `Detection` shape and `.detect()` interface as
`src.methods.yolo.model.Yolo26Detector`, so every downstream piece
(evaluation, visualization, predictions.json format) is reused unchanged
— only the detector differs.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import torch
from transformers import RTDetrImageProcessor, RTDetrV2ForObjectDetection

PERSON_COCO_CLASS_ID = 0


@dataclass(frozen=True)
class Detection:
    bbox_xywh: tuple[float, float, float, float]
    score: float


class RtDetrV2Detector:
    """Zero-shot COCO-pretrained RT-DETRv2-R18, filtered to the 'person' class.

    `PekingU/rtdetr_v2_r18vd` is RT-DETRv2's own R18-backbone checkpoint,
    COCO-only pretrained (no Objects365 variant exists for v2 on the Hub,
    consistent with v1's naming convention where the plain name means
    COCO-only) — the same pretraining corpus as `Yolo26Detector`'s
    COCO-pretrained weights, so the two zero-shot checks are a fair,
    apples-to-apples architecture comparison.

    `image_size` overrides the processor's own default (640x640, far below
    our source footage's up to 3840x2160) — unlike YOLO26n's configurable
    `imgsz`, RT-DETR's preprocessing always resizes to one fixed
    height/width (no aspect-ratio letterboxing), so this must be set
    explicitly for a fair comparison. Default here (1920x1088) matches
    YOLO's imgsz=1920 on the long side, rounded to a multiple of 32 (the
    backbone's stride) on the short side, for our 16:9 source video.
    """

    def __init__(
        self,
        checkpoint: str = "PekingU/rtdetr_v2_r18vd",
        conf: float = 0.25,
        image_size: tuple[int, int] = (1088, 1920),  # (height, width)
    ) -> None:
        height, width = image_size
        self._processor = RTDetrImageProcessor.from_pretrained(
            checkpoint, size={"height": height, "width": width}
        )
        self._model = RTDetrV2ForObjectDetection.from_pretrained(checkpoint)
        self._model.eval()
        self._conf = conf

    def detect(self, image: np.ndarray) -> list[Detection]:
        """`image`: BGR, as returned by `cv2.imread` — matches Yolo26Detector."""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        inputs = self._processor(images=rgb, return_tensors="pt")
        with torch.no_grad():
            outputs = self._model(**inputs)
        result = self._processor.post_process_object_detection(
            outputs, threshold=self._conf, target_sizes=[(h, w)]
        )[0]

        detections = []
        for box, score, label in zip(result["boxes"], result["scores"], result["labels"]):
            if int(label) != PERSON_COCO_CLASS_ID:
                continue
            x1, y1, x2, y2 = box.tolist()
            detections.append(
                Detection(bbox_xywh=(x1, y1, x2 - x1, y2 - y1), score=float(score))
            )
        return detections
