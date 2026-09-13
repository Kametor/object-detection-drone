"""Detect-then-verify cascade (item 1b), end to end, on the gold test set.

Stage 1: YOLO26n at a deliberately low confidence (high recall, many false
positives by design). Stage 2: every stage-1 box, cropped, goes through the
trained ResNet18 verifier; a box survives only if the verifier calls it
`person` — a plain binary accept/reject, not a re-weighted score sweep.
The kept boxes get the verifier's own person-probability as their score,
so downstream mAP/PR-curve code (which sweeps over `score`) has something
meaningful to sweep for this method specifically.

This and configs/05 (high-conf) / configs/13 (low-conf, no verifier) are
the three legs of the comparison: same YOLO26n zero-shot checkpoint
throughout, only the confidence floor and the verifier stage differ.

Usage:
    .venv/bin/python scripts/14_cascade_hybrid_eval.py --config configs/14_cascade_hybrid_eval.yaml
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
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.methods.sam3_zeroshot.pipeline import draw_detections  # noqa: E402
from src.methods.yolo.cascade import crop_candidate  # noqa: E402
from src.methods.yolo.model import Detection, Yolo26Detector  # noqa: E402
from src.methods.yolo.verifier import (  # noqa: E402
    PERSON_INDEX,
    build_model,
    crop_to_tensor,
)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1]
        ).decode().strip()
    except Exception:
        return "unknown"


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    torch.manual_seed(config["seed"])
    device = torch.device(config["device"])

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["conf"], imgsz=config["imgsz"]
    )

    checkpoint = torch.load(config["verifier_checkpoint"], map_location=device)
    small_input_stem = checkpoint.get("config", {}).get("small_input_stem", False)
    verifier = build_model(pretrained=False, small_input_stem=small_input_stem).to(device)
    verifier.load_state_dict(checkpoint["state_dict"])
    verifier.eval()

    frames_dir = Path(config["frames_dir"])
    output_dir = Path(config["output_dir"])
    review_dir = output_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    images, annotations = [], []
    annotation_id = image_id = 1
    stage1_total = stage2_kept = 0
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
            candidates = detector.detect(image)
            stage1_total += len(candidates)

            kept: list[Detection] = []
            for det in candidates:
                crop = crop_candidate(image, det.bbox_xywh, config["padding_ratio"], config["crop_size"])
                if crop is None:
                    continue
                tensor = crop_to_tensor(crop).unsqueeze(0).to(device)
                with torch.no_grad():
                    probs = torch.softmax(verifier(tensor), dim=1)[0]
                pred = int(probs.argmax())
                if pred != PERSON_INDEX:
                    continue  # verifier says not-person: dropped, never rescored
                kept.append(Detection(bbox_xywh=det.bbox_xywh, score=float(probs[PERSON_INDEX])))
            stage2_kept += len(kept)

            file_name = f"{safe_name}__{frame_path.name}"
            images.append({"id": image_id, "file_name": file_name, "width": w, "height": h})
            for det in kept:
                annotations.append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": list(det.bbox_xywh),
                    "score": det.score,
                    "area": det.bbox_xywh[2] * det.bbox_xywh[3],
                    "iscrowd": 0,
                })
                annotation_id += 1
            image_id += 1

            annotated = draw_detections(image, kept)
            cv2.imwrite(
                str(video_review_dir / frame_path.name), annotated,
                [cv2.IMWRITE_JPEG_QUALITY, config["jpeg_quality"]],
            )

        print(f"{video_dir.name}: done")

    elapsed = time.time() - start
    predictions = {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "person"}],
    }
    predictions_path = output_dir / "predictions.json"
    predictions_path.write_text(json.dumps(predictions, indent=2))

    reject_rate = 1 - (stage2_kept / stage1_total) if stage1_total else 0.0
    print(f"\nstage 1 (low-conf YOLO) candidates: {stage1_total}")
    print(f"stage 2 (verifier) kept: {stage2_kept} (rejected {reject_rate:.1%})")
    print(f"{len(images)} frames, {elapsed:.1f}s total ({elapsed / max(len(images), 1):.2f}s/frame)")
    print(f"Written: {predictions_path}")
    print(f"Written: {review_dir}/")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "14_cascade_hybrid_eval.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_frames": len(images),
        "stage1_candidates": stage1_total,
        "stage2_kept": stage2_kept,
        "elapsed_seconds": round(elapsed, 1),
    }
    manifest_path = manifest_dir / f"14_cascade_hybrid_eval_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
