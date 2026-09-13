"""ResNet18 crop verifier for the detect-then-verify cascade (item 1b).

Binary classifier over candidate crops: does this box actually contain a
person, or is it one of the false positives YOLO produces once its
confidence threshold is lowered far enough to catch small instances?
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import ResNet18_Weights, resnet18

# ImageFolder sorts class directories alphabetically: not_person=0, person=1.
NOT_PERSON_INDEX = 0
PERSON_INDEX = 1


@dataclass
class EpochMetrics:
    loss: float
    accuracy: float
    person_precision: float
    person_recall: float
    person_f1: float


def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet18 with a fresh 2-way head.

    ImageNet pretraining matters more than architecture choice at this
    dataset size (a few thousand crops) — see docs/decision_log.md.
    """
    weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def build_transforms(crop_size: int, train: bool) -> transforms.Compose:
    """Light augmentation only — these crops are already tiny and blurry."""
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    )
    if train:
        return transforms.Compose([
            transforms.Resize((crop_size, crop_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            normalize,
        ])
    return transforms.Compose([
        transforms.Resize((crop_size, crop_size)),
        transforms.ToTensor(),
        normalize,
    ])


def build_loaders(
    crops_dir: Path, crop_size: int, batch_size: int, num_workers: int = 0
) -> tuple[DataLoader, DataLoader, list[int]]:
    """Returns train loader, val loader, and per-class train counts."""
    train_set = datasets.ImageFolder(
        crops_dir / "train", transform=build_transforms(crop_size, train=True)
    )
    val_set = datasets.ImageFolder(
        crops_dir / "val", transform=build_transforms(crop_size, train=False)
    )
    counts = [0] * len(train_set.classes)
    for _path, label in train_set.samples:
        counts[label] += 1
    return (
        DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=num_workers),
        DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=num_workers),
        counts,
    )


def _metrics_from_counts(tp: int, fp: int, fn: int, correct: int, total: int, loss: float) -> EpochMetrics:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return EpochMetrics(
        loss=loss,
        accuracy=correct / total if total else 0.0,
        person_precision=precision,
        person_recall=recall,
        person_f1=f1,
    )


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
) -> EpochMetrics:
    """One pass. Trains when `optimizer` is given, evaluates otherwise."""
    training = optimizer is not None
    model.train(training)

    total_loss = 0.0
    correct = total = tp = fp = fn = 0

    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            predictions = logits.argmax(dim=1)
            total_loss += loss.item() * labels.size(0)
            total += labels.size(0)
            correct += (predictions == labels).sum().item()
            tp += ((predictions == PERSON_INDEX) & (labels == PERSON_INDEX)).sum().item()
            fp += ((predictions == PERSON_INDEX) & (labels != PERSON_INDEX)).sum().item()
            fn += ((predictions != PERSON_INDEX) & (labels == PERSON_INDEX)).sum().item()

    return _metrics_from_counts(tp, fp, fn, correct, total, total_loss / max(total, 1))
