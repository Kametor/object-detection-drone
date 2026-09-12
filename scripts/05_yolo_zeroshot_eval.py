"""YOLO26n zero-shot (COCO-pretrained) sanity check on the gold test set.

Runs entirely on CPU, locally (no Colab/GPU needed) — YOLO26 nano is fast
enough on the M1 for a one-off 151-image pass. This is the "measuring
stick" step: how much does the domain gap (nadir view, small objects)
hurt a detector that already knows the "person" class perfectly well in
ordinary photos?

Usage:
    .venv/bin/python scripts/05_yolo_zeroshot_eval.py --config configs/05_yolo_zeroshot.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.methods.sam3_zeroshot.pipeline import draw_detections  # noqa: E402
from src.methods.yolo.model import Yolo26Detector  # noqa: E402


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1]
        ).decode().strip()
    except Exception:
        return "unknown"


def config_hash(config: dict) -> str:
    payload = json.dumps(config, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["conf"], imgsz=config["imgsz"]
    )

    frames_dir = Path(config["frames_dir"])
    output_dir = Path(config["output_dir"])
    review_dir = output_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    images = []
    annotations = []
    annotation_id = 1
    image_id = 1
    start = time.time()

    for video_dir in sorted(frames_dir.iterdir()):
        if not video_dir.is_dir():
            continue
        safe_name = video_dir.name.replace(" ", "_")
        video_review_dir = review_dir / video_dir.name
        video_review_dir.mkdir(parents=True, exist_ok=True)

        for frame_path in sorted(video_dir.glob("*.jpg")):
            image = cv2.imread(str(frame_path))
            h, w = image.shape[:2]
            detections = detector.detect(image)

            file_name = f"{safe_name}__{frame_path.name}"
            images.append({"id": image_id, "file_name": file_name, "width": w, "height": h})
            for det in detections:
                annotations.append(
                    {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": 1,
                        "bbox": list(det.bbox_xywh),
                        "score": det.score,
                        "area": det.bbox_xywh[2] * det.bbox_xywh[3],
                        "iscrowd": 0,
                    }
                )
                annotation_id += 1
            image_id += 1

            annotated = draw_detections(image, detections)
            cv2.imwrite(str(video_review_dir / frame_path.name), annotated, [cv2.IMWRITE_JPEG_QUALITY, config["jpeg_quality"]])

        print(f"{video_dir.name}: done")

    elapsed = time.time() - start
    predictions = {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "person"}],
    }
    predictions_path = output_dir / "predictions.json"
    predictions_path.write_text(json.dumps(predictions, indent=2))

    print(f"\n{len(images)} frames, {len(annotations)} boxes, {elapsed:.1f}s total ({elapsed / max(len(images), 1):.2f}s/frame)")
    print(f"Written: {predictions_path}")
    print(f"Written: {review_dir}/")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "05_yolo_zeroshot_eval.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_frames": len(images),
        "num_boxes": len(annotations),
        "elapsed_seconds": round(elapsed, 1),
    }
    manifest_path = manifest_dir / f"05_yolo_zeroshot_eval_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
