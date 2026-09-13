"""Pick the cascade's low confidence threshold, on val, with evidence.

Item 1b runs YOLO at a deliberately low confidence so the verifier has
candidates to work with. Rather than guessing that threshold, this runs
YOLO *once* at a very low floor, then reports what each candidate
threshold would have given: how many boxes, and what fraction of the
val set's known person boxes they cover.

"Known" here means the val split's SAM3 pseudo-labels — val has no human
ground truth by design (only the test split does), so recall is measured
against the teacher, not against truth. Good enough for choosing a knob;
not a result to report as accuracy.

Usage:
    .venv/bin/python scripts/08_threshold_sweep.py --config configs/08_threshold_sweep.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.metrics import _iou_xywh  # noqa: E402
from src.methods.yolo.model import Yolo26Detector  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    videos = [
        v.strip()
        for v in Path(config["splits_dir"], "val.txt").read_text().splitlines()
        if v.strip()
    ]
    frames_root = Path(config["frames_dir"])
    annotations_root = Path(config["annotations_dir"])

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["floor_conf"], imgsz=config["imgsz"]
    )

    # frame -> (candidate boxes with scores, reference boxes)
    candidates: dict[str, list[tuple[list[float], float]]] = {}
    references: dict[str, list[list[float]]] = {}

    for video in videos:
        stem = Path(video).stem
        coco = json.loads((annotations_root / f"{stem}.json").read_text())
        id_to_file = {im["id"]: im["file_name"] for im in coco["images"]}
        for ann in coco["annotations"]:
            references.setdefault(id_to_file[ann["image_id"]], []).append(ann["bbox"])

        for frame_path in sorted((frames_root / stem).glob("*.jpg")):
            key = f"{stem}/{frame_path.name}"
            image = cv2.imread(str(frame_path))
            detections = detector.detect(image)
            candidates[key] = [(d.bbox_xywh, d.score) for d in detections]
        print(f"{stem}: {len(candidates)} frames scanned")

    total_reference = sum(len(v) for v in references.values())
    iou_threshold = config["iou_threshold"]

    print(f"\nval reference boxes (SAM3 pseudo-labels): {total_reference}")
    print(f"\n{'conf':>6} | {'candidates':>10} | {'per frame':>9} | {'covered':>7} | {'recall':>6}")
    print("-" * 52)

    rows = []
    for conf in config["thresholds"]:
        n_candidates = 0
        covered = 0
        for key, reference_boxes in references.items():
            kept = [box for box, score in candidates.get(key, []) if score >= conf]
            n_candidates += len(kept)
            for reference in reference_boxes:
                if any(_iou_xywh(box, reference) >= iou_threshold for box in kept):
                    covered += 1
        # candidates on frames with no reference boxes still count toward the load
        for key, dets in candidates.items():
            if key not in references:
                n_candidates += sum(1 for _box, score in dets if score >= conf)

        recall = covered / total_reference if total_reference else 0.0
        per_frame = n_candidates / max(len(candidates), 1)
        rows.append(
            {
                "conf": conf,
                "candidates": n_candidates,
                "candidates_per_frame": round(per_frame, 2),
                "covered": covered,
                "recall": round(recall, 4),
            }
        )
        print(f"{conf:>6.2f} | {n_candidates:>10} | {per_frame:>9.2f} | {covered:>7} | {recall:>6.3f}")

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "val_threshold_sweep.json"
    json_path.write_text(
        json.dumps(
            {
                "reference": "SAM3 pseudo-labels on the val split",
                "total_reference_boxes": total_reference,
                "iou_threshold": iou_threshold,
                "imgsz": config["imgsz"],
                "rows": rows,
            },
            indent=2,
        )
    )

    md_path = output_dir / "val_threshold_sweep.md"
    lines = [
        "# Cascade threshold choice (val split)",
        "",
        f"YOLO26n @ imgsz={config['imgsz']}, one inference pass at conf>={config['floor_conf']}, "
        "then filtered per threshold.",
        "",
        f"Coverage is measured against the val split's **SAM3 pseudo-labels** "
        f"({total_reference} boxes) at IoU>={iou_threshold} — val has no human ground truth "
        "by design, so this is a knob-choosing proxy, not an accuracy result.",
        "",
        "| conf | candidates | per frame | covered | recall |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['conf']:.2f} | {row['candidates']} | {row['candidates_per_frame']} | "
            f"{row['covered']} | {row['recall']:.3f} |"
        )
    md_path.write_text("\n".join(lines) + "\n")

    print(f"\nWritten: {json_path}")
    print(f"Written: {md_path}")


if __name__ == "__main__":
    main()
