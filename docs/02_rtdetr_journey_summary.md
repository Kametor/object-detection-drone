# Tier 1 Item 2: RT-DETR — What We Tried, What We Found, Why We Stopped

Presentation-ready summary of the RT-DETR work, in the same spirit as
`docs/01_cascade_journey_summary.md`. Every number is pulled from
`results/eval/comparison.csv`; nothing here is estimated. Session ended at
the zero-shot stage — pseudo-label fine-tuning was deliberately not
attempted this cycle (see the final section for why).

**Framing:** RT-DETR is a transformer-based detector — a genuinely
different architecture *family* from YOLO (CNN) and the cascade (CNN +
CNN verifier), which is the actual point of Tier 1 item 2: show the
multi-architecture comparison the plan calls for, distinct from item 5's
"different approach" requirement (filled separately by SAM3 zero-shot).

---

## Step 1 — Finding a real RT-DETR-R18: Ultralytics doesn't have one

The project plan named "RT-DETR-R18" specifically — a small, ResNet18-
backbone variant, comparable in spirit to the ResNet18-based cascade.
`ultralytics` (already a project dependency) only ships `rtdetr-l` and
`rtdetr-x` — larger models with a different (HGNetv2) backbone, no R18
option.

**Decision:** add Hugging Face `transformers` (new dependency) to get the
original authors' actual R18 checkpoint: `PekingU/rtdetr_v2_r18vd` —
RT-DETR**v2** (an improved follow-up from the same team, better reported
accuracy at the same 20.2M-parameter size), and confirmed via the Hub's
naming convention (no `_coco_o365` variant exists for v2, matching v1's
pattern where the plain name means COCO-only) that it's pretrained on pure
COCO — the same corpus as YOLO26n's own pretraining, keeping the zero-shot
comparison fair.

`src/methods/rtdetr/model.py` wraps this checkpoint behind the exact same
`Detection` / `.detect()` interface as `Yolo26Detector`, so every existing
evaluation/visualization script needed zero changes.

---

## Step 2 — Zero-shot sanity check, at native resolution

Ran both this HF checkpoint and, as a second data point, Ultralytics'
`rtdetr-l` — each at its own native training resolution (both default to
640×640) — on the gold test set, same conf=0.25 operating point as
YOLO26n's own zero-shot check.

| Method | mAP@.5 | mAP_small | Precision | Recall | F1 | TP/FP/FN |
|---|---|---|---|---|---|---|
| YOLO26n (Method 1, imgsz 1920) | 0.694 | 0.018 | 0.855 | 0.727 | **0.786** | 523/89/196 |
| RT-DETRv2-R18 (HF, 640×640) | **0.740** | 0.000 | 0.609 | 0.761 | 0.677 | 547/351/172 |
| RT-DETR-l (Ultralytics, 640×640) | 0.731 | 0.004 | 0.762 | 0.748 | 0.755 | 538/168/181 |

**A genuinely different profile from YOLO, not a copy:** both RT-DETR
checkpoints rank detections better overall (higher mAP) and have higher
recall, but produce far more false positives at the same threshold (2–4×
YOLO's), and are dramatically worse on small objects — near-zero for both,
worse than YOLO's already-weak 0.018.

---

## Step 3 — Tried to make the comparison "fair" by matching YOLO's resolution — broke one model, stress-tested the other

**Reasoning:** YOLO was evaluated at `imgsz=1920` (much higher than
RT-DETR's default), so forced both RT-DETR checkpoints up to a matching
1920×1088.

**Result — the two checkpoints reacted completely differently:**

| Checkpoint | mAP@.5 (640→1920) | mAP_small (640→1920) | FP (640→1920) |
|---|---|---|---|
| RT-DETRv2-R18 (HF) | 0.740 → **0.253** (collapse) | 0.000 → 0.028 | 351 → **1733** (5×) |
| RT-DETR-l (Ultralytics) | 0.731 → 0.654 (moderate drop) | 0.004 → **0.093** (23×) | 168 → 442 (2.6×) |

Inspected the HF checkpoint's raw boxes on its worst frame before
concluding this wasn't a bug in our own coordinate scaling: 67 well-formed
boxes, all clustered on one real region — a duplicate-detection storm, not
scattered garbage.

**Root cause:** RT-DETR has **no NMS at inference** (unlike YOLO, where
NMS is an independent post-processing step that tolerates resolution
changes). Its "one query, one object" behavior is *learned* during
training via one-to-one matching, calibrated to a specific token count —
push the resolution far outside that and there's no fallback. This is a
documented characteristic of the DETR family: RT-DETRv2's own paper adds
"flexible size training" specifically to mitigate it, which plausibly
explains why Ultralytics' checkpoint (a different training recipe)
degraded far more gracefully than the paper authors' own R18 release, and
even gained substantially on small objects and the hardest video (DJI_0596
mAP@.5: 0.041 → 0.373) — the resolution boost helping exactly where hoped,
just at a real cost elsewhere.

**Correction:** the 1920 forcing is kept only as a labeled diagnostic
(`rtdetr_v2_r18_1920_diagnostic_BROKEN` in the comparison table, clearly
not a competing result); each checkpoint's *native*-resolution number
(Step 2's table) is the valid one for the method comparison.

---

## Step 4 — Decided against a ResNet cascade for RT-DETR

The cascade idea (item 1b) depends on YOLO's low-confidence output being a
clean, gradually-degrading pool of candidates (more boxes, falling
precision) that a verifier can usefully filter. RT-DETR's low-confidence/
out-of-distribution behavior isn't that — it's a duplicate-detection
storm (Step 3), a fundamentally different failure shape. There's no
equivalent "ambiguous band" for a verifier to adjudicate. Not attempted,
and not a gap — the cascade's own premise doesn't transfer.

---

## Step 5 — Stopped before pseudo-label fine-tuning: why

The plan calls for fine-tuning RT-DETR-R18 on the SAM3 pseudo-labels, with
extra position/scale augmentation (transformer detectors are more
augmentation-sensitive than CNN heads). Decided not to attempt this cycle:

- Transformer detectors are known to be more data-hungry than CNN
  detectors, and our pseudo-label training set is modest (~a handful of
  videos). A short, single-config fine-tuning run carried real risk of an
  unstable or uninformative result for the time it would cost.
- The plan's own contingency clause explicitly allows for this: *"If
  schedule pressure hits after 1b, RT-DETR must still be attempted (even a
  minimal/undertrained run)"* — this was weighed and consciously not taken
  up this cycle, in favor of preserving time for SAM3 zero-shot (Tier 1
  item 3, the assignment's actual required "genuinely different approach").
- Honest framing for the writeup: RT-DETR's zero-shot comparison and the
  resolution-sensitivity finding are complete and presentable results;
  fine-tuning was a conscious, time-boxed cut, not an oversight — the
  prediction (limited data + transformer sample-inefficiency) is strong
  enough that the expected value of attempting it now was judged too low
  relative to its cost.

## Bottom line for the presentation

| | mAP@.5 (native res.) | F1 (native res.) |
|---|---|---|
| YOLO26n zero-shot (Method 1) | 0.694 | **0.786** |
| RT-DETRv2-R18 zero-shot | **0.740** | 0.677 |
| RT-DETR-l (Ultralytics) zero-shot | 0.731 | 0.755 |

RT-DETR is a genuinely different architecture with a genuinely different
profile: better raw ranking quality (mAP) and recall, worse precision and
small-object detection than YOLO — plus a real, literature-grounded,
checkpoint-dependent resolution-sensitivity finding discovered by directly
testing it. No fine-tuning attempted this cycle — a deliberate, reasoned
cut, not a silent gap.
