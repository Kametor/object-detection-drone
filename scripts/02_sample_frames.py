"""Sample temporally-diverse frames from each video in each split.

Reads data/splits/{train,val,test,background}.txt, samples frames per the
per-split parameters in the config, writes JPEGs to
data/processed/frames/<split>/<video_stem>/frame_<idx>.jpg, and writes a
CSV manifest plus a run manifest (config hash, seed, git SHA, timestamp)
into results/.

Usage:
    .venv/bin/python scripts/02_sample_frames.py --config configs/02_sample_frames.yaml
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.sampling import sample_diverse_frames  # noqa: E402


def load_split(splits_dir: Path, split_name: str) -> list[str]:
    path = splits_dir / f"{split_name}.txt"
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


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


def process_video(
    video_path: Path,
    split_name: str,
    output_dir: Path,
    params: dict,
    jpeg_quality: int,
) -> list[dict]:
    frames = sample_diverse_frames(
        video_path=video_path,
        fps=params["fps"],
        dedup_threshold=params["dedup_threshold"],
        max_gap_seconds=params["max_gap_seconds"],
    )

    video_out_dir = output_dir / split_name / video_path.stem
    video_out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    rows = []
    for sampled in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, sampled.frame_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        out_path = video_out_dir / f"frame_{sampled.frame_idx:06d}.jpg"
        cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        rows.append(
            {
                "split": split_name,
                "video": video_path.name,
                "frame_idx": sampled.frame_idx,
                "timestamp_s": round(sampled.timestamp_s, 3),
                "output_path": str(out_path.relative_to(output_dir.parent.parent)),
            }
        )
    cap.release()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())

    raw_video_dir = Path(config["raw_video_dir"])
    splits_dir = Path(config["splits_dir"])
    output_dir = Path(config["output_dir"])
    manifest_dir = Path(config["manifest_dir"])
    jpeg_quality = config["jpeg_quality"]

    all_rows = []
    for split_name, params in config["splits"].items():
        videos = load_split(splits_dir, split_name)
        for video_name in videos:
            video_path = raw_video_dir / video_name
            print(f"[{split_name}] sampling {video_name} (fps={params['fps']})...")
            rows = process_video(video_path, split_name, output_dir, params, jpeg_quality)
            print(f"  -> {len(rows)} frames kept")
            all_rows.extend(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_csv = output_dir / "manifest.csv"
    with manifest_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWritten: {manifest_csv} ({len(all_rows)} frames total)")

    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "02_sample_frames.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_frames": len(all_rows),
        "frames_per_split": {
            split: sum(1 for r in all_rows if r["split"] == split)
            for split in config["splits"]
        },
    }
    run_manifest_path = manifest_dir / f"02_sample_frames_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    run_manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {run_manifest_path}")


if __name__ == "__main__":
    main()
