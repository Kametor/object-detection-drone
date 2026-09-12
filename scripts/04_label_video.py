"""End-to-end auto-labeling tool: video + prompt + Hz -> boxes + review images.

This is the single tool used both for our own train/val pseudo-labeling
(and background-video verification) and as the reviewer-facing "upload your
own video" demo — same code path either way.

Usage:
    .venv/bin/python scripts/04_label_video.py \\
        --video "data/raw/drone_videos/Berghouse Leopard Jog.mp4" \\
        --prompt person --fps 3.0 --config configs/04_label_video.yaml

    # A reviewer's own video works the same way:
    .venv/bin/python scripts/04_label_video.py \\
        --video /path/to/their_video.mp4 --prompt "person" --fps 2.0 \\
        --config configs/04_label_video.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.methods.sam3_zeroshot.model import MockDetector  # noqa: E402
from src.methods.sam3_zeroshot.pipeline import draw_detections, label_video, to_coco  # noqa: E402


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


def build_detector(model_config: dict):
    name = model_config["name"]
    imgsz = model_config.get("imgsz", 1920)
    if name == "mock":
        return MockDetector()
    if name == "sam3":
        from src.methods.sam3_zeroshot.model import Sam3Detector

        return Sam3Detector(
            checkpoint=model_config["checkpoint"], device=model_config["device"], imgsz=imgsz
        )
    if name == "yolo_world":
        from src.methods.sam3_zeroshot.model import YoloWorldDetector

        return YoloWorldDetector(checkpoint=model_config["checkpoint"], imgsz=imgsz)
    raise ValueError(f"unknown model name: {name}")


def check_not_test_video(video_path: Path, splits_dir: str, force: bool) -> None:
    if not splits_dir:
        return
    test_file = Path(splits_dir) / "test.txt"
    if not test_file.exists():
        return
    test_videos = {line.strip() for line in test_file.read_text().splitlines() if line.strip()}
    if video_path.name in test_videos and not force:
        raise SystemExit(
            f"Refusing to run: '{video_path.name}' is in {test_file} (the gold test "
            "set). SAM3 must never touch test videos (Non-negotiable rule 2). "
            "Pass --force only if you are certain this is intentional."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())
    check_not_test_video(args.video, config["splits_dir"], args.force)

    detector = build_detector(config["model"])
    labeled_frames = label_video(
        video_path=args.video,
        prompt=args.prompt,
        fps=args.fps,
        detector=detector,
        dedup_threshold=config["dedup_threshold"],
        max_gap_seconds=config["max_gap_seconds"],
        confidence_threshold=config["confidence_threshold"],
    )
    print(f"Labeled {len(labeled_frames)} frames from '{args.video.name}' (prompt='{args.prompt}')")

    output_dir = Path(config["output_dir"])
    video_stem = args.video.stem
    frames_dir = output_dir / "frames" / video_stem
    review_dir = output_dir / "review" / video_stem
    frames_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    jpeg_quality = config["jpeg_quality"]
    for frame in labeled_frames:
        frame_name = f"frame_{frame.frame_idx:06d}.jpg"
        cv2.imwrite(str(frames_dir / frame_name), frame.image, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        annotated = draw_detections(frame.image, frame.detections)
        cv2.imwrite(str(review_dir / frame_name), annotated, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])

    coco = to_coco(labeled_frames, video_name=args.video.name, category_name=args.prompt)
    annotations_dir = output_dir / "annotations"
    annotations_dir.mkdir(parents=True, exist_ok=True)
    coco_path = annotations_dir / f"{video_stem}.json"
    coco_path.write_text(json.dumps(coco, indent=2))
    print(f"Written: {coco_path} ({len(coco['annotations'])} boxes)")
    print(f"Written: {frames_dir}/ and {review_dir}/")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "04_label_video.py",
        "video": str(args.video),
        "prompt": args.prompt,
        "fps": args.fps,
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_frames": len(labeled_frames),
        "num_boxes": len(coco["annotations"]),
    }
    manifest_path = manifest_dir / f"04_label_video_{video_stem}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
