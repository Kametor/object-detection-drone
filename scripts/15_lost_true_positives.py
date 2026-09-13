"""Find the true positives the cascade verifier throws away.

The hybrid cascade (item 1b) rejects 71.9% of stage-1's low-confidence
candidates and, in the process, loses 247 of the 643 boxes stage 1 got
right (see docs/decision_log.md, 2026-09-13 3-way comparison). This finds
those specific boxes — a pool candidate that (a) matches a gold GT box at
IoU >= tp_iou_threshold and (b) has no near-identical box surviving in the
hybrid's kept predictions — and crops each one (same padding/size the
verifier itself saw) into output_dir for a Quick Look pass, to check the
leading hypothesis that these are test-video crops unlike anything in the
verifier's train/val distribution.

Usage:
    .venv/bin/python scripts/15_lost_true_positives.py --config configs/15_lost_true_positives.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.metrics import _iou_xywh  # noqa: E402
from src.methods.yolo.cascade import crop_candidate  # noqa: E402


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1]
        ).decode().strip()
    except Exception:
        return "unknown"


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]


def load_by_file_name(predictions_path: Path) -> dict[str, list[list[float]]]:
    """image file_name -> list of that image's predicted bboxes."""
    data = json.loads(predictions_path.read_text())
    id_to_name = {img["id"]: img["file_name"] for img in data["images"]}
    by_name: dict[str, list[list[float]]] = {}
    for ann in data["annotations"]:
        by_name.setdefault(id_to_name[ann["image_id"]], []).append(ann["bbox"])
    return by_name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    gt_data = json.loads(Path(config["gt_path"]).read_text())
    id_to_gt_name = {img["id"]: img["file_name"] for img in gt_data["images"]}
    gt_by_name: dict[str, list[list[float]]] = {}
    for ann in gt_data["annotations"]:
        gt_by_name.setdefault(id_to_gt_name[ann["image_id"]], []).append(ann["bbox"])

    pool_by_name = load_by_file_name(Path(config["pool_predictions"]))
    kept_by_name = load_by_file_name(Path(config["kept_predictions"]))

    output_dir = Path(config["output_dir"])
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    tp_iou = config["tp_iou_threshold"]
    same_box_iou = config["same_box_iou_threshold"]
    frames_dir = Path(config["frames_dir"])

    lost = 0
    for file_name, pool_boxes in pool_by_name.items():
        gt_boxes = gt_by_name.get(file_name, [])
        kept_boxes = kept_by_name.get(file_name, [])
        if not gt_boxes:
            continue

        for pool_box in pool_boxes:
            is_true_positive = any(_iou_xywh(pool_box, gt) >= tp_iou for gt in gt_boxes)
            if not is_true_positive:
                continue
            survives = any(_iou_xywh(pool_box, kept) >= same_box_iou for kept in kept_boxes)
            if survives:
                continue

            # e.g. "DJI_0501__frame_000040.jpg" -> video dir "DJI_0501", frame file
            video, frame_name = file_name.split("__", 1)
            frame_path = frames_dir / video / frame_name
            image = cv2.imread(str(frame_path))
            if image is None:
                print(f"  [skip] can't read {frame_path}")
                continue
            crop = crop_candidate(image, tuple(pool_box), config["padding_ratio"], config["crop_size"])
            if crop is None:
                continue
            lost += 1
            out_name = f"{video}__{Path(frame_name).stem}__{lost:03d}.jpg"
            cv2.imwrite(str(output_dir / out_name), crop, [cv2.IMWRITE_JPEG_QUALITY, 95])

    print(f"Lost true positives (stage 1 got it right, verifier rejected it): {lost}")
    print(f"Written: {output_dir}/")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "script": "15_lost_true_positives.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lost_true_positives": lost,
    }
    manifest_path = manifest_dir / f"15_lost_true_positives_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
