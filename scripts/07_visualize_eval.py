"""Sample a few frames per test video and draw GT vs. predictions together.

For the presentation's qualitative comparison — not every frame, just a
representative sample per video.

Usage:
    .venv/bin/python scripts/07_visualize_eval.py \\
        --predictions results/yolo26_zeroshot/predictions.json \\
        --method-name yolo26n_zeroshot \\
        --frames-dir data/processed/frames/test \\
        --samples-per-video 5 \\
        --config configs/06_evaluate.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.visualize import draw_comparison  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--method-name", type=str, required=True)
    parser.add_argument("--frames-dir", type=Path, required=True)
    parser.add_argument("--samples-per-video", type=int, default=5)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())
    gt_data = json.loads(Path(config["gt_path"]).read_text())
    pred_data = json.loads(args.predictions.read_text())

    gt_by_file: dict[str, list[list[float]]] = {}
    gt_image_by_file = {im["file_name"]: im for im in gt_data["images"]}
    gt_id_to_file = {im["id"]: im["file_name"] for im in gt_data["images"]}
    for ann in gt_data["annotations"]:
        file_name = gt_id_to_file[ann["image_id"]]
        gt_by_file.setdefault(file_name, []).append(ann["bbox"])

    pred_id_to_file = {im["id"]: im["file_name"] for im in pred_data["images"]}
    pred_by_file: dict[str, list[tuple[list[float], float]]] = {}
    for ann in pred_data["annotations"]:
        file_name = pred_id_to_file[ann["image_id"]]
        pred_by_file.setdefault(file_name, []).append((ann["bbox"], ann["score"]))

    output_dir = Path(config["output_dir"]) / args.method_name / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    # group gt file_names by video (the "<video>__frame_X.jpg" convention)
    by_video: dict[str, list[str]] = {}
    for file_name in gt_image_by_file:
        video = file_name.split("__")[0]
        by_video.setdefault(video, []).append(file_name)

    for video, file_names in sorted(by_video.items()):
        file_names = sorted(file_names)
        n = min(args.samples_per_video, len(file_names))
        step = max(1, len(file_names) // n)
        sample = file_names[::step][:n]

        video_dir_name = video.replace("_", " ")
        for file_name in sample:
            frame_name = file_name.split("__", 1)[1]
            candidates = list(args.frames_dir.glob(f"*/{frame_name}"))
            image_path = next((p for p in candidates if p.parent.name.replace(" ", "_") == video), None)
            if image_path is None:
                print(f"  [skip] couldn't find source frame for {file_name}")
                continue
            image = cv2.imread(str(image_path))
            annotated = draw_comparison(
                image, gt_by_file.get(file_name, []), pred_by_file.get(file_name, [])
            )
            out_path = output_dir / file_name
            cv2.imwrite(str(out_path), annotated)
        print(f"{video}: wrote {len(sample)} comparison frames")

    print(f"\nWritten to: {output_dir}/")


if __name__ == "__main__":
    main()
