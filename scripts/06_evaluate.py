"""Score one method's predictions against the gold test set.

Reused for every method (YOLO26 zero-shot, SAM3 zero-shot, trained
YOLO26s, RT-DETR, ...) — same gold set, same metrics, so results are
directly comparable. Writes per-method JSON+Markdown, and appends a row
to results/eval/comparison.csv so the running cross-method table builds
up as each method gets evaluated.

Usage:
    .venv/bin/python scripts/06_evaluate.py \\
        --predictions results/yolo26_zeroshot/predictions.json \\
        --method-name yolo26n_zeroshot \\
        --config configs/06_evaluate.yaml
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.metrics import evaluate, evaluate_per_video, precision_recall_f1  # noqa: E402


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


def write_summary_md(path: Path, method_name: str, overall: dict, per_video: dict, operating_point: dict) -> None:
    lines = [f"# {method_name} — evaluation vs. gold test set", ""]
    lines.append("## Overall")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k, v in overall.items():
        lines.append(f"| {k} | {v:.4f} |")
    lines.append("")
    lines.append(f"## Operating point (confidence={operating_point['confidence_threshold']}, IoU={operating_point['iou_threshold']})")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k in ("tp", "fp", "fn", "precision", "recall", "f1"):
        v = operating_point[k]
        lines.append(f"| {k} | {v:.4f} |" if isinstance(v, float) else f"| {k} | {v} |")
    lines.append("")
    lines.append("## Per-video breakdown")
    lines.append("")
    video_names = list(per_video.keys())
    header_metrics = ["mAP@.5", "mAP@[.5:.95]", "mAP_small", "mAP_medium", "mAP_large"]
    lines.append("| Video | " + " | ".join(header_metrics) + " |")
    lines.append("|---|" + "---|" * len(header_metrics))
    for video in video_names:
        row = per_video[video]
        lines.append(f"| {video} | " + " | ".join(f"{row[m]:.4f}" for m in header_metrics) + " |")
    path.write_text("\n".join(lines) + "\n")


def update_comparison_csv(path: Path, method_name: str, overall: dict, operating_point: dict) -> None:
    row = {
        "method": method_name,
        "mAP@.5": round(overall["mAP@.5"], 4),
        "mAP@[.5:.95]": round(overall["mAP@[.5:.95]"], 4),
        "mAP_small": round(overall["mAP_small"], 4),
        "mAP_medium": round(overall["mAP_medium"], 4),
        "mAP_large": round(overall["mAP_large"], 4),
        "precision": round(operating_point["precision"], 4),
        "recall": round(operating_point["recall"], 4),
        "f1": round(operating_point["f1"], 4),
        "tp": operating_point["tp"],
        "fp": operating_point["fp"],
        "fn": operating_point["fn"],
    }
    rows = []
    if path.exists():
        with path.open(newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["method"] != method_name]
    rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--method-name", type=str, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())
    gt_path = Path(config["gt_path"])

    overall = evaluate(gt_path, args.predictions)
    per_video = evaluate_per_video(gt_path, args.predictions)
    operating_point = precision_recall_f1(
        gt_path, args.predictions, config["operating_point_confidence"], config["iou_threshold"]
    )

    print(f"=== {args.method_name} vs. gold test set ({gt_path}) ===")
    for k, v in overall.items():
        print(f"  {k}: {v:.4f}")
    print(f"  operating point (conf={config['operating_point_confidence']}): "
          f"P={operating_point['precision']:.3f} R={operating_point['recall']:.3f} "
          f"F1={operating_point['f1']:.3f} (TP={operating_point['tp']} FP={operating_point['fp']} FN={operating_point['fn']})")
    print("  per-video mAP@.5:", {v: round(m["mAP@.5"], 3) for v, m in per_video.items()})

    output_dir = Path(config["output_dir"]) / args.method_name
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps({
        "method": args.method_name,
        "overall": overall,
        "per_video": per_video,
        "operating_point": operating_point,
    }, indent=2))

    summary_path = output_dir / "summary.md"
    write_summary_md(summary_path, args.method_name, overall, per_video, operating_point)

    comparison_path = Path(config["output_dir"]) / "comparison.csv"
    update_comparison_csv(comparison_path, args.method_name, overall, operating_point)

    print(f"\nWritten: {metrics_path}")
    print(f"Written: {summary_path}")
    print(f"Written: {comparison_path}")

    manifest_dir = Path(config["manifest_dir"])
    manifest_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "script": "06_evaluate.py",
        "method_name": args.method_name,
        "predictions_path": str(args.predictions),
        "gt_path": str(gt_path),
        "config_path": str(args.config),
        "config_hash": config_hash(config),
        "seed": config["seed"],
        "git_sha": git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = manifest_dir / f"06_evaluate_{args.method_name}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    manifest_path.write_text(json.dumps(run_manifest, indent=2))
    print(f"Written: {manifest_path}")


if __name__ == "__main__":
    main()
