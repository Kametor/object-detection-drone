"""Mine verifier training crops from the train+val splits (item 1b).

Runs YOLO at the cascade's low confidence over train+val frames, matches
each proposed box against that frame's SAM3 pseudo-labels, and writes
person / not_person crops. The test split is never touched — the
verifier must not see it.

Candidates whose IoU falls between the negative and positive thresholds
are discarded rather than labeled: on train/val the reference boxes are
a model's output, so the ambiguous middle is where the teacher's own
mistakes live.

Usage:
    .venv/bin/python scripts/09_build_crop_dataset.py --config configs/09_build_crop_dataset.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.metrics import _iou_xywh  # noqa: E402
from src.methods.yolo.cascade import crop_candidate, label_candidate  # noqa: E402
from src.methods.yolo.model import Yolo26Detector  # noqa: E402


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1]
        ).decode().strip()
    except Exception:
        return "unknown"


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]


def load_reference_boxes(annotations_path: Path) -> dict[str, list[list[float]]]:
    coco = json.loads(annotations_path.read_text())
    id_to_file = {im["id"]: im["file_name"] for im in coco["images"]}
    references: dict[str, list[list[float]]] = {}
    for ann in coco["annotations"]:
        references.setdefault(id_to_file[ann["image_id"]], []).append(ann["bbox"])
    return references


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--only-video",
        type=str,
        default=None,
        help="re-mine a single video (by stem) instead of all — used after "
             "correcting one video's pseudo-labels",
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    splits_dir = Path(config["splits_dir"])
    frames_root = Path(config["frames_dir"])
    annotations_root = Path(config["annotations_dir"])
    output_root = Path(config["output_dir"])

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["conf"], imgsz=config["imgsz"]
    )

    counts: Counter[str] = Counter()
    for split in ("train", "val"):
        videos = [
            v.strip()
            for v in (splits_dir / f"{split}.txt").read_text().splitlines()
            if v.strip()
        ]
        for video in videos:
            stem = Path(video).stem
            if args.only_video and stem != args.only_video:
                continue
            if args.only_video:
                # re-mining after a label correction: a candidate that used
                # to land in one class can move to the other, but we only
                # ever write new files, never delete — clear this video's
                # old crops first or a stale file lingers in the wrong class.
                for stale in output_root.glob(f"{split}/*/{stem}__*.jpg"):
                    stale.unlink()
            annotations_path = annotations_root / f"{stem}.json"
            if not annotations_path.exists():
                print(f"  [skip] no pseudo-labels for {stem}")
                continue
            references = load_reference_boxes(annotations_path)

            for frame_path in sorted((frames_root / stem).glob("*.jpg")):
                key = f"{stem}/{frame_path.name}"
                image = cv2.imread(str(frame_path))
                reference_boxes = references.get(key, [])

                for index, detection in enumerate(detector.detect(image)):
                    max_iou = max(
                        (_iou_xywh(list(detection.bbox_xywh), r) for r in reference_boxes),
                        default=0.0,
                    )
                    label = label_candidate(
                        max_iou, config["positive_iou"], config["negative_iou"]
                    )
                    if label is None:
                        counts[f"{split}/ignored"] += 1
                        continue

                    crop = crop_candidate(
                        image, detection.bbox_xywh, config["padding_ratio"], config["crop_size"]
                    )
                    if crop is None:
                        counts[f"{split}/degenerate"] += 1
                        continue

                    out_dir = output_root / split / label
                    out_dir.mkdir(parents=True, exist_ok=True)
                    name = f"{stem.replace(' ', '_')}__{frame_path.stem}__{index:02d}.jpg"
                    cv2.imwrite(str(out_dir / name), crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    counts[f"{split}/{label}"] += 1

            print(f"[{split}] {stem}: done")

    print("\n=== crop dataset ===")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "script": "09_build_crop_dataset.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "counts": dict(counts),
    }
    manifest_path = (
        manifest_dir / f"09_build_crop_dataset_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWritten: {output_root}/")
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
