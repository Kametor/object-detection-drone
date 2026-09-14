"""Convert SAM3 pseudo-labels into a YOLO-format training dataset.

Tier 1 item 1's still-missing half: every YOLO result so far (Method 1,
the cascade) is built on the zero-shot COCO-pretrained checkpoint --
nothing has actually been trained on this project's own pseudo-labels
yet. This script builds the `ultralytics`-expected directory layout
(images/{train,val}, labels/{train,val}, data.yaml) from
results/pseudo_labels/annotations/*.json, so scripts/36 (Colab, GPU) can
just call `model.train(data=...)`.

Runs locally (file conversion only, no GPU) per CLAUDE.md Section 3.

Usage:
    .venv/bin/python scripts/35_export_yolo_training_data.py --config configs/35_export_yolo_training_data.yaml
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

PERSON_CLASS_ID = 0  # single-class dataset: class 0 = person


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1]
        ).decode().strip()
    except Exception:
        return "unknown"


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]


def write_split(
    videos: list[str],
    frames_dir: Path,
    annotations_dir: Path,
    images_out: Path,
    labels_out: Path,
    require_annotations: bool,
) -> tuple[int, int]:
    """Returns (num_images, num_boxes) written for this split."""
    images_out.mkdir(parents=True, exist_ok=True)
    labels_out.mkdir(parents=True, exist_ok=True)

    num_images = num_boxes = 0
    for video in videos:
        stem = Path(video).stem
        safe_stem = stem.replace(" ", "_")
        annotations_path = annotations_dir / f"{stem}.json"

        boxes_by_frame: dict[str, list[list[float]]] = {}
        if annotations_path.exists():
            coco = json.loads(annotations_path.read_text())
            id_to_name = {img["id"]: Path(img["file_name"]).name for img in coco["images"]}
            for ann in coco["annotations"]:
                boxes_by_frame.setdefault(id_to_name[ann["image_id"]], []).append(ann["bbox"])
        elif require_annotations:
            print(f"  [skip] no pseudo-labels for {stem}")
            continue
        # else: background video, intentionally no annotations file -> every frame gets an empty label

        video_frames_dir = frames_dir / stem
        if not video_frames_dir.exists():
            print(f"  [skip] no frames dir for {stem}")
            continue

        for frame_path in sorted(video_frames_dir.glob("*.jpg")):
            image = cv2.imread(str(frame_path))
            if image is None:
                continue
            h, w = image.shape[:2]

            out_name = f"{safe_stem}__{frame_path.stem}"
            shutil.copy2(frame_path, images_out / f"{out_name}.jpg")

            lines = []
            for bx, by, bw, bh in boxes_by_frame.get(frame_path.name, []):
                cx, cy = (bx + bw / 2) / w, (by + bh / 2) / h
                nw, nh = bw / w, bh / h
                lines.append(f"{PERSON_CLASS_ID} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
                num_boxes += 1
            (labels_out / f"{out_name}.txt").write_text("\n".join(lines))
            num_images += 1

        print(f"  {stem}: {num_images} images so far")

    return num_images, num_boxes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    splits_dir = Path(config["splits_dir"])
    frames_dir = Path(config["frames_dir"])
    annotations_dir = Path(config["annotations_dir"])
    output_dir = Path(config["output_dir"])
    if output_dir.exists():
        shutil.rmtree(output_dir)  # stale files from a previous export would silently linger otherwise

    train_videos = [v.strip() for v in (splits_dir / "train.txt").read_text().splitlines() if v.strip()]
    val_videos = [v.strip() for v in (splits_dir / "val.txt").read_text().splitlines() if v.strip()]
    if config.get("include_background_in_train", False):
        background_videos = [v.strip() for v in (splits_dir / "background.txt").read_text().splitlines() if v.strip()]
        train_videos = train_videos + background_videos

    print("=== train ===")
    train_images, train_boxes = write_split(
        train_videos, frames_dir, annotations_dir,
        output_dir / "images" / "train", output_dir / "labels" / "train",
        require_annotations=False,
    )
    print("=== val ===")
    val_images, val_boxes = write_split(
        val_videos, frames_dir, annotations_dir,
        output_dir / "images" / "val", output_dir / "labels" / "val",
        require_annotations=True,
    )

    data_yaml = {
        "path": str(output_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "names": {PERSON_CLASS_ID: "person"},
    }
    (output_dir / "data.yaml").write_text(yaml.safe_dump(data_yaml, sort_keys=False))

    print(f"\ntrain: {train_images} images, {train_boxes} boxes")
    print(f"val:   {val_images} images, {val_boxes} boxes")
    print(f"Written: {output_dir}/data.yaml")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "script": "35_export_yolo_training_data.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "train_images": train_images,
        "train_boxes": train_boxes,
        "val_images": val_images,
        "val_boxes": val_boxes,
    }
    manifest_path = manifest_dir / f"35_export_yolo_training_data_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
