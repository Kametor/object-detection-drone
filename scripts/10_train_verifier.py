"""Train the ResNet18 crop verifier for the cascade (item 1b).

Trains on crops mined from the train split, validates on crops from the
val split — the same video-level discipline as everything else, so the
verifier never sees a test video.

Usage:
    .venv/bin/python scripts/10_train_verifier.py --config configs/10_train_verifier.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.nn as nn
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.methods.yolo.verifier import build_loaders, build_model, run_epoch  # noqa: E402


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

    train_loader, val_loader, class_counts = build_loaders(
        Path(config["crops_dir"]), config["crop_size"], config["batch_size"]
    )
    print(f"train crops per class (not_person, person): {class_counts}")
    print(f"val batches: {len(val_loader)}, device: {device}")

    model = build_model(pretrained=config["pretrained"]).to(device)

    # Weight the loss inversely to class frequency so the majority class
    # (not_person) doesn't simply dominate the decision.
    total = sum(class_counts)
    weights = torch.tensor(
        [total / (len(class_counts) * c) if c else 0.0 for c in class_counts],
        dtype=torch.float32,
        device=device,
    )
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"])

    checkpoint_path = Path(config["checkpoint_path"])
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    history = []
    best_f1 = -1.0
    for epoch in range(1, config["epochs"] + 1):
        train_metrics = run_epoch(model, train_loader, criterion, device, optimizer)
        val_metrics = run_epoch(model, val_loader, criterion, device)
        history.append({
            "epoch": epoch,
            "train": vars(train_metrics),
            "val": vars(val_metrics),
        })
        marker = ""
        # Select on val F1, not accuracy: val is ~82% person, so accuracy
        # would reward a model that just says "person" to everything.
        if val_metrics.person_f1 > best_f1:
            best_f1 = val_metrics.person_f1
            torch.save({"state_dict": model.state_dict(), "config": config}, checkpoint_path)
            marker = "  <- best, saved"
        print(
            f"epoch {epoch:>2} | train loss {train_metrics.loss:.4f} acc {train_metrics.accuracy:.3f}"
            f" | val loss {val_metrics.loss:.4f} acc {val_metrics.accuracy:.3f}"
            f" P {val_metrics.person_precision:.3f} R {val_metrics.person_recall:.3f}"
            f" F1 {val_metrics.person_f1:.3f}{marker}"
        )

    results_dir = Path(config["output_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "training_history.json").write_text(
        json.dumps({"best_val_person_f1": best_f1, "class_counts": class_counts, "history": history}, indent=2)
    )

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"10_train_verifier_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps({
        "script": "10_train_verifier.py",
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "best_val_person_f1": best_f1,
        "class_counts": class_counts,
    }, indent=2))

    print(f"\nbest val person-F1: {best_f1:.4f}")
    print(f"Written: {checkpoint_path}")
    print(f"Written: {results_dir / 'training_history.json'}")
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
