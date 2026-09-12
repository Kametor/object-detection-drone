"""Build the dataset overview table for the presentation.

Joins the automatic per-video inventory (results/inventory/video_inventory.csv,
from scripts/01_inventory.py) with the manual visual-triage notes
(docs/video_notes.csv) and the split assignment (data/splits/*.txt) into a
single table: results/dataset_overview/table.csv (+ a markdown rendering
for pasting into the presentation).

Usage:
    .venv/bin/python scripts/03_dataset_overview.py --config configs/03_dataset_overview.yaml
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


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


def load_csv(path: Path) -> dict[str, dict]:
    with path.open(newline="") as f:
        return {row["video" if "video" in row else "file"]: row for row in csv.DictReader(f)}


def load_split_assignment(splits_dir: Path) -> dict[str, str]:
    assignment = {}
    for split_name in ("train", "val", "test", "background"):
        split_file = splits_dir / f"{split_name}.txt"
        for video_name in split_file.read_text().splitlines():
            video_name = video_name.strip()
            if video_name:
                assignment[video_name] = split_name
    return assignment


def build_rows(inventory: dict, notes: dict, split_assignment: dict) -> list[dict]:
    rows = []
    for video_name, inv in inventory.items():
        note = notes.get(video_name, {})
        rows.append(
            {
                "video": video_name,
                "split": split_assignment.get(video_name, "unassigned"),
                "duration_s": inv["duration_s"],
                "resolution": f"{inv['width']}x{inv['height']}",
                "fps": inv["fps"],
                "contains_person": note.get("contains_person", "unknown"),
                "person_size": note.get("person_size", "-"),
                "other_objects": note.get("other_objects", "-"),
                "background_type": note.get("background_type", "-"),
                "occlusion": note.get("occlusion", "-"),
                "notes": note.get("notes", ""),
            }
        )
    rows.sort(key=lambda r: (r["split"], r["video"]))
    return rows


def write_markdown(rows: list[dict], path: Path) -> None:
    headers = list(rows[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())

    inventory = load_csv(Path(config["inventory_csv"]))
    notes = load_csv(Path(config["notes_csv"]))
    split_assignment = load_split_assignment(Path(config["splits_dir"]))

    rows = build_rows(inventory, notes, split_assignment)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "table.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = output_dir / "table.md"
    write_markdown(rows, md_path)

    print(f"Written: {csv_path}")
    print(f"Written: {md_path}")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "03_dataset_overview.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config.get("seed"),
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_videos": len(rows),
    }
    manifest_path = manifest_dir / f"03_dataset_overview_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
