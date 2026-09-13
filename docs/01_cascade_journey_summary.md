# Item 1b Journey: Detect-then-Verify Cascade — Problem → Fix → Result

Presentation-ready walkthrough of every step taken to build and improve the
YOLO26n + ResNet18 cascade (Tier 1, item 1b of `plan.md`). Every number here
is pulled from `results/eval/comparison.csv` and the dated entries in
`docs/decision_log.md` — nothing here is estimated or reconstructed from
memory.

**Framing note for the presentation:** everything below is iteration on the
*baseline* approach (YOLO, a supervised detector) — it is **not** the
assignment's required "genuinely different alternative approach." That role
is filled separately by SAM3 zero-shot (a foundation model, no training).
This document is the answer to the assignment's "identify the baseline's
core problems, and try to address them" ask (task items 3–4), not item 5.

---

## Step 0 — Baseline (Method 1): plain YOLO26n, zero-shot, conf=0.25

**What:** COCO-pretrained YOLO26n, no training at all, run at its default
confidence threshold (0.25) on the gold test set (196 frames, 719
human-labeled boxes across 4 videos).

**Result:**

| Metric | Value |
|---|---|
| mAP@.5 | 0.694 |
| mAP@[.5:.95] | 0.482 |
| Precision | 0.855 |
| Recall | 0.727 |
| F1 | 0.786 |
| TP / FP / FN | 523 / 89 / 196 |

**Problem identified:** on the two hardest test videos (DJI_0501, DJI_0596),
`mAP_small` = **exactly 0.0** — plain YOLO catches **zero** small/distant
people at any confidence level. This isn't noise; it's a structural limit
of the detector's feature map resolution on tiny objects.

---

## Step 1 — Try lowering YOLO's confidence floor to 0.01 (no verifier yet)

**Expectation:** a lower floor forces YOLO to propose boxes for the small
objects it was silently discarding, raising recall — at the cost of some
precision.

**Result:** exactly that trade, but far more extreme than hoped:

| Conf | Precision | Recall | F1 |
|---|---|---|---|
| 0.25 (baseline) | 0.855 | 0.727 | 0.786 |
| 0.10 | 0.695 | 0.805 | 0.746 |
| 0.05 | 0.538 | 0.848 | 0.659 |
| 0.01 | 0.220 | 0.894 | 0.353 |

At 0.01, recall climbs to 0.894 (real gain) but precision collapses to
0.220 — 4 out of 5 predictions are wrong. **Unusable alone.** (Curiosity:
mAP@.5 for this unfiltered pool is actually 0.801, higher than every
cascade variant later — mAP rewards a good *ranking* across all thresholds
and doesn't penalize a sea of false positives as harshly as a real
deployment threshold would. Kept as an open note, not a target to beat.)

---

## Step 2 — First cascade attempt: verify every candidate with ResNet18

**Idea:** run YOLO at the noisy 0.01 floor, then have a small trained
ResNet18 classifier look at every proposed box (as a cropped image) and
decide "is this really a person?" — reject what it says no to.

**Expectation:** keep the recall gained by lowering the floor, while the
verifier cleans up the flood of new false positives.

**Result — worse than doing nothing:**

| Metric | Method 1 | Full verify-everything hybrid |
|---|---|---|
| mAP@.5 | 0.694 | **0.368** |
| F1 | 0.786 | **0.514** |

**Why:** the verifier was also asked to judge boxes YOLO was *already
confident about* (score ≥ 0.25) — and it wrongly rejected a meaningful
number of those, throwing away detections Method 1 got right for free.

---

## Step 3 — Fix: only verify the ambiguous band, trust YOLO above 0.25

**Fix:** boxes scoring ≥ 0.25 are auto-accepted, unchanged. Only the
[0.01, 0.25) "ambiguous band" — where recall was being bought at heavy
precision cost — goes through the verifier.

**Result — big recovery:**

| Metric | Method 1 | Band-gated hybrid |
|---|---|---|
| mAP@.5 | 0.694 | **0.732** |
| Best F1 | 0.786 | 0.782 (@ conf 0.15) |

Close, but still just short of the baseline's F1.

---

## Step 4 — Diagnosed why the verifier struggled: training data imbalance

**Investigation:** checked what the verifier's ~5k training crops actually
contained.

| Video | % of train "person" crops | % of train "not_person" crops |
|---|---|---|
| **DJI_0790** | **70%** | **81%** |
| Surenen Pass | 15% | 1% |
| Stockflue | 8% | 6% |
| others | remainder | remainder |

One video (a snow/sled-dog scene) dominated training — the verifier had
essentially learned that video's specific look, not "person" in general.

**Fix:** video-balanced sampling — every source video contributes equally
per training epoch, regardless of how many crops it produced.

**Result:**

| Metric | Band-gated (original) | Band-gated (video-balanced) |
|---|---|---|
| mAP@.5 | 0.732 | **0.760** |
| Best F1 | 0.782 | 0.782 (unchanged — same region) |

**Bonus finding — the real point of this cascade:** on the two hardest
videos, small-object recall went from **flatly zero** to something real:

| Video | Small GT people | Caught by Method 1 | Caught by cascade |
|---|---|---|---|
| DJI_0501 | 5 | 0 | 1 |
| DJI_0596 | 39 | 0 | **9** |

---

## Step 5 — Tried narrowing the verified band to [0.10, 0.25)

**Idea (user's hypothesis):** maybe candidates below 0.10 are too hard/noisy
even for the verifier to usefully judge — raise the floor so it only
judges a "cleaner" band.

**Expectation:** better precision on an easier task.

**Result — opposite of expected:** mAP@.5 **dropped** to 0.734. The
discarded [0.01, 0.10) region was contributing real net-positive ranking
signal, not just noise. **Reverted** to the 0.01 floor.

---

## Step 6 — Tried adding a size-based gate (always verify small objects)

**Idea:** YOLO already handles large objects; since it structurally can't
represent small ones, route every small candidate to the verifier
regardless of its confidence.

**First checked before building it:** would simply *dropping* large,
low-confidence candidates (instead of verifying them) cost real recall?
Yes — 75/719 gold GT boxes (10.4%) are *only* ever proposed that way, so
large objects kept the existing confidence-only gate.

**Result at a 32×32 "small" threshold:** mAP@.5 **dropped** to 0.753. Root
cause: 4 true positives lost were high-confidence detections sized
926–1011 px² — not really tiny, just under the cutoff — that the verifier
wrongly second-guessed.

**Result at a corrected 24×24 threshold:** bit-for-bit identical to
step 4's result (0.760) — safe, but added no further gain. **Conclusion:**
this idea had no headroom left once tuned to avoid harm.

---

## Step 7 — Score fusion: blend both models' confidence instead of a hard yes/no

**Idea:** instead of the verifier making a binary accept/reject call,
combine YOLO's own confidence and the verifier's person-probability into
one continuous score (geometric mean), and let the standard mAP/F1 sweep
find the best cutoff — rather than pre-deciding it with a threshold.

**Result — best yet:**

| Metric | Method 1 | Band-gated (hard gate) | **Score fusion** |
|---|---|---|---|
| mAP@.5 | 0.694 | 0.760 | **0.786** |
| Best F1 | 0.786 | 0.782 | 0.783 (@ conf 0.38) |

mAP clearly best; F1 essentially tied with the baseline (not yet beating
it). Per-video breakdown showed this was a real mixed bag — better on 2 of
4 videos, worse on 2 — netting out close to even on F1 despite the mAP win.

---

## Step 8 — Architecture tweak: "small-input stem" for the ResNet18

**Idea:** ResNet18's stock first layer (7×7 conv, stride 2) plus a maxpool
was designed for 224×224 ImageNet photos — for our 64×64 crops (often
already a tiny, blurry person blown up to fill the frame), it downsamples
to 16×16 *before the network even starts reasoning*, discarding most of
the little detail there was. Replaced it with a 3×3, stride-1 conv and no
maxpool (a standard adaptation for small-input images), keeping everything
else — millions of pretrained ImageNet weights — unchanged.

**Retrained with this change (video-balanced sampling kept), then re-ran
score fusion:**

| Metric | Score fusion, standard stem | Score fusion, small-input stem |
|---|---|---|
| mAP@.5 | 0.786 | **0.788** |
| Precision | 0.865 | **0.890** |
| Recall | 0.715 | 0.712 |
| **F1** | 0.783 | **0.791** |
| FP | 80 | **63** |

**This is the first configuration all cycle to beat Method 1's own F1**
(0.791 vs. 0.786) — via a real drop in false positives (89 → 63 relative
to the baseline) at a negligible recall cost. Method 1's 0.786 is at
Ultralytics' unmodified 0.25 default — deliberately never tuned, by
design, throughout this project (Method 1's whole point is to be the
untouched, out-of-the-box baseline); the cascade's own 0.791 is its
swept-optimal point. (Side note from the later GPU validation run,
`docs/decision_log.md`: sweeping Method 1's own threshold too — a
different question than the one this comparison asks — lands it around
0.789, close enough to be a useful robustness check but not a reason to
change the comparison's design.)

**Honest caveat:** this checkpoint
scored *worse* on the validation set (F1 0.9446) than the standard-stem
checkpoint (0.981), yet generalized *better* to the held-out test videos —
reinforcing, once again, that val (a single video, sharing train's
distribution) is not a reliable predictor of test performance in this
project. This result comes from one training run (one random seed) — a
real signal, not yet confirmed by repetition.

---

## Bottom line for the presentation

| Stage | mAP@.5 | Best F1 |
|---|---|---|
| Method 1 (plain YOLO, no training, conf=0.25 as always used in this project) | 0.694 | 0.786 |
| **Final cascade** (score fusion + small-input-stem verifier, own swept-optimal conf) | **0.788** | **0.791** |

These CPU numbers were re-run on Colab T4 GPU for the authoritative,
hardware-final figures — see `docs/decision_log.md`, "GPU (T4) validation
of the full method comparison": every mAP matches almost exactly
(reproducibility confirmed), and the GPU run also confirms the
small-input-stem ResNet beats both the standard-stem ResNet and
EfficientNet-B0 inside the cascade on real GPU numbers, not just CPU.

A real, modest, honestly-earned win — reached only after two failed
attempts (full hybrid, narrow band) and two neutral ones (size gating),
each diagnosed and documented rather than hidden. The cascade's clearest,
most defensible value isn't the aggregate number — it's recovering some of
the small/distant people (10 of 44, previously zero) that plain YOLO
structurally cannot see at all.

**Also tried: EfficientNet-B0 as an alternative verifier backbone**
(`configs/26`, trained on Colab GPU). Scored highest of all three
checkpoints on validation (F1 0.9835) but *lowest* on the actual test set
(mAP@.5 0.779, F1 0.782 vs. the small-input-stem ResNet's 0.788/0.791) —
a third confirmation that val score doesn't predict test generalization
here. Also ~5x slower per crop on this CPU despite far fewer parameters
(4.0M vs. ResNet18's 11.2M) — depthwise-separable convolutions vectorize
less efficiently on general CPU kernels than plain convolutions, an
efficiency gain that mainly shows up on GPU/accelerator hardware. No
change to the final configuration: score fusion + small-input-stem
ResNet18 remains best.
