"""Inventory raw videos: duration, resolution, fps, frame count.

Usage:
    .venv/bin/python scripts/01_inventory.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import cv2

RAW_DIR = Path("data/raw/drone_videos")
OUT_CSV = Path("results/inventory/video_inventory.csv")
VIDEO_EXTS = {".mp4", ".mov"}


def inspect_video(path: Path) -> dict:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"file": path.name, "error": "could not open"}
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_s = frame_count / fps if fps else 0.0
    cap.release()
    return {
        "file": path.name,
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "duration_s": round(duration_s, 1),
        "size_mb": round(path.stat().st_size / 1024 / 1024, 1),
        "has_srt": path.with_suffix(".SRT").exists() or path.with_suffix(".srt").exists(),
    }


def main() -> None:
    videos = sorted(p for p in RAW_DIR.iterdir() if p.suffix.lower() in VIDEO_EXTS)
    rows = [inspect_video(p) for p in videos]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total_duration = sum(r.get("duration_s", 0) for r in rows)
    print(f"{len(rows)} videos, {total_duration/60:.1f} min total")
    for r in rows:
        print(
            f"  {r['file']:<32} {r['width']}x{r['height']:<6} "
            f"{r['fps']:>6.2f}fps  {r['duration_s']:>7.1f}s  "
            f"{r['size_mb']:>7.1f}MB  srt={r['has_srt']}"
        )
    print(f"\nWritten: {OUT_CSV}")


if __name__ == "__main__":
    main()
