# Tier 1 Item 3: SAM3 Zero-Shot — The Assignment's Required Alternative Approach

Presentation-ready summary, matching `docs/01_cascade_journey_summary.md`
and `docs/02_rtdetr_journey_summary.md`'s format. All numbers from
`results/eval/comparison.csv` and `results/manifests/34_sam3_zeroshot_eval_*.json`.

**Framing:** every other method in this project (YOLO26n, the ResNet/
EfficientNet cascade, RT-DETR) is a trained or fine-tunable supervised
detector — different architectures, same paradigm. SAM3 is a foundation
model prompted directly with the class name ("person"), with **zero
training on this project's data**. This is the genuinely different
approach the assignment explicitly asks for (task item 5), not an
architecture swap — and it was reused at near-zero marginal cost, since
the same `Sam3Detector` wrapper (`src/methods/sam3_zeroshot/model.py`)
was already built and GPU-validated for the pseudo-labeling pipeline
(`notebooks/01_sam3_autolabel.ipynb`).

---

## Setup

Ran on Colab T4 (`notebooks/04_sam3_zeroshot_eval.ipynb`), GPU-only — SAM3
is ViT-based and far too heavy for CPU, unlike every other method in this
project which could at least run (slowly) locally. Prompted with
"person", conf=0.25 (unmodified default — same "measure the raw
out-of-the-box domain gap" convention used for YOLO26n's and RT-DETR's
own zero-shot checks), imgsz=1024 (the GPU-memory-safe value found after
imgsz=1920 OOM'd on a real T4 during the earlier labeling work — SAM3's
attention cost scales quadratically with resolution).

## Result: best accuracy, worst speed of any method tried

| Method | Hardware | mAP@.5 | mAP@[.5:.95] | Recall (@0.25) | F1 (@0.25) |
|---|---|---|---|---|---|
| YOLO26n zero-shot (Method 1) | T4 | 0.693 | 0.479 | 0.726 | 0.784 |
| RT-DETRv2-R18 zero-shot | CPU (not yet re-run on T4) | 0.740 | 0.468 | 0.761 | 0.677 |
| Cascade, small-input-stem (best trained result) | T4 | 0.786 | 0.526 | 0.778 | 0.766 |
| **SAM3 zero-shot** | T4 | **0.847** | **0.626** | **0.872** | 0.624 |

(RT-DETR's row is the only one not yet reproduced on T4 — its own script
already runs on GPU automatically when available, so re-running it on
Colab would be a quick addition if the presentation needs a fully
uniform-hardware table; not done yet in this cycle.)

SAM3 wins on every ranking-quality and recall metric — by a wide margin,
with **zero training** — while every other method in this comparison was
either fine-tuned, hand-tuned, or (for the cascade) an entire second
model trained specifically for this task.

**The cost is precision and, far more severely, speed:**

| | Value |
|---|---|
| Precision (@0.25) | 0.485 (665 false positives) |
| **Inference speed** | **0.37 FPS** (mean 2.72s/frame) |
| Fastest/slowest single frame | 2.22s / 44.26s |

0.37 FPS is roughly an order of magnitude slower than every trained
detector in this project. Not a deployment candidate as-is — this is
exactly consistent with its role throughout the project: a foundation
model used as a **zero-shot ceiling-finder and pseudo-labeling teacher**,
not a real-time detector.

## Per-video: the sharpest contrast in the project

| Video | mAP@.5 |
|---|---|
| Berghouse_Leopard_Jog | **1.000** (perfect) |
| DJI_0862 | 0.907 |
| DJI_0501 | 0.606 |
| DJI_0596 | 0.260 |

DJI_0596 remains the hardest video for every method tried this cycle
(ant-sized instances, per `CLAUDE.md` Section 6) — but SAM3's 0.260 there
is a large relative improvement over YOLO's 0.052 and RT-DETR's
0.029–0.041, consistent with a foundation model's stronger generalization
even where every method still struggles in absolute terms.

## Concrete success/failure examples (from visual inspection)

**Success — `Berghouse_Leopard_Jog__frame_000000.jpg`:** two trail runners,
both correctly boxed at high confidence (0.88 and ~0.9), exactly matching
ground truth — the visual confirmation behind this video's perfect 1.000
mAP@.5.

**Mixed — `DJI_0596__frame_000000.jpg`, the clearest failure example in
this project:** this video turns out to be a lake steamer boat (Swiss
flag visible — consistent with `CLAUDE.md`'s "Lake Geneva clips" note),
not a snow/mountain scene as its "ant-sized instances" label had
suggested. One frame shows all three error categories at once:
1. **Correct:** a cluster of people on the boat's rear deck, boxed
   correctly.
2. **Missed:** two people on the boat's raised bridge/wheelhouse — no
   prediction anywhere near their ground-truth boxes.
3. **False positive:** 2-3 "person" boxes over open water where nothing
   is present — plausibly wave/glare patterns misread as a distant person
   (not confirmed, just visually plausible).

## Open question, honestly flagged

The 44.26s single-frame maximum (against a 2.22s minimum and 2.72s mean)
is not explained by anything captured in this run — plausibly first-call
model compilation/caching overhead rather than a genuinely pathological
frame, but this is a plausible guess, not a confirmed cause (the
per-frame timing log itself wasn't preserved, only the aggregate min/
mean/max that reached the run manifest). Worth stating as an open
question in the presentation rather than a claimed explanation.

## Bottom line for the presentation

SAM3 zero-shot is the clearest paradigm-contrast result in the entire
project: the best accuracy of any method tried, achieved with no training
at all, at the cost of an order-of-magnitude speed penalty and
meaningfully lower precision than the trained detectors. It directly
answers the assignment's "genuinely different alternative approach"
requirement (task item 5) — every other method here is a supervised-
detection architecture variant; this is a different paradigm entirely,
with a different, honestly-reported trade-off profile.
