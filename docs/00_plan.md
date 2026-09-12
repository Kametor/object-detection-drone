# Work Plan — Computer Vision Interview Assignment

This document is the time-boxed, checkable version of the chosen method plan
(see `docs/decision_log.md`). Each day has a concrete "done" output (file,
table, commit) defined for it — "I worked on it" doesn't count, "here's what
I have" does.

Assignment PDF: `../bilgisayarli_goru_mulakat_gorevi.pdf` (kept outside the
repo, not tracked)
Literature review: `docs/reference/Autonomous_Labeling_Literature_Review.pptx`

## Timeline

Deadline: 2026-09-17 (7 calendar days from today). 5 weekday evenings + 2
weekend days available.

| Day | Date | Type | Focus |
|---|---|---|---|
| 0 | Thu 09-10 (tonight) | — | Plan, repo skeleton, reading the literature summary |
| 1 | Fri 09-11 | evening (~3-4h) | Data inventory + target class selection |
| 2 | Sat 09-12 | full day | Frame sampling, split, gold test set, YOLO26s zero-shot check |
| 3 | Sun 09-13 | full day | SAM3 setup (labeling tool + zero-shot detector) + evaluation pipeline |
| 4 | Mon 09-14 | evening | Pseudo-label generation + tracklet verification + noise audit |
| 5 | Tue 09-15 | evening | Student model training + full quantitative/qualitative comparison |
| 6 | Wed 09-16 | evening | Error analysis, result video, README, Colab T4 verification |
| 7 | Thu 09-17 | evening (buffer) | Presentation, decision log review, final check, delivery |

Principle: if a task looks like it will take more than one evening, propose
a smaller version first. Finishing the pipeline end-to-end takes priority
over polishing any single component.

---

## Day 1 — Friday evening: Inventory and target selection

**Why this comes first:** the target class decision is what everything else
is built on; if it's wrong, all of Saturday is wasted.

- [x] Download the Kaggle `kmader/drone-videos` dataset (put it on Drive —
      Colab will read from there)
- [x] `scripts/01_inventory.py`: extract sample frames from each video at
      regular intervals, record duration/resolution/FPS per video
- [x] Visual triage: which objects appear repeatedly, is there scale
      variation, are there ~500+ instances, is there occlusion/hard
      negatives
- [x] Write the decision to `docs/00_target_selection.md` (candidate
      classes, why each was eliminated, why the chosen one was chosen —
      this is the first question that will come up in the interview) —
      **decision: `person`**

**Output:** `docs/00_target_selection.md`, a per-video summary table under
`results/inventory/`, the selected target class.

## Day 2 — Saturday: Data preparation + two starting points

- [x] `scripts/02_sample_frames.py`: temporal-diversity-aware frame
      sampling (near-duplicates dropped), **video-level** train/val/test
      split (never frame-level — see README → Project rules)
- [ ] Gold test set: manually label ~100-200 frames (CVAT/Roboflow/LabelImg).
      This set never enters any pseudo-labeling pipeline
- [ ] YOLO26s zero-shot COCO-pretrained sanity check: run on the gold test
      set to measure the domain gap (nadir view, small objects), as a
      measuring stick, not a contender
- [ ] Score it on the gold test set for the first time (not final yet)

**Output:** `data/splits/{train,val,test}.txt` (video lists) — done,
`data/gold_test/` labeled set, first zero-shot YOLO26s results in
`results/yolo26s_zeroshot/`.

## Day 3 — Sunday: SAM3 setup and the evaluation infrastructure

- [ ] Set up SAM3 (fall back to YOLO-World) for two roles: (a) the labeling tool
      that will pseudo-label train+val, and (b) a zero-shot foundation-model
      detector prompted with "person", benchmarked on the test set (Tier 1,
      item 3 — this is what satisfies the "genuinely different alternative"
      grading criterion, see `docs/decision_log.md` 2026-09-12)
- [ ] `src/eval/`: mAP@0.5, mAP@0.5:0.95, PR curve, breakdown by size
      (small/medium/large), TIDE error decomposition
- [ ] **No comparison at a fixed score threshold** — motion energy, class
      confidence, and text-image similarity are not on the same scale
- [ ] First two-way quantitative table for YOLO26s zero-shot and SAM3
      zero-shot

**Output:** `src/methods/sam3_zeroshot/`, `src/eval/metrics.py`,
`results/comparison_v1/` (first 2-method table + PR curves).

## Day 4 — Monday evening: Pseudo-label self-training

- [ ] Use SAM3 (the labeling tool) to generate pseudo-labels on the
      train + val videos
- [ ] Noise filtering: high confidence threshold → ByteTrack temporal
      consistency (drop short tracks, flicker is almost always a false
      positive) → NMS → minimum box area → border-clipping rules
- [ ] **Manually audit ~100 pseudo-labels and report the measured noise
      rate** — this number goes into the presentation
- [ ] Log the results to `docs/decision_log.md` as a dated entry

**Output:** `src/data/pseudo_label.py`, `results/pseudo_labels/audit.md`
(noise rate + examples).

## Day 5 — Tuesday evening: Trained-detector comparison (Tier 1 + Tier 2)

**Scope note:** per the 2026-09-12 realignment (see `docs/decision_log.md`),
methods are tiered by priority. Tier 1 (YOLO26s, RT-DETR-R18, SAM3
zero-shot) is the minimum viable deliverable and is never dropped. If time
runs short, degrade Tier 2 in reverse order: drop the ResNet ablation
first, then ConvNeXt+CenterNet.

Execution order confirmed 2026-09-12: 1 -> 1b -> 2 -> Tier 2. If time runs
short after 1b, RT-DETR-R18 (item 2) must still be attempted before
polishing 1b further or starting Tier 2 — see `docs/decision_log.md`.

- [ ] Tier 1, item 1: YOLO26s (base) — train with optional P2 head, SAHI
      slicing, ByteTrack
- [ ] Tier 1, item 1b: cascade verifier — YOLO26s at a low confidence
      threshold + a ResNet18 crop classifier as a false-positive filter
      (positives from SAM3-labeled crops, negatives from YOLO's own
      unmatched low-confidence boxes + random background crops)
- [ ] Tier 1, item 2: RT-DETR-R18 — train with position/scale augmentation
- [ ] Tier 2 (if time allows): ConvNeXt backbone + CenterNet head + FPN neck
- [ ] Quantitatively compare all methods completed so far (YOLO26s
      zero-shot, SAM3 zero-shot, YOLO26s base vs. +verifier, RT-DETR-R18,
      ...) in a single table: mAP, PR, size breakdown, video/condition
      breakdown, compute cost (params, GFLOPs, VRAM, T4 FPS, and
      human-labeling-minutes)
- [ ] Qualitative comparison: selecting success, failure, and ambiguous
      examples

**Output:** `src/methods/{yolo,rtdetr,convnext_centernet}/`,
`results/final_comparison/table.csv` (generated by script, not by hand).

## Day 5.5 — if time remains: Tier 3 stretch method

- [ ] Keypoint tracking: LoFTR + RANSAC, manual box init on the first
      frame, re-detection in a local search window on subsequent frames
      (full-frame search if lost). Different protocol requiring
      per-video/per-object init — not forced into the shared mAP table,
      reported separately with its own evaluation

(The classical-CV motion baseline was dropped entirely on 2026-09-12 — see
`docs/decision_log.md`. It is class-agnostic, so it doesn't actually
perform person-specific detection.)

## Day 6 — Wednesday evening: Error analysis and delivery material

- [ ] Error analysis: interpret the TIDE breakdown + temporal stability
      (flicker rate across consecutive frames)
- [ ] Produce a result video (if applicable)
- [ ] `README.md`: setup + run steps, one-command reproducibility
- [ ] End-to-end verification of the notebook on Colab **free-tier T4** —
      this is also the dev environment (see `CLAUDE.md` Section 3), so
      this step mainly confirms nothing broke after a session reset

**Output:** `README.md`, the delivery notebook under `notebooks/` green on
T4, result video (if applicable) in `results/`.

## Day 7 — Thursday evening (buffer): Presentation and final check

- [ ] Map the presentation one-to-one to the PDF's "Presenting Results"
      list (chosen target, data preparation strategy, starting approach,
      alternative approach, quantitative/qualitative comparison,
      success/failure/ambiguous results, error analysis, strengths/
      weaknesses, compute cost) — **presentation language: English** (per
      `CLAUDE.md` Section 4, all repo docs are English too)
- [ ] Review `docs/decision_log.md` — does every technical decision have a
      matching justification in the presentation?
- [ ] Code cleanliness check: `pathlib`, type hints, config-driven runs (no
      hardcoded hyperparameters)
- [ ] Final end-to-end reproducibility check, delivery

**Output:** presentation file, delivery-ready repo.

---

## Tracking rules

- Every script's output is written to `results/` by the script itself —
  never edited by hand.
- At the end of each evening, the relevant checkboxes in this file are
  checked off, and any deviation (why something planned wasn't done) is
  noted in one line.
- If a day falls behind schedule, scope is cut first (production serving,
  multi-class detection, a broad hyperparameter sweep, manually labeling
  the whole dataset are out of scope) — the timeline is not extended.
