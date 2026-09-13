"""Ultralytics RT-DETR (HGNetv2 backbone) zero-shot sanity check.

A second RT-DETR data point alongside scripts/28's HF R18 checkpoint —
same purpose (measure the domain gap, no training), different backbone
size. See src/methods/rtdetr/ultralytics_model.py.

`frames_per_video` (optional, in the config) caps how many frames per
video are processed — for a fast preview run before committing to the
full test set.

Usage:
    .venv/bin/python scripts/30_rtdetr_ultralytics_zeroshot_eval.py --config configs/30_rtdetr_ultralytics_zeroshot.yaml
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

from src.methods.rtdetr.ultralytics_model import RtDetrUltralyticsDetector  # noqa: E402
from src.methods.sam3_zeroshot.pipeline import draw_detections  # noqa: E402


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
    frames_per_video = config.get("frames_per_video")  # None = all frames

    detector = RtDetrUltralyticsDetector(
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

        frame_paths = sorted(video_dir.glob("*.jpg"))
        if frames_per_video is not None:
            frame_paths = frame_paths[:frames_per_video]

        video_start = time.time()
        for i, frame_path in enumerate(frame_paths, start=1):
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

            print(f"  {video_dir.name} [{i}/{len(frame_paths)}] {frame_path.name}: {len(detections)} boxes", flush=True)

        video_elapsed = time.time() - video_start
        print(f"{video_dir.name}: done ({len(frame_paths)} frames, {video_elapsed:.1f}s)", flush=True)

    elapsed = time.time() - start
    predictions = {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "person"}],
    }
    predictions_path = output_dir / "predictions.json"
    predictions_path.write_text(json.dumps(predictions, indent=2))

    print(f"\n{len(images)} frames, {len(annotations)} boxes, {elapsed:.1f}s total ({elapsed / max(len(images), 1):.2f}s/frame)", flush=True)
    print(f"Written: {predictions_path}", flush=True)
    print(f"Written: {review_dir}/", flush=True)

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "30_rtdetr_ultralytics_zeroshot_eval.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frames_per_video": frames_per_video,
        "num_frames": len(images),
        "num_boxes": len(annotations),
        "elapsed_seconds": round(elapsed, 1),
    }
    manifest_path = manifest_dir / f"30_rtdetr_ultralytics_zeroshot_eval_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
