"""Export one video's pseudo-labels as a CVAT-importable pre-annotation set.

Used when the pseudo-label audit finds a systematic teacher failure worth
correcting by hand instead of discarding (e.g. SAM3 boxing sled dogs as
people in DJI_0790). Writes a flat folder of that video's frames plus a
COCO file whose `file_name` values match those frames exactly, which is
what CVAT's COCO 1.0 importer needs to attach boxes to images.

Usage:
    .venv/bin/python scripts/11_export_for_cvat.py --video DJI_0790 --config configs/11_export_for_cvat.yaml
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, required=True, help="video stem, e.g. DJI_0790")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    frames_dir = Path(config["frames_dir"]) / args.video
    annotations_path = Path(config["annotations_dir"]) / f"{args.video}.json"
    output_dir = Path(config["output_dir"]) / args.video
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    coco = json.loads(annotations_path.read_text())

    # CVAT matches annotations to uploaded images by file_name, so strip the
    # "<video>/" prefix our pipeline uses internally down to the bare name.
    images = []
    for image in coco["images"]:
        bare_name = Path(image["file_name"]).name
        shutil.copy2(frames_dir / bare_name, images_dir / bare_name)
        images.append({
            "id": image["id"],
            "file_name": bare_name,
            "width": image["width"],
            "height": image["height"],
            "license": 0,
            "flickr_url": "",
            "coco_url": "",
            "date_captured": 0,
        })

    # Drop `score`: these are being handed over as annotations to correct,
    # not as predictions, and CVAT has no notion of a confidence field.
    annotations = [
        {
            "id": ann["id"],
            "image_id": ann["image_id"],
            "category_id": ann["category_id"],
            "segmentation": [],
            "area": ann["area"],
            "bbox": ann["bbox"],
            "iscrowd": 0,
        }
        for ann in coco["annotations"]
    ]

    out_json = output_dir / "instances_default.json"
    out_json.write_text(json.dumps({
        "licenses": [{"id": 0, "name": "", "url": ""}],
        "info": {"description": f"SAM3 pseudo-labels for {args.video}, for manual correction"},
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "person", "supercategory": ""}],
    }, indent=2))

    print(f"{len(images)} frames -> {images_dir}/")
    print(f"{len(annotations)} boxes -> {out_json}")


if __name__ == "__main__":
    main()
