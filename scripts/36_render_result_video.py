"""Render the cascade's predictions on full test videos into one combined
demo video -- the assignment PDF's "sonuç videosu" (if available).

Reuses exactly the same detect-then-verify cascade as
scripts/25_cascade_score_fusion_eval.py (same checkpoints, same score
fusion sqrt(yolo_conf * verifier_prob)) -- this is not a new method or a
new run of the evaluated pipeline, only a different consumer of it:
instead of scoring against the gold test set's sampled frames, it runs
every frame of the original test videos and writes an annotated .mp4.

Boxes are only drawn at the cascade's own reported operating point
(draw_threshold, 0.38 by default -- see docs/decision_log.md) so what's
shown matches the numbers already reported, not a cherry-picked lower
threshold that looks fuller on video.

Usage:
    .venv/bin/python scripts/36_render_result_video.py --config configs/36_render_result_video.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
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


def letterbox(frame: np.ndarray, canvas_w: int, canvas_h: int) -> np.ndarray:
    """Resize `frame` to fit within (canvas_w, canvas_h), preserving aspect
    ratio, centered on a black canvas -- so videos of different native
    resolutions/aspect ratios can share one output video."""
    h, w = frame.shape[:2]
    scale = min(canvas_w / w, canvas_h / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    x0, y0 = (canvas_w - nw) // 2, (canvas_h - nh) // 2
    canvas[y0 : y0 + nh, x0 : x0 + nw] = resized
    return canvas


def cascade_detect(
    image: np.ndarray,
    detector: Yolo26Detector,
    verifier: torch.nn.Module,
    device: torch.device,
    high_conf: float,
    crop_size: int,
    padding_ratio: float,
) -> list[Detection]:
    """One frame through the cascade: YOLO's low-confidence candidates,
    fused with the verifier's opinion on everything below `high_conf`.
    Identical logic to scripts/25_cascade_score_fusion_eval.py."""
    kept: list[Detection] = []
    for det in detector.detect(image):
        if det.score >= high_conf:
            kept.append(det)
            continue
        crop = crop_candidate(image, det.bbox_xywh, padding_ratio, crop_size)
        if crop is None:
            continue
        tensor = crop_to_tensor(crop).unsqueeze(0).to(device)
        with torch.no_grad():
            probs = torch.softmax(verifier(tensor), dim=1)[0]
        person_prob = float(probs[PERSON_INDEX])
        fused_score = math.sqrt(det.score * person_prob)
        kept.append(Detection(bbox_xywh=det.bbox_xywh, score=fused_score))
    return kept


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())

    torch.manual_seed(config["seed"])
    device = torch.device(config["device"])
    high_conf = config["high_conf_threshold"]
    draw_threshold = config["draw_threshold"]
    frame_stride = config.get("frame_stride", 1)

    detector = Yolo26Detector(
        checkpoint=config["checkpoint"], conf=config["conf"], imgsz=config["imgsz"]
    )
    checkpoint = torch.load(config["verifier_checkpoint"], map_location=device)
    small_input_stem = checkpoint.get("config", {}).get("small_input_stem", False)
    architecture = checkpoint.get("config", {}).get("architecture", "resnet18")
    verifier = build_model(pretrained=False, small_input_stem=small_input_stem, architecture=architecture).to(device)
    verifier.load_state_dict(checkpoint["state_dict"])
    verifier.eval()

    canvas_w, canvas_h = config["canvas_width"], config["canvas_height"]
    output_path = Path(config["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = None  # opened once the first video tells us the real input fps

    total_frames_written = 0
    total_frames_read = 0
    per_video_counts = {}
    start = time.time()

    for video_path_str in config["videos"]:
        video_path = Path(video_path_str)
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video: {video_path}")
        input_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        output_fps = input_fps / frame_stride
        if writer is None:
            writer = cv2.VideoWriter(str(output_path), fourcc, output_fps, (canvas_w, canvas_h))
            first_output_fps = output_fps
        elif abs(output_fps - first_output_fps) > 0.5:
            print(f"Note: {video_path.name} native fps ({input_fps:.1f}) differs from the "
                  f"first video's output fps ({first_output_fps:.1f}) -- playback speed will "
                  f"drift slightly for this clip, not resampled to match.")

        label = video_path.stem
        frame_idx = 0
        written_this_video = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_idx += 1
            total_frames_read += 1
            if (frame_idx - 1) % frame_stride != 0:
                continue

            detections = cascade_detect(
                frame, detector, verifier, device, high_conf,
                config["crop_size"], config["padding_ratio"],
            )
            kept = [d for d in detections if d.score >= draw_threshold]
            annotated = draw_detections(frame, kept)
            cv2.putText(annotated, label, (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(annotated, label, (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (30, 30, 30), 1, cv2.LINE_AA)

            writer.write(letterbox(annotated, canvas_w, canvas_h))
            written_this_video += 1
            total_frames_written += 1

        cap.release()
        per_video_counts[video_path.name] = written_this_video
        print(f"{video_path.name}: {written_this_video} frames written")

    if writer is not None:
        writer.release()
    elapsed = time.time() - start

    print(f"\n{total_frames_written} frames written ({total_frames_read} read, stride={frame_stride}), "
          f"{elapsed:.1f}s total ({elapsed / max(total_frames_written, 1):.2f}s/frame)")
    print(f"Written: {output_path}")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "36_render_result_video.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "videos": config["videos"],
        "per_video_frames_written": per_video_counts,
        "total_frames_written": total_frames_written,
        "total_frames_read": total_frames_read,
        "frame_stride": frame_stride,
        "draw_threshold": draw_threshold,
        "elapsed_seconds": round(elapsed, 1),
        "output_path": str(output_path),
    }
    manifest_path = manifest_dir / f"36_render_result_video_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
