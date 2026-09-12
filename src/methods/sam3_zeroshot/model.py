"""Promptable-detector interface used by the auto-labeling pipeline.

Both real detectors need a GPU and are only meant to be exercised on Colab
(see CLAUDE.md Section 3); `MockDetector` covers local pipeline testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class Detection:
    """A single detected instance. bbox_xywh is in pixel coordinates."""

    bbox_xywh: tuple[float, float, float, float]
    score: float


class PromptableDetector(Protocol):
    """Anything that can find `prompt` in an image and return boxes."""

    def detect(self, image: np.ndarray, prompt: str) -> list[Detection]: ...


class Sam3Detector:
    """Real SAM3 wrapper, via Ultralytics' SAM3SemanticPredictor.

    Confirmed 2026-09-12 against docs.ultralytics.com/models/sam-3 (see
    docs/decision_log.md for the full note) — requires `ultralytics>=8.3.237`.

    IMPORTANT — the weights are access-gated: request approval at
    https://huggingface.co/facebook/sam3 (Meta reviews the request; not
    instant), download the approved `sam3.pt`, and pass its path as
    `checkpoint`. Do this as early as possible — don't wait until this
    class is actually needed (Day 3-4) to discover approval is slow.

    Not smoke-tested yet (no GPU locally) — run it once on a single real
    frame on Colab before trusting it at scale; the exact `set_image`/
    `predictor(text=...)` call shape may need a small adjustment against
    whatever `ultralytics` version actually installs.

    `imgsz` default raised to 1920 for the same reason as `YoloWorldDetector`
    below — most source video is 4K and the default 640 would shrink small
    people below what the network can represent.
    """

    def __init__(
        self,
        checkpoint: str = "sam3.pt",
        device: str = "cuda",
        conf: float = 0.25,
        imgsz: int = 1920,
    ) -> None:
        from ultralytics.models.sam import SAM3SemanticPredictor

        overrides = {
            "conf": conf,
            "imgsz": imgsz,
            "task": "segment",
            "mode": "predict",
            "model": checkpoint,
            "save": False,
            "device": device,
        }
        self._predictor = SAM3SemanticPredictor(overrides=overrides)

    def detect(self, image: np.ndarray, prompt: str) -> list[Detection]:
        self._predictor.set_image(image)
        result = self._predictor(text=[prompt])[0]
        boxes_xyxy = result.boxes.xyxy.tolist()
        scores = result.boxes.conf.tolist()
        return [
            Detection(bbox_xywh=(x1, y1, x2 - x1, y2 - y1), score=float(score))
            for (x1, y1, x2, y2), score in zip(boxes_xyxy, scores)
        ]


class YoloWorldDetector:
    """Fallback text-promptable detector if SAM3 access isn't granted in time.

    SAM2 is NOT a substitute here despite earlier plans saying "fall back
    to SAM2" — confirmed 2026-09-12 that SAM2 has no text/open-vocabulary
    prompting at all, it only refines a given point/box/mask prompt
    (Ultralytics' own docs pair it with a YOLO detector for exactly this
    reason). YOLO-World is genuinely text-promptable and gives boxes
    directly, and we already depend on `ultralytics` for YOLO26s, so this
    adds no new dependency.

    Not smoke-tested yet — verify `model.set_classes([prompt])` +
    `model.predict(image)` against the installed `ultralytics` version on
    Colab before trusting it at scale.

    `imgsz` matters a lot here: most of our source video is 4K
    (3840x2160), and Ultralytics' default inference size (640) would
    shrink it by ~6x before the model ever sees it — a 40x80px person
    becomes ~7x13px, likely below what the network can represent at all.
    Default raised to 1920 (2026-09-12) for this reason; a more thorough
    fix (SAHI-style tiled inference) is deferred to the dedicated
    YOLO26s+SAHI experiment (Tier 1, item 1) rather than built into this
    generic labeling tool.
    """

    def __init__(
        self,
        checkpoint: str = "yolov8s-worldv2.pt",
        conf: float = 0.25,
        imgsz: int = 1920,
    ) -> None:
        from ultralytics import YOLOWorld

        self._model = YOLOWorld(checkpoint)
        self._conf = conf
        self._imgsz = imgsz
        self._last_prompt: str | None = None

    def detect(self, image: np.ndarray, prompt: str) -> list[Detection]:
        if prompt != self._last_prompt:
            self._model.set_classes([prompt])
            self._last_prompt = prompt
        result = self._model.predict(
            image, conf=self._conf, imgsz=self._imgsz, verbose=False
        )[0]
        boxes_xyxy = result.boxes.xyxy.tolist()
        scores = result.boxes.conf.tolist()
        return [
            Detection(bbox_xywh=(x1, y1, x2 - x1, y2 - y1), score=float(score))
            for (x1, y1, x2, y2), score in zip(boxes_xyxy, scores)
        ]


class MockDetector:
    """Deterministic stand-in for local pipeline testing (no GPU needed).

    Returns a single fixed-size box in the center of the image with a
    constant score, regardless of `prompt`. Only exists to exercise
    sample_diverse_frames -> detect -> COCO/review-image plumbing before
    Sam3Detector is filled in.
    """

    def __init__(self, score: float = 0.9) -> None:
        self.score = score

    def detect(self, image: np.ndarray, prompt: str) -> list[Detection]:
        h, w = image.shape[:2]
        box_w, box_h = w * 0.1, h * 0.2
        x, y = (w - box_w) / 2, (h - box_h) / 2
        return [Detection(bbox_xywh=(x, y, box_w, box_h), score=self.score)]
