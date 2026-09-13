"""Size-gated cascade: verify small objects unconditionally, large ones by band.

Extends scripts/16's confidence-band gate with a second, independent gate
on box size. The user's diagnosis: YOLO already works on large objects, so
trusting it there at high confidence is fine (unchanged from scripts/16);
but it structurally cannot represent small objects at all (mAP_small was
exactly 0.0 for plain YOLO on the two hardest test videos -- see
docs/decision_log.md), so a small candidate's YOLO confidence is not a
trustworthy signal even when it happens to be high, and every small
candidate should go through the verifier.

Checked before building this (see decision_log.md, 2026-09-13): simply
*dropping* large+low-confidence candidates instead of verifying them, as
first proposed, would cost 75/719 gold GT boxes (10.4%) that are only ever
proposed that way -- so large objects keep scripts/16's original gate
(trust >= high_conf_threshold, verify the band below it) rather than a
harder cutoff.

Routing per candidate:
    area < small_area_threshold           -> verifier decides, always
    area >= small_area_threshold, score >= high_conf_threshold -> auto-accept
    area >= small_area_threshold, score <  high_conf_threshold -> verifier decides

Kept boxes always carry YOLO's own score, never the verifier's -- same
score-scale rationale as scripts/16.

Usage:
    .venv/bin/python scripts/22_cascade_size_gated_hybrid_eval.py --config configs/22_cascade_size_gated_hybrid_eval.yaml
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
    high_conf = config["high_conf_threshold"]
    small_area = config["small_area_threshold"]

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["conf"], imgsz=config["imgsz"]
    )

    checkpoint = torch.load(config["verifier_checkpoint"], map_location=device)
    small_input_stem = checkpoint.get("config", {}).get("small_input_stem", False)
    architecture = checkpoint.get("config", {}).get("architecture", "resnet18")
    verifier = build_model(pretrained=False, small_input_stem=small_input_stem, architecture=architecture).to(device)
    verifier.load_state_dict(checkpoint["state_dict"])
    verifier.eval()

    frames_dir = Path(config["frames_dir"])
    output_dir = Path(config["output_dir"])
    review_dir = output_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    images, annotations = [], []
    annotation_id = image_id = 1
    auto_accepted = verified_small = verified_large_band = verifier_kept = 0
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

            kept: list[Detection] = []
            for det in candidates:
                area = det.bbox_xywh[2] * det.bbox_xywh[3]
                is_small = area < small_area

                if not is_small and det.score >= high_conf:
                    auto_accepted += 1
                    kept.append(det)
                    continue

                if is_small:
                    verified_small += 1
                else:
                    verified_large_band += 1

                crop = crop_candidate(image, det.bbox_xywh, config["padding_ratio"], config["crop_size"])
                if crop is None:
                    continue
                tensor = crop_to_tensor(crop).unsqueeze(0).to(device)
                with torch.no_grad():
                    probs = torch.softmax(verifier(tensor), dim=1)[0]
                if int(probs.argmax()) != PERSON_INDEX:
                    continue
                verifier_kept += 1
                kept.append(det)  # keep YOLO's own score, not the verifier's

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

    print(f"\nauto-accepted (large, score >= {high_conf}): {auto_accepted}")
    print(f"verified (small, any score): {verified_small}")
    print(f"verified (large, band [conf, {high_conf})): {verified_large_band}")
    print(f"verifier kept: {verifier_kept}")
    print(f"total kept: {len(annotations)}")
    print(f"{len(images)} frames, {elapsed:.1f}s total ({elapsed / max(len(images), 1):.2f}s/frame)")
    print(f"Written: {predictions_path}")
    print(f"Written: {review_dir}/")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "22_cascade_size_gated_hybrid_eval.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_frames": len(images),
        "auto_accepted": auto_accepted,
        "verified_small": verified_small,
        "verified_large_band": verified_large_band,
        "verifier_kept": verifier_kept,
        "total_kept": len(annotations),
        "elapsed_seconds": round(elapsed, 1),
    }
    manifest_path = manifest_dir / f"22_cascade_size_gated_hybrid_eval_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
