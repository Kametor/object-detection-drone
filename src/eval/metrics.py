"""COCO-style detection metrics: mAP, per-video breakdown, PR operating point.

Uses pycocotools (the standard tool) for mAP/size-breakdown instead of a
hand-rolled implementation — reused by every method's evaluation, not
just this one.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

# COCOeval.summarize() computes these 12 stats in this fixed order.
STAT_NAMES = [
    "mAP@[.5:.95]", "mAP@.5", "mAP@.75", "mAP_small", "mAP_medium", "mAP_large",
    "AR@1", "AR@10", "AR@100", "AR_small", "AR_medium", "AR_large",
]


def _load_predictions_matched_to_gt(gt: COCO, predictions_path: Path) -> list[dict]:
    """Rewrite prediction image_ids to match `gt`'s ids, joined by file_name.

    Our various methods each assign their own sequential image ids when
    they run — only file_name is a stable join key back to the gold set.
    """
    raw = json.loads(predictions_path.read_text())
    file_name_to_gt_id = {img["file_name"]: img_id for img_id, img in gt.imgs.items()}
    pred_id_to_file_name = {img["id"]: img["file_name"] for img in raw["images"]}

    matched = []
    for ann in raw["annotations"]:
        file_name = pred_id_to_file_name[ann["image_id"]]
        gt_id = file_name_to_gt_id.get(file_name)
        if gt_id is None:
            continue  # prediction for an image not in the gold set — skip
        matched.append({**ann, "image_id": gt_id})
    return matched


def _run_cocoeval(gt: COCO, predictions: list[dict], img_ids: list[int] | None = None) -> dict:
    if not predictions:
        return {name: 0.0 for name in STAT_NAMES}
    with contextlib.redirect_stdout(io.StringIO()):
        dt = gt.loadRes(predictions)
        ev = COCOeval(gt, dt, iouType="bbox")
        if img_ids is not None:
            ev.params.imgIds = img_ids
        ev.evaluate()
        ev.accumulate()
        ev.summarize()
    return dict(zip(STAT_NAMES, (float(s) for s in ev.stats)))


def evaluate(gt_path: Path, predictions_path: Path) -> dict:
    """Overall mAP + COCO's size breakdown (small/medium/large area bins)."""
    with contextlib.redirect_stdout(io.StringIO()):
        gt = COCO(str(gt_path))
    predictions = _load_predictions_matched_to_gt(gt, predictions_path)
    return _run_cocoeval(gt, predictions)


def evaluate_per_video(gt_path: Path, predictions_path: Path) -> dict[str, dict]:
    """Same metrics, computed separately per source video/condition."""
    with contextlib.redirect_stdout(io.StringIO()):
        gt = COCO(str(gt_path))
    predictions = _load_predictions_matched_to_gt(gt, predictions_path)

    videos: dict[str, list[int]] = {}
    for img_id, img in gt.imgs.items():
        video = img["file_name"].split("__")[0]
        videos.setdefault(video, []).append(img_id)

    return {
        video: _run_cocoeval(gt, predictions, img_ids=ids)
        for video, ids in sorted(videos.items())
    }


def _iou_xywh(a: list[float], b: list[float]) -> float:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def precision_recall_f1(
    gt_path: Path,
    predictions_path: Path,
    conf_threshold: float,
    iou_threshold: float = 0.5,
) -> dict:
    """Single operating-point precision/recall/F1 via greedy IoU matching.

    Distinct from mAP (which sweeps confidence internally) — this answers
    "if we actually deployed at this one confidence threshold, how many
    of its detections would be right, and how many real people would it
    catch?"
    """
    gt_data = json.loads(gt_path.read_text())
    pred_data = json.loads(predictions_path.read_text())

    file_name_to_gt_id = {img["file_name"]: img["id"] for img in gt_data["images"]}
    pred_id_to_file_name = {img["id"]: img["file_name"] for img in pred_data["images"]}

    gt_by_image: dict[int, list[list[float]]] = {}
    for ann in gt_data["annotations"]:
        gt_by_image.setdefault(ann["image_id"], []).append(ann["bbox"])

    pred_by_image: dict[int, list[tuple[list[float], float]]] = {}
    for ann in pred_data["annotations"]:
        if ann["score"] < conf_threshold:
            continue
        file_name = pred_id_to_file_name[ann["image_id"]]
        gt_image_id = file_name_to_gt_id.get(file_name)
        if gt_image_id is None:
            continue
        pred_by_image.setdefault(gt_image_id, []).append((ann["bbox"], ann["score"]))

    tp = fp = fn = 0
    for image_id in file_name_to_gt_id.values():
        gt_boxes = gt_by_image.get(image_id, [])
        preds = sorted(pred_by_image.get(image_id, []), key=lambda p: -p[1])
        matched_gt = [False] * len(gt_boxes)
        for box, _score in preds:
            best_iou, best_j = 0.0, -1
            for j, gt_box in enumerate(gt_boxes):
                if matched_gt[j]:
                    continue
                iou = _iou_xywh(box, gt_box)
                if iou > best_iou:
                    best_iou, best_j = iou, j
            if best_iou >= iou_threshold:
                matched_gt[best_j] = True
                tp += 1
            else:
                fp += 1
        fn += matched_gt.count(False)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "confidence_threshold": conf_threshold,
        "iou_threshold": iou_threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
