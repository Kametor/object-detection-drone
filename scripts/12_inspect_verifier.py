"""Visually inspect the trained cascade verifier (item 1b) on val crops.

The val split's person/not_person labels are already known (mined by
09_build_crop_dataset.py against corrected pseudo-labels), so this just
runs the trained ResNet18 over them and copies every misclassified crop
into results/cascade_verifier/review/ for a Quick Look pass — the same
"look at the actual files, not just the aggregate metric" habit used for
the DJI_0790/DJI_0876 pseudo-label audits.

Usage:
    .venv/bin/python scripts/12_inspect_verifier.py --config configs/12_inspect_verifier.yaml
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

import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.methods.yolo.verifier import (  # noqa: E402
    NOT_PERSON_INDEX,
    PERSON_INDEX,
    build_model,
    build_transforms,
)
from torchvision import datasets  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402


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

    val_set = datasets.ImageFolder(
        Path(config["crops_dir"]) / "val",
        transform=build_transforms(config["crop_size"], train=False),
    )
    loader = DataLoader(val_set, batch_size=64, shuffle=False)

    model = build_model(pretrained=False).to(device)
    checkpoint = torch.load(config["checkpoint_path"], map_location=device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    review_dir = Path(config["review_dir"])
    false_positive_dir = review_dir / "false_positive"  # true not_person, predicted person
    false_negative_dir = review_dir / "false_negative"  # true person, predicted not_person
    for d in (false_positive_dir, false_negative_dir):
        if d.exists():
            shutil.rmtree(d)  # stale files from a previous checkpoint would mislead the review
        d.mkdir(parents=True)

    counts = {"true_positive": 0, "true_negative": 0, "false_positive": 0, "false_negative": 0}
    sample_index = 0
    with torch.no_grad():
        for images, labels in loader:
            preds = model(images.to(device)).argmax(dim=1).cpu()
            for pred, true_label in zip(preds.tolist(), labels.tolist()):
                src_path = Path(val_set.samples[sample_index][0])
                sample_index += 1
                if true_label == PERSON_INDEX and pred == PERSON_INDEX:
                    counts["true_positive"] += 1
                elif true_label == NOT_PERSON_INDEX and pred == NOT_PERSON_INDEX:
                    counts["true_negative"] += 1
                elif true_label == NOT_PERSON_INDEX and pred == PERSON_INDEX:
                    counts["false_positive"] += 1
                    shutil.copy2(src_path, false_positive_dir / src_path.name)
                else:
                    counts["false_negative"] += 1
                    shutil.copy2(src_path, false_negative_dir / src_path.name)

    total = sum(counts.values())
    print(f"val crops: {total}")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"\nMisclassified crops copied for review:")
    print(f"  {false_positive_dir} ({counts['false_positive']} — not_person the model called person)")
    print(f"  {false_negative_dir} ({counts['false_negative']} — person the model missed)")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "script": "12_inspect_verifier.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
    }
    manifest_path = (
        manifest_dir / f"12_inspect_verifier_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWritten: {manifest_path}")


if __name__ == "__main__":
    main()
