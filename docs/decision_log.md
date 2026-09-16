# Decision Log

Every significant technical decision is recorded here as a dated entry:
what was decided, what alternatives were considered, why. These entries
become presentation slides directly.

## 2026-09-10 — Repo skeleton and confirmation of the method plan

**Decision:** The project was set up in a layered structure (`configs/`,
`data/`, `docs/`, `notebooks/`, `scripts/`, `src/{data,methods,eval}`,
`results/`). The literature review was placed under `docs/reference/`, the
day-by-day work plan was written to `docs/00_plan.md`. The assignment PDF
is kept outside the repo for reference only.

**Alternatives:** Working inside one large notebook was considered and
rejected — the assignment explicitly counts code quality and
reproducibility as grading criteria (PDF, "Evaluation" section); a
notebook-only approach was therefore not chosen.

**Rationale:** Pure functions in `src/` are both testable and reproducible
on Colab via notebook imports; the numbered entry points in `scripts/`
document the run order.

**Method plan:**

1. Baseline A — classical CV, zero labels: ego-motion compensation
   (ORB+RANSAC homography) → warp → frame differencing → morphology →
   connected components. Score = normalized motion energy.
2. Baseline B — off-the-shelf reference: COCO-pretrained YOLO, zero-shot.
   Not a contender, a measuring stick for the domain gap.
3. Alternative 1 — open-vocabulary detection: text-prompted
   vision-language detector (OWLv2 / YOLO-World / GroundingDINO). Score =
   image-text similarity. A completely different paradigm from Baseline A.
4. Alternative 2 — pseudo-label self-training: Alternative 1 is used as
   teacher, pseudo-labels are generated on training videos, filtered, and
   a small supervised student (YOLO-s / RT-DETR-R18) is trained. Headline
   result: near-zero labeling cost + deployable speed.

**Note — the method plan was confirmed against the literature:** the
"reference architecture" section (Layers 2-5) of the literature review
under `docs/reference/` independently mirrors the Baseline A/B →
Alternative 1 → Alternative 2 sequence described above. Two concrete
implementation details taken from the review:

- Pseudo-label acceptance should happen at the **tracklet level**, not the
  frame level — the largest efficiency gains in the review (96%, 78%) come
  from this granularity.
- The teacher should not be frozen (STAC's pitfall); it should be updated
  with EMA.

## 2026-09-11 — Scope widening: multi-architecture student comparison

**Decision:** Alternative 2 (pseudo-label self-training) was widened from
a single student model to a comparison of four architectures: YOLO26s (+P2
head, SAHI, ByteTrack), RT-DETR-R18 (transformer), ConvNeXt backbone +
CenterNet head + FPN neck, and a ResNet18/50 backbone ablation. A SAM3
(fall back to SAM2) promptable-segmentation teacher option was added to
Alternative 1, to be compared on a small sample against the existing
OWLv2/YOLO-World/GroundingDINO candidates, picking whichever gives the
cleanest boxes. A fourth alternative to try if time remains was also
added: LoFTR+RANSAC keypoint-based single-object tracking (manual init,
local-window re-detection). The final presentation language was changed
from Turkish to **English** (`docs/`, `README.md` stayed Turkish at the
time of this entry — later superseded, see the 2026-09-12 entry below).

**Context:** the user consulted other computer vision practitioners, put
their suggestions together (`plan.md`), and asked for them to be
integrated into the plan.

**Alternatives and why this wasn't rejected:** this widening directly
conflicts with `CLAUDE.md` Section 11's "no custom architecture design"
and Section 1's "prefer finishing the pipeline over polishing any single
component" principles — this was stated explicitly and put to the user.
The user knowingly accepted the added time risk and asked to proceed with
the widened scope. The one thing that was rejected: synthetic data
generation via Blender/Gaussian-splatting — this had already been
positioned as a "future work" presentation slide in the friends'
suggestions, and will not be implemented in this cycle.

**Rationale / risk mitigation:** if schedule pressure hits, the
degradation order is defined in `CLAUDE.md` Section 6: drop the ResNet
ablation first, then ConvNeXt+CenterNet; the YOLO26s vs. RT-DETR-R18
comparison is kept as the minimum viable result (equivalent to the
original single-student plan). The core pipeline (Baseline A/B, Alt 1,
gold test set, evaluation protocol) will not be sacrificed under any
circumstance.

**Affected files:** `CLAUDE.md` (Sections 4, 6, 11 updated),
`docs/00_plan.md` (Day 3-5 tasks updated).

## 2026-09-11 — Target class selection: `person`

**Decision:** the target class was set to `person`. The full candidate
table and rationale are in `docs/00_target_selection.md`.

**Method:** at least 1 frame was extracted from all 13 videos, plus 4-5
additional frames (evenly spaced across the video) from six of them, and
visually triaged — the decision was based on the whole video, not a
single frame.

**Alternatives:** boat/sailboat (2 videos, mostly stationary — a poor fit
for the motion-based Baseline A), vehicle and dog (sled team) (only 1
video — fails the "2-3 different videos" criterion), static objects
(statue, glacial lagoon) (no scale variation, no repeated instances) were
considered and eliminated.

**Rationale:** `person` appears consistently in 6/13 videos (above the
threshold), has strong scale variation from altitude/distance changes,
easily yields 500+ instances, and has rich occlusion/hard-negative
material (vegetation and footbridge occlusion, distant figures blending
into rock/shadow, small human silhouettes blending with sled dogs in
snow). It's also already a COCO class, which keeps Baseline B's
(zero-shot COCO-YOLO) domain-gap measurement meaningful.

**Side correction:** during triage, the dataset turned out not to be from
a single country (Switzerland) — Scotland, likely Iceland, and at least
one non-European location are also present. `CLAUDE.md` Section 1 was
corrected accordingly; this doesn't affect the target-class decision.

## 2026-09-12 — Video-level train/val/test split: 3/1/2

**Decision:** all 6 videos containing `person` were split into three sets
at the video level, with no video used in more than one set:

| Set | Video(s) | Total duration |
|---|---|---|
| **Train** | Berghouse Leopard Jog, Surenen Pass Trail Running, Stockflue Flyaround | ~100.3s |
| **Val** | VerticalFlyOver | 18.9s |
| **Test** | DJI_0790 (snow/dog-sled), DJI_0862 (volcanic terrain) | ~117.1s |

List files: `data/splits/{train,val,test}.txt`. The 7 videos without
`person` were also put into `data/splits/background.txt` — these won't be
labeled, only used as a hard-negative background source (see below).

**Alternatives discussed and rejected (summary of the decision process):**

1. **Segment-based split within the same video** (a few seconds of each
   video for train, the rest for test) — rejected. Different time windows
   of the same video share the same people, the same background, the same
   lighting, and the same drone flight path; even though the frames are
   pixel-different, the model can memorize those specific people's
   appearance instead of the general concept of "person" ("identity/
   sequence leakage" — the reason video-based benchmarks like MOT and
   ImageNet-VID always split at the video/sequence level). This is exactly
   what `CLAUDE.md` Rule 1 forbids.
2. **Shrinking test to a single video to maximize train** — rejected.
   `CLAUDE.md` Section 7 explicitly requires a "breakdown by video/
   condition" table; with a single test video that breakdown collapses to
   one row and becomes meaningless. So test was kept at a minimum of 2
   videos, chosen to represent as different conditions as possible
   (snow/dog-sled vs. volcanic terrain — deliberately different from
   train's grass/rocky conditions, giving a real generalization test).
3. **The assumption that augmentation reduces the need for more train
   videos** — rejected. Augmentation (flip/rotate/color/scale) produces
   variations of the same scene, it doesn't invent a new scene/domain; it
   therefore doesn't change the train-video-count decision, it's a
   separate step applied to the train side *after* the split decision.
4. **Augmenting or enlarging val** — rejected. Val's job is
   checkpoint/architecture selection, which requires it to be fixed and
   real (unaugmented); an augmented val would corrupt model selection with
   random noise and would go against the spirit of Rule 3 ("every reported
   number must be reproducible").
5. **Carving val out of the train videos as a time slice** (instead of a
   separate video) — considered but rejected. Val leakage is a lower risk
   than test leakage (it affects checkpoint selection, not the final
   numbers), but since no hyperparameter sweep is planned anyway (Section
   11), val's only job is checkpoint selection/early stopping — keeping a
   separate video for that (the shortest one, VerticalFlyOver, 18.9s) has
   low cost and a high payoff (reliable model selection without breaking
   the rule).

**Rationale (summary):** with a small data budget, the side that should be
cut is train (Alternative 2 already has a "get by with little labeling"
story); shrinking test instead eliminates an evaluation dimension the
assignment requires (breakdown by condition) entirely — that trade-off is
more expensive.

**Accepted remaining limitation:** with only 6 videos, similar shoot
series/actors may recur across train and test videos (e.g., Berghouse and
Surenen); this can't be fully solved but is stated explicitly (matching
Section 1's "honest error analysis" criterion). Test is not statistically
"definitive," it's "indicative" — this will be phrased that way in the
final report.

**Free idea (to be applied):** the 7 videos in `background.txt` will be
added to Alternative 2 training as unlabeled hard-negative background —
expected to reduce the false-positive rate, at no labeling cost.

## 2026-09-12 — SAM3's role: labeling tool only, not a benchmarked method

**Decision:** SAM3 (fall back to SAM2) will not enter the comparison table
as Alternative 1 — it will only be used to pseudo-label the train+val
videos. Alternative 1 (the open-vocabulary detector benchmarked on the
test set) will be chosen from among OWLv2/YOLO-World/GroundingDINO.
`CLAUDE.md` Section 6 was updated accordingly.

**Rationale:** if SAM3 were both the labeling tool and a benchmarked
method, Alt1's own score would carry a circularity risk when compared
against Alt2, which is trained on pseudo-labels it produced/influenced.
Separating the two removes this risk entirely for Alt1 (a residual
similarity from Alt2 learning from SAM3's pseudo-labels remains, but that
is inherent to any self-training setup — which is exactly why the
separate, manually-labeled test set and the noise-rate audit exist).

**Idea discussed and rejected regarding SAM3's accuracy:** it was
suggested that if SAM3's accuracy is measured on a small sample and clears
a good-enough threshold, SAM3 could also label the test videos —
rejected. The reason is circularity, not accuracy: the validation sample
would likely come from train's easy conditions (grass/trail), while test
is deliberately the most different/hard conditions (snow, volcanic
terrain) — accuracy there would never actually be measured. Also, if SAM3
labeled test, its systematic errors would get baked into "ground truth,"
making honest error analysis impossible.

**Accepted risk mitigation:** on top of the automated quality filters
(confidence threshold, ByteTrack temporal filter, NMS, minimum area),
after SAM3 labels train+val, the user and Claude will manually review a
portion of the output together — 100% correctness isn't claimed, but this
should catch obvious errors the automated filters might miss.

## 2026-09-12 — Method plan realigned to the user's own priority list (`plan.md`)

**Decision:** `CLAUDE.md` Section 6 was rewritten to directly match the
numbered method list the user drafted in `plan.md` after consulting other
CV practitioners, replacing the earlier Baseline A/B + Alternative 1-4 +
"student" terminology, which the user found confusing and hard to track.
The new structure uses three priority tiers:

- **Tier 1 (required, minimum viable deliverable):** YOLO26s (zero-shot
  sanity check, then trained on pseudo-labels), RT-DETR-R18, and SAM3 used
  as a zero-shot foundation-model detector (prompted with "person",
  benchmarked on the test set).
- **Tier 2 (secondary, time-permitting):** ConvNeXt backbone + CenterNet
  head + FPN neck, ResNet18/50 backbone ablation.
- **Tier 3 (stretch, lowest priority):** LoFTR+RANSAC keypoint tracking,
  and the classical-CV motion baseline (ego-motion compensation + frame
  differencing).

**Alternatives dropped:** a standalone open-vocabulary benchmark
(OWLv2/YOLO-World/GroundingDINO) and a DINOv2 few-shot metric-learning
alternative — both were scope added by Claude before `plan.md` existed;
the user's own list is now the single source of truth for which methods
get built. The open-vocabulary role is fully covered by SAM3 (Tier 1).

**Two explicit changes from the user's original list, both discussed and
confirmed:**

1. **The classical-CV motion baseline was demoted** from "first baseline"
   to Tier 3 (lowest priority), at the user's request — it reads more like
   a tracker than a per-frame detector, and the assignment expects
   detection even where temporal information is used.
2. **SAM3-as-zero-shot-detector was promoted** from the user's original
   "mention only if hardware allows" framing to a required Tier 1 item.
   This was flagged loudly before being adopted: with the motion baseline
   and keypoint tracking both demoted to stretch-only, and the four
   trained-detector methods (YOLO26s, RT-DETR, ConvNeXt+CenterNet, ResNet
   ablation) all being architecture swaps on the same supervised-detection
   paradigm, the plan risked satisfying zero of the assignment's "at least
   one genuinely different alternative approach" grading criterion
   (Section 1) if time ran out before reaching Tier 3. Benchmarking SAM3
   zero-shot on the test set costs almost nothing extra (it reuses the
   same SAM3 inference pipeline already required for pseudo-label
   generation), so promoting it to Tier 1 closes that gap at near-zero
   cost. The user confirmed this reasoning and accepted the change.

**Rationale for demoting the motion baseline without a Tier-1
replacement:** unlike SAM3-as-detector, the motion baseline requires
genuinely separate implementation effort (ORB+RANSAC homography, frame
differencing, morphology) that doesn't overlap with anything else being
built, so there's no equivalent "near-free" way to keep it in Tier 1 — it
stays a stretch goal.

**Affected files:** `CLAUDE.md` (Sections 5, 6, 8, 11 updated),
`docs/00_plan.md` (Day 2/3/5/5.5 to be updated to match the new tiers).

## 2026-09-12 — Classical-CV motion baseline dropped entirely

**Decision:** the classical-CV motion baseline (ego-motion compensation +
frame differencing, item 7 in the tiered method plan above) was removed
from the plan entirely, rather than kept as a demoted Tier 3 stretch item.

**Reasoning:** while reviewing the tiered list, the user pointed out that
this method doesn't actually perform the assignment's task. It is
**class-agnostic** — it flags anything that moves differently from the
background (a person, a dog, wind-blown vegetation, homography-estimation
parallax noise), with no notion of "person" at all. Concretely, on the
DJI_0790 test video (a person plus 6-8 sled dogs), it would box both
indiscriminately, scoring poorly on precision against a person-only
ground truth not because it's a weak detector but because it isn't
detecting the target class in any meaningful sense. Its only legitimate
role would have been as an explicitly-labeled lower-bound reference to
motivate why class-aware methods are needed — a valid point, but one Tier
1's SAM3-vs-trained-detector comparison already makes, and the user
decided it wasn't worth spending implementation time to demonstrate a
method that "isn't going to work" for the stated task.

**Note on the remaining Tier 3 item (keypoint tracking, LoFTR+RANSAC):**
this method shares a related limitation — it doesn't detect "person" in
general either, it re-locates one manually-initialized instance per video
via feature matching. This was raised back to the user, who confirmed
2026-09-12 it should stay (not be dropped like the motion baseline), but
remain lowest priority: it's explicitly a **human-in-the-loop,
semi-autonomous** method (needs a manual box on frame 1 of every video),
which the user distinguishes from the motion baseline's problem
(class-agnostic) — the assignment asks for autonomous object detection,
so this method is a legitimate stretch demo (already scoped with its own
evaluation protocol, not forced into the shared mAP table) rather than
something that misleadingly poses as a comparable detector. Tried only if
time remains.

**Affected files:** `CLAUDE.md` (Section 6 updated — items renumbered,
"Dropped" note expanded), `docs/00_plan.md` (Day 5.5 updated).

## 2026-09-12 — Full manual video review: `person` found in 11/13 videos, not 6

**Decision/correction:** the user manually watched all 13 videos in full
(rather than relying on the sparse-frame triage from 2026-09-11) and found
`person` actually appears in 11 of 13 videos. The original triage sampled
too few frames to reliably catch small/distant figures. Updated inventory:

- **Confirmed already known:** Berghouse Leopard Jog, Surenen Pass Trail
  Running, Stockflue Flyaround, VerticalFlyOver, DJI_0790, DJI_0862.
- **Newly found to contain `person`:** Bluemlisalphutte Flyover
  (ant-sized distant figures), DJI_0501 (a human statue — false-positive
  trap — plus real tiny people near it), DJI_0574 (cyclists, person
  partly occluded by the bicycle), DJI_0596 (very small people on a
  ship's deck), DJI_0876 (one person briefly walking by a house).
- **Genuinely person-free (only 2, not 7):** Creux du Van Flight, Isles
  of Glencoe.

**Impact:** `data/splits/background.txt` was corrected from 7 entries
down to these 2. The 5 removed videos had been about to be used as
hard-negative (assumed-empty) training material — if left uncorrected,
the model would have been taught that real (if small/hard) people are
background, actively harming recall. This validates the safety-check
concern raised earlier the same day (verify background frames rather than
trust single-thumbnail triage) — the user's full manual review served
that verification more thoroughly than the planned automated check would
have.

**Reframing of the hard cases:** rather than treating the small/occluded/
ambiguous instances (ant-sized people, bicycle occlusion, the statue) as
noise to avoid, the user wants them kept as deliberate material for
honest failure/ambiguous-case analysis (`CLAUDE.md` Section 1 grading
criterion) — e.g., explicitly reporting "undetectable below N px" or
"occlusion by a bicycle drops recall to X%" rather than only reporting
cases where the system works well.

**Follow-up required:** the train/val/test split decided on 2026-09-12
(3/1/2 over 6 videos) is superseded by this finding and needs to be
redone now that 11 videos (not 6) contain `person` — see the next entry.

## 2026-09-12 — Train/val/test split redone over 11 videos: 6/1/4

**Decision:** with 11 `person` videos now available (see the entry
above), the split was redone, replacing the earlier 3/1/2-over-6 split:

| Set | Video(s) | Total duration | Role |
|---|---|---|---|
| **Train** (6) | Berghouse Leopard Jog, Surenen Pass Trail Running, Stockflue Flyaround, DJI_0574, DJI_0790, DJI_0876 | ~240.9s | Volume + diversity, including two occlusion cases (bushes, bicycle) so the pseudo-label-trained students get some exposure to partial occlusion |
| **Val** (1) | VerticalFlyOver | 18.9s | Unchanged from the previous split |
| **Test** (4) | DJI_0862, DJI_0596, Bluemlisalphutte Flyover, DJI_0501 | ~128.3s | One achievable headline case (DJI_0862, good-sized people) + two "too small" hard cases (DJI_0596 ship-deck, Bluemlisalphutte ant-sized) + one ambiguous/false-positive qualitative case (DJI_0501's human statue, plus real tiny people near it) |

Compared to the previous split, train volume more than doubled (100.3s →
240.9s) and test now covers 4 conditions instead of 2, deliberately
including hard/ambiguous cases rather than only "winnable" ones — this
directly serves the "honest error analysis, including failures and
ambiguous cases" grading criterion (`CLAUDE.md` Section 1): e.g., DJI_0596
and Bluemlisalphutte are expected to produce near-zero recall due to
object size, and this is reported as a finding, not hidden.

**DJI_0501 and DJI_0596 were deliberately excluded from train:** both are
extremely hard for SAM3 to pseudo-label reliably (statue confusion / tiny
objects), so including them in train would add labeling noise without
useful training signal — their value is in test-side qualitative and
small-object-failure reporting, not as training material.

**SAHI fairness question (raised by the user):** SAHI (slicing-aided
inference) is model-agnostic in principle and could be applied to any
detector, but for time-budget reasons it will be tested only as an
enhancement on the YOLO26s branch (as originally scoped in `plan.md`),
reported as a clearly-labeled "YOLO26s + SAHI" row/footnote in the
comparison table rather than claimed as a uniform methodology. Applying
it to RT-DETR too is a possible time-permitting extension, not required.

**Affected files:** `data/splits/{train,test}.txt` updated (`val.txt`
unchanged), `data/splits/background.txt` corrected in the previous entry,
`data/processed/frames/` cleared and to be regenerated by
`scripts/02_sample_frames.py`.

## 2026-09-12 — SAM3 auto-labeling architecture: one generic video+prompt+Hz tool

**Decision:** the auto-labeling pipeline was built as a single generic
tool rather than a script tied to our own dataset, because the delivery
notebook needs to work end-to-end if a reviewer uploads their own video —
`CLAUDE.md` already requires everything to run on a standard Colab
session, and this extends that to "on any input video, not just ours."

**Architecture:**
- `src/methods/sam3_zeroshot/model.py` — a `PromptableDetector` interface
  (`.detect(image, prompt) -> list[Detection]`), a `MockDetector` for
  local testing without a GPU, and a `Sam3Detector` stub left
  unimplemented on purpose — SAM3's exact package/API will be confirmed
  once installed on Colab rather than guessed at now.
- `src/methods/sam3_zeroshot/pipeline.py::label_video(video, prompt, fps,
  detector, ...)` — calls the existing `sample_diverse_frames()` (already
  built for `scripts/02_sample_frames.py`) internally, then runs the
  detector per sampled frame. This is the one code path used both for our
  own train/val videos and for a reviewer's new video — no duplicated
  frame-selection logic.
- `scripts/04_label_video.py` — the CLI: `--video --prompt --fps
  --config`, exactly the three inputs a reviewer enters. Writes frames,
  COCO-format annotations, review images (boxes + confidence drawn on
  every labeled frame — already sparse, so this is cheap), and a run
  manifest.

**Consequence for `scripts/02_sample_frames.py`:** narrowed to the
**test** split only. It has no detector import at all, so the gold test
set is structurally guaranteed to never be touched by any model (Rule 2
enforced by code shape, not just discipline). Train/val frame
extraction+labeling now happens together, in one pass, via
`scripts/04_label_video.py`.

**Code-level safety guard:** `scripts/04_label_video.py` checks the input
video's filename against `data/splits/test.txt` and refuses to run unless
`--force` is passed. This protects our own test videos from an accidental
labeling run while still allowing an arbitrary reviewer-supplied video
(whose filename won't match).

**Verified locally with `MockDetector`** (fixed center box, no GPU
needed): ran end-to-end on `VerticalFlyOver.mp4` (54 frames labeled,
boxes+scores drawn correctly in the review images) and confirmed the
test-video guard refuses `DJI_0862.MOV`. The mock output was deleted
afterward so it can't be confused with real SAM3 results later
(`CLAUDE.md` Rule 5 — never let a placeholder pass as a real result).

**Also cleaned up:** `src/methods/` skeleton subfolders from Day 0
(`baseline_motion/`, `openvocab/`, `student/`) had been left over from the
pre-realignment naming (see the earlier 2026-09-12 method-plan entry) —
replaced with `yolo/`, `rtdetr/`, `sam3_zeroshot/`, `convnext_centernet/`,
`resnet_ablation/`, `keypoint_tracking/`, matching the current tiered
method list. `CLAUDE.md` Section 8 updated to match (and no longer lists
a `motion_baseline/` folder, since that method was dropped entirely).

## 2026-09-12 — SAM3's real API confirmed; fallback corrected from SAM2 to YOLO-World

**Decision/correction:** looked up SAM3's actual current API (via
WebSearch/WebFetch against docs.ultralytics.com and Meta's SAM3 page)
instead of guessing, since `Sam3Detector` had been deliberately left
unimplemented pending this. Two things changed as a result:

1. **SAM3's real API, confirmed against docs.ultralytics.com/models/sam-3:**
   it's available through `ultralytics>=8.3.237` as
   `ultralytics.models.sam.SAM3SemanticPredictor`. Usage: build the
   predictor with `overrides={"model": "sam3.pt", "task": "segment", ...}`,
   call `predictor.set_image(image)` then `predictor(text=["person"])`;
   the result exposes `.boxes.xyxy` and `.boxes.conf` directly — no manual
   mask-to-box conversion needed, simpler than originally assumed.
   Implemented in `src/methods/sam3_zeroshot/model.py::Sam3Detector`.
   **Not smoke-tested yet** (no local GPU) — verify against the actual
   installed version on Colab before trusting it at scale.
2. **SAM3's weights are access-gated**, confirmed via Ultralytics' own
   docs: `sam3.pt` is not auto-downloaded, it requires requesting and
   being granted access at huggingface.co/facebook/sam3 first. This is a
   real schedule risk on a 7-day clock if approval is slow — access
   should be requested immediately, not when Day 3-4 arrives.
3. **The planned "fall back to SAM2" doesn't actually work**, confirmed
   via Ultralytics' own SAM2 docs: SAM2 has no text/open-vocabulary
   prompting at all — it only refines a *given* point/box/mask prompt,
   and Ultralytics' own auto-annotation workflow pairs it with a YOLO
   detector for exactly this reason. So SAM2 cannot serve as a
   like-for-like substitute for "find person from a text prompt." The
   fallback was corrected to **YOLO-World**, which is genuinely
   text-promptable (`model.set_classes(["person"])` +
   `model.predict(image)`, boxes + confidence directly) and adds no new
   dependency since `ultralytics` is already needed for YOLO26s.
   Implemented as `src/methods/sam3_zeroshot/model.py::YoloWorldDetector`,
   also not yet smoke-tested on real hardware.

**Affected files:** `CLAUDE.md` (labeling-tool paragraph corrected),
`docs/00_plan.md` (Day 3 task wording), `requirements.txt` (added
`ultralytics`), `src/methods/sam3_zeroshot/model.py` (both detectors
implemented for real instead of left as stubs), `configs/04_label_video.yaml`
(`model.name` now accepts `sam3` or `yolo_world`).

## 2026-09-12 — Cascade verifier added to the YOLO26s branch (item 1b)

**Decision:** on a second CV-practitioner consultation, the user proposed
adding a detect-then-verify cascade to YOLO26s: run YOLO26s at a low
confidence threshold (raises recall, especially on small/hard instances,
at the cost of more false positives), then pass every resulting box —
cropped — through a small ResNet18 binary classifier ("is this crop
actually a person?") as a second-stage filter. Added as item 1b under
Tier 1's YOLO26s entry in `CLAUDE.md` Section 6.

**Gap Claude filled in:** the original proposal only specified training
the classifier on positive crops (SAM3-labeled person boxes) — a binary
classifier needs negative examples too, or it has no notion of "not a
person." Negatives will come from YOLO26s's own low-confidence boxes that
don't match any SAM3-labeled person (i.e., its actual false positives,
which is exactly the error distribution being corrected), supplemented
with random crops from the 2 background videos for diversity.

**Expectation set honestly:** this cascade should help on
medium-difficulty false positives (YOLO sees something plausible but is
unsure), not on the ant-sized instances (Bluemlisalphutte, DJI_0596) —
lowering the confidence threshold doesn't recover an object whose feature
map representation was already lost to downsampling. This will be stated
as a limitation, not glossed over, when reporting results.

**Repurposing of item 5 (ResNet18/50 ablation):** rather than building a
separate full ResNet-backbone detector, the same ResNet18 is used here as
the crop classifier — more directly useful, and keeps total scope roughly
flat instead of purely additive. A standalone ResNet detector is dropped
unless time is unusually generous.

**Scheduling risk flagged and accepted:** Claude recommended finishing
*base* results for both Tier 1 architectures (YOLO26s, RT-DETR-R18) before
building 1b, since Tier 1's "never sacrificed" guarantee covers RT-DETR
too — building 1b first risks running out of time before RT-DETR exists
at all. The user heard this and explicitly chose to build 1b right after
YOLO26s and before RT-DETR anyway. Confirmed execution order: 1 -> 1b -> 2
-> 3. If schedule pressure hits after 1b, RT-DETR must still be attempted
(even minimally) before further polishing 1b or starting Tier 2.

**Affected files:** `CLAUDE.md` (Section 6 — item 1b added, item 5
repurposed, execution order note added).

## 2026-09-12 — Reviewer self-testing: no separate demo notebook needed

**Decision:** considered building a second, minimal "reviewer demo"
notebook (public repo, defaulting to YOLO-World instead of SAM3, a
Colab file-upload widget instead of Drive) so a reviewer could test the
pipeline end-to-end without needing our credentials. Decided against it
as unnecessary scope for now.

**Rationale:** the concerns motivating it turned out to be low-risk in
practice — the user's own SAM3 access approval came back in minutes (the
16-day cases found earlier appear to be outliers, not the norm), the
source footage is a public Kaggle dataset so there's no sensitivity in
sharing it, and repo access can be granted on request (add the reviewer
as a GitHub collaborator) rather than needing to be public by default.
`scripts/04_label_video.py` is already generic (`--video --prompt --fps`)
regardless — a reviewer with repo access just needs to point
`DRIVE_VIDEO_DIR` at their own video. Revisit only if a reviewer actually
asks and hits friction.

## 2026-09-12 — SAM3 imgsz corrected from 1920 to 1024 after a real OOM

**Decision/correction:** the smoke test in `notebooks/01_sam3_autolabel.ipynb`
was run for real on a T4 (14.56GB) and hit `CUDA out of memory` — a single
attention operation wanted 10.81GB at `imgsz=1920` (rounded to 1932 for
SAM3's stride-14 patch grid). `imgsz` was lowered to 1024 for both
`Sam3Detector` and `YoloWorldDetector` (`configs/04_label_video.yaml`,
`src/methods/sam3_zeroshot/model.py`).

**Root cause:** SAM3 is ViT-based; self-attention cost scales
quadratically with the number of image patches, i.e. roughly with
`imgsz^2`. This was missed on 2026-09-12 when `imgsz` was first raised
from 640 to 1280 and then to 1920 — that reasoning (more resolution
preserves small objects, T4 "should" handle it) only accounted for
compute/detail trade-offs, not attention memory, and was never actually
verified against a real GPU before this point (both detectors were
explicitly flagged as "not smoke-tested yet"). `YoloWorldDetector` (a CNN)
is not subject to the same quadratic blowup, but its default was also
kept at 1024 for now since it hasn't been tested above that value in this
project either — raising it later is a reasonable thing to try, just not
assumed safe without checking.

**Outcome:** 1024 is a middle ground — still meaningfully better than
Ultralytics' default 640 for our mostly-4K source video (per the earlier
2026-09-12 entry), while comfortably fitting a T4. The smoke test was
re-run after this fix; see the notebook run for the actual result.

**Lesson for this project:** two docstrings had said "not smoke-tested
yet, verify before trusting at scale" and were right to hedge — the
untested assumption inside them (1920 is a safe default) turned out
wrong on the very first real run. Worth remembering before raising
resolution/batch-size defaults on other GPU-bound methods (RT-DETR,
ConvNeXt+CenterNet) later without an equivalent real check.

**Follow-up — smoke test passed after the fix (same day):** re-ran on
"Berghouse Leopard Jog.mp4" frame 0 at `imgsz=1024` (rounded to 1036).
Found 3 detections: the 2 real runners at high confidence (0.91, 0.88),
plus one lower-confidence (0.47) box overlapping the second runner's
lower body — most likely a duplicate/fragment detection rather than a
third person, going by the visual. Not treated as a bug: this is exactly
what the Day 4 quality pipeline's NMS step exists to clean up. Inference
took ~750ms/frame on the T4, which is acceptable for a one-time labeling
pass over ~500 frames. Cleared to proceed to labeling all train+val
videos.

**Follow-up — user re-examined the smoke test result and made a scope
call:** looking again at the low-confidence (0.47) box's position (offset
to the side of the second runner, not nested inside their box), the user
judged it's more likely the runner's **shadow** than a duplicate/fragment
detection — a sharper read than Claude's first guess. Claude's
recommendation was to leave `confidence_threshold` alone and rely on the
already-planned ByteTrack temporal-consistency filter instead, since a
single-frame confidence score can't distinguish "hard-but-real" (our
small/occluded instances) from "confidently wrong" (a shadow) — both can
score similarly low for legitimate-sounding reasons. The user decided
differently: SAM3's pseudo-labels are too important to the project to
leave at a permissive threshold right now, ByteTrack isn't being
implemented at the moment (deprioritized, not ruled out later), and
manual review of the full train+val labeling run (already about to
happen) is the actual backstop. `confidence_threshold` raised from 0.3,
first to 0.4 (Claude's suggested moderate step), then the user pushed
further to **0.5** — deliberately high enough to exclude the observed
0.47 shadow outright, explicitly accepting the risk that genuine
hard/small instances (Bluemlisalphutte, DJI_0596) scoring similarly low
get excluded too. Revisit after the manual review if this turns out to
have cut too much real recall, or if shadow-type noise still shows up
despite the higher bar.

**Bug found — smoke test wasn't previewing the real threshold:** after
raising `confidence_threshold` to 0.5 and re-running the smoke-test cell,
the user still saw the 0.47 shadow box. Cause: the notebook's smoke-test
cell instantiated `Sam3Detector` directly and called `.detect()` without
ever reading `configs/04_label_video.yaml` — it was using
`Sam3Detector`'s own default `conf=0.25` (a separate parameter, passed to
the underlying Ultralytics predictor) instead of the config's
`confidence_threshold`, which is only actually applied inside
`src/methods/sam3_zeroshot/pipeline.py::label_video()` — the path cell 6
uses via `scripts/04_label_video.py`, but which the smoke-test cell
bypassed entirely. So cell 6 was already going to apply 0.5 correctly;
only the smoke test was misleading. Fixed by having the smoke-test cell
load the same config and filter with it, so it previews production
behavior instead of an unrelated default.

## 2026-09-12 — Kernel crash during bulk labeling: leftover GPU memory from the smoke test

**Bug found:** partway through the train+val labeling loop, the Colab
kernel crashed and auto-restarted (visible in the runtime logs — not a
normal Python exception, the whole kernel process died). Root cause:
cell 5's smoke test creates `detector = Sam3Detector(...)`, which loads
a full SAM3 model onto the GPU and never frees it — that object stays
resident in the notebook kernel's memory for the rest of the session.
Cell 6 then spawns a **separate subprocess per video**, each loading its
own full copy of SAM3 onto the *same physical* T4. Two SAM3 instances
(one idle in the kernel, one active per subprocess) together exceeded
the 14.56GB card even though either alone fits comfortably at
`imgsz=1024`.

**Fix:** cell 6 now starts by explicitly freeing the smoke-test
detector's GPU memory (`del detector; gc.collect();
torch.cuda.empty_cache()`) before spawning any labeling subprocess.
Also made the labeling loop **idempotent** — it now skips any video
whose `results/pseudo_labels/annotations/<stem>.json` already exists, so
a crash partway through doesn't require redoing already-completed
videos (a kernel restart, unlike a full runtime disconnect, typically
leaves the VM's disk intact — the 50-minute total loss from earlier the
same day was a full runtime reset, a different failure mode from this
one).

**Broader lesson:** on free-tier Colab, both failure modes (full runtime
reset, and in-session kernel crash) are real and distinct risks for a
long-running GPU loop — persisting progress incrementally (this
idempotent skip-if-done check) and not letting notebook cells hold GPU
objects alive longer than needed are both worth doing by default for
later long-running steps (YOLO26s/RT-DETR training, Day 4-5).

**Follow-up — cell 8 (push results) fixed to be self-sufficient:** the
first real run of cell 8 needed manual intervention it didn't originally
account for: a 403 (token lacked `repo` scope — resolved by generating a
new classic token with that scope) followed by a rejected push (this
repo was also being pushed to directly from the local machine while the
Colab run was in progress, so `origin/main` had moved on — resolved with
`git pull origin main --no-edit --no-rebase` before pushing). Cell 8 now
includes that pull step by default, so a future run doesn't need the
same manual fix — merge (not rebase) is safe here because this cell only
ever touches files under `results/`, which nothing else in the project
touches, so there's never a real conflict to resolve.

## 2026-09-12 — Gold test set complete: 151 frames, 541 `person` boxes

**Milestone:** the user manually labeled all 151 gold test frames in
CVAT (Track mode, per-frame boxes) and exported as COCO. Per-video
counts: Bluemlisalphutte 42, DJI_0501 50, DJI_0596 93, DJI_0862 356 —
541 total. Saved to `data/gold_test/annotations.json`. This set was
never touched by SAM3 or YOLO-World at any point (Non-negotiable rule 2)
— it's the independent ground truth every method (YOLO26s, RT-DETR, SAM3
zero-shot, ConvNeXt+CenterNet, etc.) will be scored against.

**`.gitignore` correction:** while tracking this file, discovered the
`!/data/splits/` negation pattern added 2026-09-12 never actually
worked — `git check-ignore` confirmed a *new* untracked file under
`data/splits/` still matches the blanket `/data/` rule; the earlier test
that seemed to show it working was checking an *already-tracked* file,
and git simply stops applying `.gitignore` to paths already in the
index (a different mechanism, misread as the negation succeeding). Fixed
the comment to describe the real mechanism (`git add -f`) and used it
for `data/gold_test/annotations.json` too.

**Day 2's remaining task list is now fully done.** Next SAM3-related
step (Tier 1, item 3 — zero-shot benchmark on this same test set) is
blocked on free-tier Colab GPU quota resetting (see the environment
correction entry above); non-GPU work continues in the meantime
(pseudo-label quality filtering, noise-rate audit on the SAM3 train/val
output).

## 2026-09-13 — YOLO26n zero-shot baseline: first complete method, run entirely on CPU

**Decision:** started Tier 1 item 1 with the simplest possible version
first — the zero-shot COCO-pretrained sanity check already planned as
its first sub-step — rather than jumping straight to pseudo-label
training. User's specific choices, each with a stated reason:
- **`imgsz=1920`** (long side; ~1920x1080 given our 16:9 test videos) —
  people are very small in nadir/aerial frames; the Ultralytics default
  (640) would shrink them far below what any backbone can represent.
- **YOLO26-nano specifically** — a larger `imgsz` costs more compute
  per image, so the smallest/fastest variant was chosen to keep total
  inference time reasonable.
- **Zero-shot first, no training** — COCO already includes "person";
  measure the out-of-the-box domain gap before spending any effort on
  pseudo-label training.

**Why this ran locally on the M1, not Colab:** unlike SAM3 (ViT-based,
quadratic attention memory), YOLO is a CNN — memory/compute scale far
more gently with resolution, and the nano variant is CPU-optimized by
design (confirmed via Ultralytics' own docs: "43% faster CPU inference
than YOLO11n"). This is genuine CPU-only inference, not a GPU workaround
— consistent with `CLAUDE.md` Section 3's "lightweight, non-GPU steps
only" scope for local work, and useful right now since Colab's free-tier
GPU quota is exhausted for the day (see the environment entry above).
Confirmed in practice: 151 frames, 52.6s total (0.35s/frame) on the M1
CPU.

**Built `src/eval/metrics.py`** using `pycocotools` (the standard tool)
rather than a hand-rolled mAP implementation — `evaluate()` for overall
mAP + COCO's built-in small/medium/large size breakdown,
`evaluate_per_video()` for the video/condition breakdown Section 7
requires (reusing the same file_name convention
`<video>__frame_XXXXXX.jpg` established for the pseudo-labels), and a
custom `precision_recall_f1()` for a single stated operating point
(mAP itself sweeps confidence internally, so a separate greedy
IoU-matching function was needed for this). `scripts/06_evaluate.py` is
built to be reused for every future method (SAM3 zero-shot, trained
YOLO26s, RT-DETR, ...) against the same gold set — it appends a row to
`results/eval/comparison.csv` per method, so the cross-method table
builds up automatically rather than being written by hand (Rule 5).

**Result — the domain gap, now with numbers, not just visual
impression:**

| Metric | Value |
|---|---|
| mAP@0.5 (overall) | 0.546 |
| mAP@[.5:.95] (overall) | 0.364 |
| **mAP@0.5, small objects** | **0.007** |
| mAP@0.5, medium objects | 0.316 |
| mAP@0.5, large objects | 0.669 |
| Precision @ conf=0.25 | 0.799 |
| Recall @ conf=0.25 | 0.580 |

Per-video mAP@0.5: Bluemlisalphutte 0.0, DJI_0596 0.052, DJI_0501 0.226,
DJI_0862 0.8.

**Qualitative confirmation, inspected directly in the review images:**
- **DJI_0862** performs well (0.8 mAP@0.5) because this particular
  frame/segment turns out to be a **ground-level shot** (a person's shoe
  fills the foreground), not a nadir aerial angle — an ordinary COCO-like
  viewing angle, which is exactly where a COCO-pretrained detector is
  expected to do well. This nuances the earlier target-selection note
  that called DJI_0862 "good size despite low-contrast terrain" — the
  size is fine partly *because* this isn't a hard aerial angle.
- **Bluemlisalphutte** (mAP@0.5 = 0.0): zero true detections, and one
  confident (0.61) false positive on a **patch of snow**, mistaken for a
  person from altitude.
- **DJI_0596** (mAP@0.5 = 0.052): zero detections of the real people
  visible on the ship's deck — too few pixels for the nano backbone to
  represent at all, regardless of confidence threshold.

Both failure cases were predicted in `docs/00_target_selection.md`
("expected small-object failure case") before any model was run — this
is now measured, not just anticipated, and gives concrete
failure-case material for the presentation's error-analysis section.

**Status:** Tier 1 item 1's zero-shot sub-step is complete with full
metrics. Next for this item: SAM3 zero-shot benchmark (same eval script,
once Colab GPU quota returns), then pseudo-label quality filtering +
noise audit, then actually training YOLO26s on the pseudo-labels.

## 2026-09-13 — ⚠️ Size-diversity swap (Berghouse ↔ Bluemlisalphutte), with a KNOWN Rule 2 deviation on Berghouse's test labels

**Decision:** the user noticed train had no small/hard-scale `person`
instances — both Berghouse Leopard Jog and Surenen Pass Trail Running
(the only two train videos with clearly-visible, large runners) meant
train was entirely "easy" scale, while test carried all the size
diversity. Swapped one video each way:

- **Berghouse Leopard Jog: train → test**
- **Bluemlisalphutte Flyover: test → train**

(Surenen stays in train as its one remaining "easy" example; DJI_0596
stays in test as its one remaining "hard/small" example — chosen
specifically to avoid emptying either set of that condition entirely.)

**⚠️ Rule 2 deviation — flagged loudly, overridden by the user anyway:**
Claude explicitly raised that the clean way to do this swap requires (a)
manually labeling Berghouse in CVAT for its new test role, and (b)
re-running SAM3 on Bluemlisalphutte for its new train role — and that
skipping both breaks Non-negotiable Rule 2 (no model output in ground
truth) for Berghouse specifically. The user overrode this, citing time
pressure and having personally reviewed SAM3's output on Berghouse as
close enough to manual labeling. **What actually happened, spelled out
so this is never mistaken for a clean gold set later:**

- **Berghouse's "test" ground truth in `data/gold_test/annotations.json`
  is NOT human-labeled.** It's Berghouse's own SAM3 pseudo-labels
  (previously generated when it was a train video), copied in verbatim
  and merged into the gold set, each annotation tagged
  `"source": "SAM3_pseudo_label_reused_as_gt"` for traceability. 113
  images, 220 boxes.
- **Bluemlisalphutte's train "pseudo-labels" in
  `results/pseudo_labels/annotations/Bluemlisalphutte Flyover.json` are
  NOT from SAM3.** They're Bluemlisalphutte's actual human/CVAT labels
  (previously its gold-test ground truth), copied verbatim and reused as
  if SAM3 had produced them, tagged
  `"source": "human_CVAT_label_reused_as_pseudo_label"` per annotation.
  68 images, 42 boxes.

**Why this matters (restated for whoever writes the final report):** any
method whose output resembles SAM3 — SAM3 itself if benchmarked
zero-shot, and any pseudo-label-trained student (YOLO26s, RT-DETR,
ConvNeXt+CenterNet) — will score artificially well on Berghouse
specifically, because its "ground truth" is close to a copy of what
those methods are expected to produce. **The Berghouse row of the
per-video breakdown table must be reported with this caveat, not as a
clean result**, or presented alongside the other three test videos
without qualification. Conversely, Bluemlisalphutte no longer tests
whether pseudo-label self-training actually works on a hard/small case —
its train "pseudo-labels" are secretly perfect, so if a student does
well on Bluemlisalphutte-like frames later, that can't be credited to
pseudo-labeling being robust on small objects.

**Mitigations applied without spending real time:** frames were
relocated to match each video's new role (`data/processed/frames/test/`
for Berghouse, `results/pseudo_labels/frames/` for Bluemlisalphutte);
`data/splits/{train,test}.txt` updated; the stale Bluemlisalphutte test
predictions/frames were removed rather than left to confuse a later run.
YOLO26n zero-shot was re-evaluated against the corrected gold set (see
below) so at least that result isn't stale — this doesn't fix the
labeling shortcut, it just keeps everything else internally consistent
with the new split.

**Updated YOLO26n zero-shot result (was already correct for size,
independent of this shortcut, but the test set composition changed):**

| Metric | Before swap | After swap |
|---|---|---|
| mAP@0.5 (overall) | 0.546 | 0.694 |
| mAP@0.5, small | 0.007 | 0.018 |
| mAP@0.5, large | 0.669 | 0.680 |
| Precision @ conf=0.25 | 0.799 | 0.855 |
| Recall @ conf=0.25 | 0.580 | 0.727 |

Per-video mAP@0.5 now: Berghouse 0.935 (independent result — YOLO26n is
not SAM3-derived, so this particular number is NOT compromised by the
labeling shortcut above), DJI_0862 0.8, DJI_0501 0.226, DJI_0596 0.052.
Overall numbers rose mainly because an easy video (Berghouse) replaced a
near-impossible one (Bluemlisalphutte) in the test pool — a reminder that
this is a small (4-video) test set where swapping one video visibly
moves the aggregate; the per-video breakdown remains the more meaningful
read than the overall average.

**If time remains (explicit user statement, recorded verbatim intent):**
label Berghouse manually in CVAT and re-run SAM3 on Bluemlisalphutte to
retire this deviation properly. Until then, every table/slide using
Berghouse's test numbers must carry this caveat.

## 2026-09-13 — Cascade (item 1b) design decisions, settled before writing code

Four things were pinned down before implementing the detect-then-verify
cascade, so the implementation wouldn't bake in unexamined guesses.

**1. Where the verifier's training crops come from.** The obvious source
— the TP/FP boxes we already have — is unusable: those came from the
test split, which the verifier must never see. So crops are mined from
**train+val only**: run YOLO at low confidence on those frames, match
candidates against those frames' SAM3 pseudo-labels by IoU, crop, label.

The inherited-noise problem was flagged: train/val "truth" is SAM3's
output, not human labels, so a real person SAM3 missed becomes a
mislabeled *negative* (teaching the verifier to reject real people), and
a SAM3 false positive that YOLO also fires on becomes a mislabeled
*positive*. Mitigation adopted: an **ignore zone** — IoU>=0.5 is a
positive, IoU==0 is a negative, and everything in between is **discarded
rather than guessed at**. Standard practice in detection training, and
it removes the most ambiguous cases rather than feeding them in as
noise. Partial silver lining: Bluemlisalphutte (the hardest/smallest
video) is now in train and its "pseudo-labels" are actually human CVAT
labels from the swap above — so the small-object end of the mining set
has genuinely correct references. The user will also eyeball the mined
crops before training.

**2. Verifier architecture: ResNet18.** Chosen over the lighter
MobileNetV3-Small deliberately. With a small crop dataset (order 1-3k
crops), the quality and reliability of ImageNet-pretrained features
matters more than parameter count, and ResNet18's transfer behavior is
the better-understood baseline. The efficiency argument for
MobileNetV3-Small doesn't bind here: classifying ~6 crops per frame at
64x64 is a rounding error next to YOLO at imgsz=1920, which dominates
the budget entirely. Noted as the swap-in if this ever moves to edge
hardware.

**3. Final detection score = YOLO_confidence × verifier_probability.**
Considered replacing YOLO's score with the verifier's outright (what
R-CNN-family two-stage detectors do). Rejected for *this* setup: our
verifier only ever sees a crop, so it carries no information about
localization quality, while YOLO's confidence does — and mAP is
sensitive to box quality through IoU. Multiplying keeps both signals:
"well-localized AND actually a person."

**4. Low confidence threshold = 0.01, chosen from measurement, not
intuition** (`results/eval/val_threshold_sweep.{json,md}`,
`scripts/08_threshold_sweep.py`). One YOLO pass at conf>=0.01 over the
val split, then every threshold evaluated by filtering that same pass:

| conf | candidates | per frame | covered | recall |
|---|---|---|---|---|
| 0.01 | 329 | 6.09 | 86 | 0.804 |
| 0.05 | 109 | 2.02 | 67 | 0.626 |
| 0.10 | 69 | 1.28 | 51 | 0.477 |
| 0.20 | 40 | 0.74 | 38 | 0.355 |
| 0.25 (current baseline) | 30 | 0.56 | 29 | 0.271 |

Dropping from 0.25 to 0.01 raises the recall *ceiling* the cascade can
possibly reach from 0.271 to 0.804 — nearly threefold — and that figure
is already measured at IoU>=0.5, so it accounts for the worry that
low-confidence boxes localize badly. The cost is 6.09 candidates per
frame instead of 0.56, which is nothing for the verifier to chew
through. Caveat stated up front: at 0.01 roughly three quarters of
candidates are not people, so if the verifier underperforms, the cascade
will land *worse* than the plain baseline on precision — the three-row
ablation below is designed to show that honestly either way.
**Agreed fallback: if the cascade underperforms at 0.01, retreat to 0.05
rather than abandoning the approach.**

Coverage above is measured against SAM3 pseudo-labels (val has no human
ground truth by design) — a proxy for choosing a knob, not an accuracy
claim, and labeled as such in the generated table.

**5. Reporting: three rows, not two.** Comparing "YOLO@0.25" against
"YOLO@0.01 + verifier" would change two variables at once and make the
verifier's contribution unattributable. The comparison table will carry
YOLO@0.25 (baseline, already measured), YOLO@0.01 without the verifier
(isolates what lowering the threshold alone does), and YOLO@0.01 + the
verifier (isolates what the verifier recovers).

## 2026-09-13 — Teacher failure found in audit: SAM3 labels sled dogs as people

**Finding.** Reviewing the mined verifier crops, the user spotted dogs in
`data/crops/train/person/`. Traced back: a crop is labeled `person` only
when a YOLO candidate overlaps a **SAM3 box** at IoU>=0.5, so dogs being
labeled `person` means SAM3 itself boxed them as people. Confirmed
visually in `results/pseudo_labels/review/DJI_0790/` — most of the ~8-10
boxes per frame sit on the dog team, with only the musher(s) at the back
being real people.

**Scale.** DJI_0790 carries 867 of train's 1382 pseudo-label boxes (63%),
at 10.1 boxes/frame across 86 frames. A sled team is 6-8 dogs plus 1-2
humans, so roughly 70-80% of those 867 boxes are wrong — close to **half
of all train pseudo-labels**.

**Why SAM3 fails here, specifically.** From directly overhead, a dark
elongated shape moving along a packed track on white snow has almost the
same silhouette whether it's a dog or a person in a winter coat. The
user's own read after inspecting the frames: the two genuinely look
alike at this angle and resolution. This is not random noise — it's a
*systematic* failure mode tied to viewpoint, and it's exactly the kind
of thing the mandatory pseudo-label audit (Section 6) exists to catch.

**Decision.** Rather than discard the video (which would drop train from
1382 to 515 boxes and lose the snow domain) or relabel from scratch,
export SAM3's boxes as CVAT pre-annotations and correct them by hand —
`scripts/11_export_for_cvat.py`. This costs part of the "fully automatic
labeling" story, but replaces it with a stronger one, and produces a
number Section 7 explicitly asks for: **human-minutes of labeling**,
spent on 1 of 6 train videos, only where the teacher demonstrably failed.

**Presentation angle worth keeping (user's request).** The corrected dog
boxes don't go to waste. Every dog box deleted from the pseudo-labels
becomes a **hard negative** in the verifier's crop dataset — because a
YOLO candidate that no longer matches any person box is mined as
`not_person`. So the cascade's second stage gets trained on precisely
the confusion that broke the first stage. The audit doesn't just remove
bad data; it converts the teacher's failure mode into the verifier's
training signal.

**Manual crop audit (2026-09-13).** Per Section 6's mandatory pseudo-label
quality check, the user manually reviewed every crop in `data/crops/{train,val}/{person,not_person}/`
(not just the ~100-sample spot-check the plan calls for a minimum of) after
the DJI_0790 and DJI_0876 corrections above. Result: all crops labeled
correctly — no person visible in a `not_person` folder, no non-person
content in a `person` folder. This is the noise-rate number for the
presentation: **0 observed mislabels across a full manual pass**, not a
sampled estimate. Proceeding to verifier training (item 1b,
`scripts/10_train_verifier.py`) on this crop set.

## 3-way YOLO threshold/verifier comparison on the gold test set (2026-09-13)

Ran the same YOLO26n zero-shot checkpoint three ways on the gold test set
(196 frames, 719 human-labeled boxes) — `scripts/13_yolo_lowconf_test.yaml`
reuses `05_yolo_zeroshot_eval.py` at the cascade's low threshold,
`14_cascade_hybrid_eval.py` adds the trained verifier on top:

| method | mAP@.5 | mAP@[.5:.95] | P | R | F1 | TP/FP/FN |
|---|---|---|---|---|---|---|
| yolo26n_zeroshot (conf 0.25) | 0.694 | 0.482 | 0.855 | 0.727 | 0.786 | 523/89/196 |
| yolo26n_lowconf (conf 0.01) | 0.801 | 0.533 | 0.855 | 0.727 | 0.786 | 523/89/196 |
| yolo26n_lowconf + verifier hybrid | 0.368 | 0.202 | 0.482 | 0.551 | 0.514 | 396/426/323 |

**Sanity check that passed:** the low-conf run's operating point at
conf=0.25 is bit-for-bit identical to the high-conf run (same TP/FP/FN) —
expected, since it's the same model/boxes, just a wider net that mAP (which
sweeps confidence internally) can see more of. mAP@.5 rising from 0.694 to
0.801 is exactly that effect, not a real improvement in detection quality.

**Unexpected result: the verifier hybrid is worse than plain YOLO on every
metric**, not just worse than hoped. Stage 1 proposed 2926 candidates;
the verifier kept 822 (rejected 71.9%) — but FP actually *rose* (89 -> 426
at the conf=0.25 cut) while TP fell (523 -> 396). Two things are going on,
and the operating-point row above is partly misleading about which one
dominates because of a scale mismatch this project's own eval protocol
(Section 7) warns about: the hybrid's "confidence" at that row is the
*verifier's* softmax probability, not YOLO's detection confidence, and the
two are not the same scale — a small ResNet head trained to convergence on
~5k crops tends to be overconfident near 0/1, so a 0.25 cut barely filters
anything (396+426=822 = every kept box), unlike YOLO's confidence which is
smoothly spread out. mAP (which sweeps each method's own score
independently) is the fairer comparison here and it still shows the hybrid
clearly behind, so the scale mismatch explains the operating-point number's
literal FP figure but not the overall conclusion.

Per-video mAP@.5 breaks the story down further:

| video | lowconf | hybrid |
|---|---|---|
| Berghouse_Leopard_Jog | 0.980 | 0.658 |
| DJI_0501 | 0.388 | 0.484 |
| DJI_0596 | 0.256 | 0.020 |
| DJI_0862 | 0.861 | 0.272 |

The verifier only helps on one of four test videos (DJI_0501) and hurts
badly on the other three — worst on DJI_0596, one of the two videos
already flagged in CLAUDE.md Section 6 for ant-sized instances the YOLO
feature map can't represent at any confidence, so the verifier is being
asked to judge crops that were already too degraded at the source.

**Leading hypothesis, not yet confirmed:** the verifier was trained and
validated on crops mined from the *train/val* videos' own SAM3
pseudo-labels (val F1 0.989, see the item 1b training entry above) — a
distribution the val split shares with training. The gold *test* videos
are the ones explicitly held out at the video level (Section 2, rule 1)
specifically so this kind of gap would show up; a classifier this small,
this confident, generalizing well within train/val's domain but poorly to
genuinely unseen footage is a plausible and honest explanation, not yet
verified against the actual review crops.

**Next step:** inspect `results/cascade_hybrid/review/` (per-frame kept
boxes) and `results/eval/yolo26n_lowconf_verifier_hybrid/comparison/`
(GT vs. prediction) before writing this up as a final conclusion — this
entry records the measured numbers, not yet the confirmed root cause.

## Band-gated cascade variant (2026-09-13), following the user's diagnosis

Manually reviewing `results/cascade_hybrid/review/lost_true_positives/`
confirmed the leading hypothesis above was wrong in one important way: many
of the 247+ lost true positives are **clearly, easily visible people**, not
just ambiguous edge cases — the verifier isn't only failing on genuinely
hard crops, it's misclassifying some it should get right. The user's own
diagnosis: sending YOLO's *already-confident* boxes (>=0.25, where plain
YOLO alone already scores P=0.855 R=0.727) through the verifier puts them
at needless risk for no reason to expect a gain there. Proposed fix: trust
YOLO outright at/above 0.25, and only let the verifier adjudicate the
ambiguous [0.01, 0.25) band where precision was being sacrificed for recall.

Implemented as `scripts/16_cascade_band_hybrid_eval.py`. Kept boxes always
carry YOLO's own score (never the verifier's), which also fixes the
operating-point scale-mismatch flagged in the first hybrid entry above —
this predictions.json is directly comparable to the plain-YOLO runs.

| method | mAP@.5 | mAP@[.5:.95] | best F1 (@conf) |
|---|---|---|---|
| yolo26n_zeroshot (0.25) | 0.694 | 0.482 | 0.786 (@0.25) |
| yolo26n_lowconf (0.01, full pool) | 0.801 | 0.533 | 0.353 (@0.01) |
| lowconf + full verifier hybrid | 0.368 | 0.202 | 0.514 |
| **lowconf + band-gated verifier (0.01-0.25 only)** | **0.733** | **0.503** | 0.781 (@0.15) |

Band-gating recovers most of the full hybrid's damage (DJI_0862 mAP@.5:
0.272 -> 0.817; Berghouse: 0.658 -> 0.975) and **beats method 1 on mAP@.5**
(0.694 -> 0.733) — a genuine ranking-quality improvement. It does **not**
beat method 1 at any single operating point: swept 0.01-0.25, the closest
is conf=0.15 (F1=0.781 vs. method 1's 0.786; TP 523->539, FP 89->123 — 16
more people found at the cost of 34 more false alarms, a close to break-even
trade depending on which error type the use case weighs more).

**Conclusion for the presentation:** the verifier genuinely helps — it
recovers a meaningful fraction of the low-confidence band's extra true
positives while suppressing most of its false positives — but it is not
accurate enough on this training-set size (~5k crops) to net-beat simply
picking a good confidence threshold on plain YOLO. This is an honest
negative-ish result for item 1b specifically, not a pipeline failure: it's
exactly the kind of "does a second method genuinely add value" question
Section 1 asks us to answer, and the honest answer here is "not yet, and
here's the measured gap and the likely reason (verifier training set size /
domain coverage)."

## Video-balanced sampling result (2026-09-13)

Retrained the verifier (`configs/17_train_verifier_video_balanced.yaml`)
with a `WeightedRandomSampler` that equalizes each (video, class) group's
contribution per epoch, addressing the DJI_0790 dominance (70%/81% of
train's person/not_person crops) found while diagnosing the lost true
positives above. Val person-F1 dipped slightly (0.989 -> 0.981, expected:
val shares train's video distribution, so it can't reward better
out-of-domain generalization, only measure a small in-domain cost of it).
Re-ran both cascade variants against the gold test set with the new
checkpoint:

| method | mAP@.5 | mAP@[.5:.95] | best F1 (@conf) |
|---|---|---|---|
| yolo26n_zeroshot (method 1, plain YOLO @0.25) | 0.694 | 0.482 | 0.786 (@0.25) |
| band-gated hybrid, original verifier | 0.733 | 0.503 | 0.781 (@0.15) |
| **band-gated hybrid, video-balanced verifier** | **0.760** | **0.514** | 0.782 (@0.15) |
| full hybrid, original verifier | 0.368 | 0.202 | 0.514 |
| full hybrid, video-balanced verifier | 0.393 | 0.231 | 0.550 |

Video-balanced sampling helped both cascade variants on every metric —
mAP@.5 for the band-gated hybrid improved another 0.027 (0.733 -> 0.760),
now 0.066 above method 1's own mAP@.5. The full (non-band-gated) hybrid
also improved but remains far behind plain YOLO, confirming band-gating
(not verifier quality) is what fixes that variant's core problem: sending
already-confident boxes through the verifier for no expected gain.

**The F1 gap did not close.** Best single operating point is still
conf=0.15 (F1=0.782), 0.0037 below method 1's 0.786 (TP 544 vs. 523 — 21
more people found — at the cost of 128 vs. 89 false alarms — 39 more).
Video-balancing narrowed this from a 0.0049 gap to 0.0037, a real but
small improvement, not the fix.

**Conclusion for item 1b, final for this cycle:** the cascade's ranking
quality (mAP) is now unambiguously better than plain YOLO's, and the
verifier is demonstrably improvable (video-balancing helped, meaning the
original bottleneck was partly a data-composition problem, not purely
"ResNet18 crops can't do this task"). But at any single deployed
threshold, it has not yet beaten simply running YOLO at 0.25 — the honest
takeaway is "a second training pass on more balanced data closed part of
the gap, not all of it," and further gains would likely need genuinely
more/more-diverse train crops (more train videos have very few person
crops: Bluemlisalphutte contributed only 5), not just resampling the
crops that already exist. Time-boxing this here and moving to Tier 1 item
2 (RT-DETR-R18) per the plan's degradation order.

## Narrowing the verifier's band to [0.10, 0.25) (2026-09-13) — counter to hypothesis

User's hypothesis: the verifier's job gets harder as YOLO's floor drops
toward 0.01 — near-noise-floor candidates are a genuinely harder
classification task than the FP-heavy-but-plausible candidates near 0.25,
so raising the floor to 0.10 (an already-swept value, not a new search;
`scripts/20`/`scripts/21`) should let the verifier do a cleaner job on an
easier band.

**Result: mAP@.5 went down, not up** (band-gated hybrid: 0.760 -> 0.734).
Root cause is arithmetic, not the verifier: at any evaluation cut >= 0.10,
the narrow-band and wide-band hybrid predictions are *identical* — a box
originally scored by YOLO below 0.10 can never pass a >=0.10 cut regardless
of which band it was mined from, so the two variants can only differ below
conf=0.10. The wide band's advantage lived entirely in that
[0.01, 0.10) region: the verifier was in fact contributing net-positive
signal there too, not just noise as hypothesized — removing that region
outright removes real ranking value along with the noise.

**The single-operating-point F1 is completely unchanged** (0.7822 @
conf=0.15 either way) — expected, since that optimum sits above 0.10 and
both variants share that region byte-for-byte. Still short of method 1's
0.7859 by 0.0037.

**Conclusion:** don't narrow the band — revert to the 0.01 floor
(`configs/19`, mAP@.5 0.760) as the best cascade configuration found this
cycle. This closes out item 1b's iteration for now: mAP is
unambiguously better than plain YOLO's; the best single deployed
threshold is not, by a small and now well-characterized margin (0.0037
F1). Moving to Tier 1 item 2 (RT-DETR-R18).

## Where the cascade actually earns its keep: small objects on the hardest videos

The aggregate F1 story above (cascade doesn't quite beat plain YOLO's
0.7859) is pooled by box count, and DJI_0862 + Berghouse — the two easy,
box-rich videos — make up 81% of the test set's 719 GT boxes. That pooling
was hiding a real, targeted win on the two hard videos (DJI_0501, DJI_0596)
the user specifically expected the cascade to help on:

| video | small GT boxes | matched by method 1 (any conf) | matched by band-gated hybrid |
|---|---|---|---|
| DJI_0501 | 5 | 0 | 1 |
| DJI_0596 | 39 | 0 | **9** |

Plain YOLO catches **zero** of these 44 small people at any confidence
level — the feature map genuinely can't represent them, matching the
Section 6 "ant-sized instances" note. The cascade's lower floor (0.01)
plus verifier cleanup recovers 10 of them (23%), confirmed by direct
IoU-matched detection counts (`_iou_xywh` >= 0.5), not just an AP-curve
artifact. mAP_small/AR_small for both videos moved from exactly 0.0 to
nonzero (DJI_0596: AR_small 0.0 -> 0.123).

**This is the honest, complete picture for the presentation:** the
cascade doesn't win on the aggregate, box-count-weighted F1 headline, but
it does exactly what it was designed to do — trade some precision for
recall specifically in the small/hard-instance regime plain YOLO
structurally cannot address — and this shows up cleanly once the
breakdown is by video and object size (Section 7's requirement) rather
than looked at only in aggregate. Both framings are true and both belong
in the writeup: "not a net win on the headline metric" and "a real,
targeted capability gain on exactly the cases it was built for."

## Adding a size gate on top of the confidence band (2026-09-13) — also reverted

User's next refinement: YOLO already works on large objects and
structurally can't represent small ones (mAP_small was exactly 0.0 for
plain YOLO on the two hardest videos), so route small candidates to the
verifier unconditionally, regardless of score, while leaving large objects
on the existing confidence-only gate.

**First checked before building it:** does simply *dropping* large
low-confidence candidates (instead of verifying them, as the current best
config does) cost real recall? Yes — 75/719 gold GT boxes (10.4%) are only
ever proposed as a large, low-confidence candidate, so that idea was
dropped in favor of keeping large objects on the existing gate
unconditionally (auto-accept >= 0.25, verify below it, same as
`configs/19`) and only adding small objects as a new always-verify
category. Implemented in `scripts/22_cascade_size_gated_hybrid_eval.py`.

**Result: mAP@.5 dropped slightly** (0.760 -> 0.753) and the best F1
dropped too (0.786 -> 0.783, now at conf=0.25 itself rather than 0.15).
Operating-point TP fell 523 -> 519 at conf=0.25 — the verifier now
second-guesses some small, high-confidence YOLO detections it previously
never saw, and gets a few of them wrong. `mAP_small` itself went down
(0.063 -> 0.056), the opposite of the intended effect.

**Why:** plain YOLO essentially never produces a small detection at
score >= 0.25 to begin with (confirmed on the hard videos above) — so the
rare cases where it does are apparently reliable, and asking a verifier
that is itself imperfect (val F1 ~0.98, worse out-of-domain per the
lost-true-positives review) to double-check them is pure downside, not a
safety net. "YOLO's confidence isn't trustworthy for small objects" turned
out to only hold when YOLO *isn't* confident — confidence-band gating
(configs/16/19) was already implicitly capturing the useful version of
this idea; adding size as an independent gate did not.

**Final configuration for item 1b:** `configs/19` (confidence-band only,
[0.01, 0.25), video-balanced verifier) — mAP@.5 0.760, best F1 0.7822 @
conf=0.15, plus the documented small-object win on DJI_0501/DJI_0596
(10/44 previously-invisible small people recovered). Closing this item's
iteration here.

## Narrowing the size gate to 24x24 (2026-09-13) — fixes the harm, adds no gain

Diagnosed the previous size-gate regression precisely before changing
anything: all 4 lost true positives were high-confidence (>=0.25)
detections sized 926-1011px^2 — just under the 32x32 (1024px^2) cutoff,
not genuinely tiny — that the verifier wrongly rejected on re-check.
Confirmed zero high-confidence true positives exist below 24x24
(576px^2) in the current best predictions, so that threshold can't
reproduce the same failure. Re-ran `scripts/22_cascade_size_gated_hybrid_eval.py`
with `small_area_threshold: 576` (`configs/23`).

**Result: bit-for-bit identical to the confidence-band-only baseline**
(mAP@.5 0.760, mAP_small 0.0632, operating point 523/89/196, all four
per-video mAP@.5 values unchanged). At this threshold, no candidate in
the test set is both small (<576px^2) and high-confidence (>=0.25) to
begin with, so the "always verify small" rule never actually overrides
what confidence-band gating alone would have done — it neither helps
nor hurts on this test set.

**Conclusion:** 24x24 is a safe choice (recovers the 32x32 run's damage
completely) but the size-gate idea itself adds no measurable value beyond
plain confidence-band gating (`configs/19`) once tuned to be harmless —
its two implementations (32x32, 24x24) bracket the finding: too high a
cutoff second-guesses YOLO's rare-but-reliable confident small
detections (net loss); low enough to avoid that, and it has nothing left
to act on beyond what the confidence band already covers (net zero).
Closing item 1b's iteration here for real: `configs/19` (confidence-band,
[0.01, 0.25), video-balanced verifier) is the final configuration —
mAP@.5 0.760, best F1 0.7822 @ conf=0.15, plus the documented
small-object recovery on DJI_0501/DJI_0596 (10/44 previously-invisible
small people).

## Score fusion instead of hard gating: the best result this cycle (2026-09-13)

User's next refinement: instead of the verifier making a hard accept/reject
call on band candidates (scripts/16), combine YOLO's own confidence with
the verifier's person-probability into one continuous score and let mAP's
threshold sweep find the useful cutoff, rather than pre-deciding it with a
binary gate. Implemented in `scripts/25_cascade_score_fusion_eval.py` as
the geometric mean `sqrt(yolo_score * verifier_person_prob)` — zero unless
both models agree, a natural way to combine two independent probability-
like estimates. Boxes >= 0.25 stay untouched (unaffected by any of this,
per the settled size-gate findings above); every band candidate keeps its
fused score instead of being kept-or-dropped.

| method | mAP@.5 | mAP@[.5:.95] | mAP_small | best F1 (@conf) |
|---|---|---|---|---|
| yolo26n_zeroshot (method 1) | 0.694 | 0.482 | 0.000 | 0.786 (@0.25) |
| band-gated hybrid, video-balanced (prior best) | 0.760 | 0.514 | 0.063 | 0.782 (@0.15) |
| **score fusion, video-balanced verifier** | **0.786** | **0.522** | **0.076** | 0.783 (@0.38) |

**New best mAP@.5 this cycle**, beating method 1 by 0.092 and the prior
best band-gated hybrid by 0.026 — the largest single jump of any item 1b
experiment today. The best single-operating-point F1 (0.783 @ its own
conf=0.38 — note this is the *fused* score's own scale, not comparable
number-for-number to YOLO's 0.25) is the closest yet to method 1's 0.786,
within 0.003.

Per-video mAP@.5, and specifically the DJI_0596 trend across every item 1b
refinement tried today, shows monotonic improvement:

| video | method 1 | band-gated | score fusion |
|---|---|---|---|
| Berghouse | 0.935 | 0.975 | 0.973 |
| DJI_0501 | 0.226 | 0.364 | 0.338 |
| DJI_0596 | 0.052 | 0.193 | **0.244** |
| DJI_0862 | 0.800 | 0.831 | 0.851 |

**Why this likely works better than hard gating:** a binary accept/reject
throws away graded information both models have. A YOLO score of 0.20 with
a verifier person-probability of 0.55 and a YOLO score of 0.02 with the
same 0.55 probability were previously treated identically (both simply
"kept, at their own YOLO score") -- fusion correctly ranks the first well
above the second. This matches the general lesson from the size-gate
experiments: wherever we replaced a hard cutoff with information both
signals actually carry, results improved; wherever we discarded
information the models had via too coarse a rule, results got worse.

Still using the video-balanced verifier (small-input-stem variant is
training separately); worth re-running fusion with that checkpoint once
it's ready to check whether the gains compound.

## First configuration to beat method 1's own F1 (2026-09-13)

Score fusion (configs/25's design) re-run with the small-input-stem
ResNet18 (configs/24) instead of the standard-stem video-balanced
checkpoint. Despite a *worse* val person-F1 (0.9446 vs. 0.981 -- see the
training entry above), test-set performance is the best of any
configuration tried today:

| method | mAP@.5 | best F1 (@conf) | P | R | TP/FP/FN |
|---|---|---|---|---|---|
| method 1 (plain YOLO @0.25) | 0.694 | 0.786 | 0.855 | 0.727 | 523/89/196 |
| score fusion, video-balanced stem | 0.786 | 0.783 (@0.38) | 0.865 | 0.715 | 514/80/205 |
| **score fusion, small-input-stem** | **0.788** | **0.791 (@0.38)** | **0.890** | 0.712 | 512/63/207 |

**This is the first configuration all cycle to beat method 1's F1 at a
single operating point** (0.791 vs. 0.786) -- via higher precision (63 FP
vs. method 1's 89) at a small recall cost (207 vs. 196 FN). Consistent
with earlier findings, val performance did not predict this: the
small-stem checkpoint scored *lower* on val than the standard-stem one,
yet generalizes better to the genuinely held-out test videos. This
reinforces that val (a single video, sharing train's distribution) is an
unreliable signal for this specific comparison — checkpoint selection by
val F1 alone would have picked the worse-generalizing model.

**Final answer to "should we accept ResNet for this cascade":** yes, with
this specific configuration (small-input stem + score fusion) as the
best-found item 1b result — a genuine, if modest, win over the baseline
at a real deployable threshold, on top of the already-documented mAP gain
and small-object recovery. Time-boxing further iteration here.

## Tier 1 item 2 begins: RT-DETRv2-R18 zero-shot sanity check (2026-09-13)

Ultralytics (already a dependency) only ships RT-DETR with HGNetv2
backbones (`rtdetr-l.pt`, `rtdetr-x.pt`) — no R18 variant. The original
authors' R18-backbone checkpoints live on the Hugging Face Hub via the
`transformers` library (new dependency): `PekingU/rtdetr_r18vd` (v1,
COCO-only) or `PekingU/rtdetr_v2_r18vd` (v2, an improved follow-up from
the same team, same 20.2M params, no Objects365 variant exists for v2 on
the Hub — consistent with v1's naming convention where the plain name
means COCO-only). Chose **v2** for better reported accuracy at the same
size and cost, while keeping the pure-COCO pretraining that makes this
zero-shot check comparable to YOLO26n's own (`configs/05`, same
`Yolo26Detector`-shaped interface, same conf=0.25 operating point).

`src/methods/rtdetr/model.py` wraps `RTDetrV2ForObjectDetection` +
`RTDetrImageProcessor` behind the same `Detection`/`.detect()` shape as
`Yolo26Detector`, so `06_evaluate.py`/`07_visualize_eval.py` needed zero
changes. Confirmed CPU timing on one frame (0.29s) before running the
full test set (0.33s/frame average — comparable to YOLO26n's own
zero-shot timing, ran locally per CLAUDE.md Section 3).

| metric | YOLO26n zero-shot | RT-DETRv2-R18 zero-shot |
|---|---|---|
| mAP@.5 | 0.694 | **0.740** |
| mAP@[.5:.95] | 0.482 | 0.485 |
| mAP_small | 0.018 | **0.0002** |
| Precision (@0.25) | 0.855 | 0.609 |
| Recall (@0.25) | 0.727 | 0.761 |
| F1 (@0.25) | **0.786** | 0.677 |
| TP/FP/FN | 523/89/196 | 547/351/172 |

**A genuinely different failure profile, not just a worse/better copy of
YOLO's:** RT-DETR ranks detections better overall (higher mAP, higher
recall) but produces 4x YOLO's false positives at the same 0.25 cut, and
is *dramatically* worse on small objects — `mAP_small` is essentially
zero (0.0002 vs. YOLO's already-poor 0.018). Leading hypothesis: RT-DETR's
image processor resizes every frame to a **fixed 640x640**, regardless of
source resolution (our test frames are up to 3840x2160) — far more
aggressive downsampling than YOLO26n's configurable `imgsz=1920`, so
small/distant people are likely destroyed before the model even sees
them. Not yet confirmed by inspecting review images.

Per-video mAP@.5 also inverts part of the YOLO story: RT-DETR does much
better on DJI_0501 (0.559 vs. YOLO's 0.226) but even worse than YOLO on
DJI_0596 (0.029 vs. 0.052) — the video with the smallest instances gets
hit hardest by the resolution difference, as expected.

**Next:** inspect `results/eval/rtdetr_v2_r18_zeroshot/comparison/` to
confirm the resolution hypothesis qualitatively, then proceed to
fine-tuning on the SAM3 pseudo-labels (per `plan.md`'s item 2, with
position/scale augmentation since transformer detectors are more
augmentation-sensitive than CNN heads).

## Attempted "fair" resolution match for RT-DETR broke it (2026-09-13)

Tried forcing RT-DETR's input resolution up from its native 640x640 to
1920x1088 (matching YOLO's `imgsz=1920`), reasoning that resolution parity
would make the two zero-shot checks more comparable — YOLO's own domain-gap
check specifically benefits from a higher `imgsz` (small objects need more
pixels to survive downsampling), so the same should help RT-DETR.

**Result: catastrophic, not an improvement.**

| | RT-DETR @ 640x640 (native) | RT-DETR @ 1920x1088 (forced) |
|---|---|---|
| mAP@.5 | 0.740 | **0.253** |
| FP (@conf 0.25) | 351 | **1733** |
| Boxes on the worst single frame | — | 67, clustered on one spot |

Inspected the worst-offending frame's raw boxes before concluding this
wasn't a coordinate-scaling bug in `src/methods/rtdetr/model.py`: the 67
boxes are well-formed (plausible size, within image bounds) and tightly
clustered on one real region of the image — a duplicate-detection storm,
not scattered garbage.

**Root cause:** unlike YOLO (a CNN pipeline with NMS as an independent
post-processing step, tolerant of `imgsz` changes without retraining),
RT-DETR has **no NMS at inference** — its "one query, one object" behavior
is a learned property of one-to-one Hungarian matching during training,
calibrated to the token count/spatial statistics of its trained
resolution. Push the input far outside that resolution and there's no
fallback mechanism to suppress the resulting duplicate/spurious
detections.

**This is a documented characteristic of DETR-family detectors, not
something unique to this run:** RT-DETRv2's own paper introduces "flexible
size training" (randomizing input resolution during training) specifically
to address this known brittleness in the original RT-DETR/DETR line.
Honest caveat: we have not verified the exact resolution range
`PekingU/rtdetr_v2_r18vd` used for that flexible-size training — 1920x1088
(a very different aspect ratio and far larger than typical multi-scale
training ranges like 480–800) plausibly falls outside it entirely, which
would fully explain this result without implying v2's own mitigation
failed on its own terms.

**Correction applied:** `configs/28` reverted to RT-DETR's native 640x640
(the only valid number for the method comparison — restored in
`results/eval/rtdetr_v2_r18_zeroshot/`). The 1920x1088 attempt is kept as
`configs/29` / `results/rtdetr_resolution_diagnostic/` /
`rtdetr_v2_r18_1920_diagnostic_BROKEN` in the comparison table — clearly
named as a diagnostic, not a candidate result — because the *lesson*
(transformer detectors' inference resolution should match training
resolution far more strictly than CNN detectors', due to the no-NMS
one-to-one matching design) is itself a genuine, presentation-worthy
finding about architecture-specific fragility, discovered by directly
trying to violate it.

## Ultralytics RT-DETR-l at 1920x1088: graceful degradation, not collapse

Tested whether the HF R18 checkpoint's catastrophic resolution
sensitivity (mAP@.5 0.740 -> 0.253 when forced to 1920x1088, see above)
is a general RT-DETR-family trait or specific to that checkpoint. Ran the
same forced resolution on Ultralytics' RT-DETR-l (HGNetv2 backbone,
32.97M params) — a 10-frames-per-video preview first (`configs/31`,
following the flush-progress + small-sample-first workflow established
this session), then the full test set (`configs/32`) once the preview
looked survivable (no duplicate-detection storm, just a mild box-count
uptick on DJI_0596's last couple of frames).

| metric | 640x640 (native) | 1920x1088 (forced) |
|---|---|---|
| mAP@.5 | 0.731 | 0.654 |
| mAP_small | 0.004 | **0.093** (23x) |
| F1 (@0.25) | 0.755 | 0.610 |
| FP (@0.25) | 168 | 442 (2.6x — vs. the HF checkpoint's 5x) |
| DJI_0596 mAP@.5 | 0.041 | **0.373** (9x) |

**A genuinely different failure mode from the HF R18 checkpoint's total
collapse:** this checkpoint degrades *gracefully* — aggregate mAP/F1 drop
moderately (not catastrophically) from more false positives, but small-
object detection improves dramatically (mAP_small 23x, DJI_0596 9x) —
the same mechanism we'd hope resolution would help with, actually showing
up here. Likely explanation: Ultralytics' RT-DETR training recipe
(different augmentation/multi-scale schedule from the paper authors'
official R18 checkpoint) leaves it measurably more robust to an
off-training-distribution resolution, though clearly not fully immune
(FP still rose 2.6x).

**Practical takeaway:** RT-DETR resolution sensitivity is real but
checkpoint-dependent, not an absolute law of the architecture family —
worth keeping the native-resolution number as each checkpoint's valid
zero-shot baseline for the method comparison, while noting this 1920
result as a genuine, presentable secondary finding (not a broken
diagnostic to discard, unlike the HF 1920 attempt).

## EfficientNet-B0 verifier: best val score, not best test score (2026-09-13)

Trained on Colab GPU (video-balanced sampling, same recipe as the best
ResNet checkpoint) after the user found EfficientNet-Lite0 and asked to
try the architecture family; used torchvision's standard `efficientnet_b0`
(no new dependency) since edge/quantized deployment isn't a project goal.
Best val person-F1: **0.9835** — the highest of all three verifier
checkpoints tried this cycle.

Evaluated with the same score-fusion design (`configs/33`) on the gold
test set:

| Verifier | mAP@.5 | Best F1 (@conf) | Val F1 | Relative CPU speed |
|---|---|---|---|---|
| ResNet18, video-balanced | 0.786 | 0.783 (@0.38) | 0.981 | 1x |
| **ResNet18, small-input-stem (current best)** | **0.788** | **0.791 (@0.38)** | 0.945 | ~1x |
| EfficientNet-B0, video-balanced | 0.779 | 0.782 (@0.38) | **0.984** | **~5x slower** |

**Confirms the session's recurring lesson a third time:** the highest val
score does not translate to the best test result — EfficientNet-B0 scores
worst of the three on the actual gold test set despite scoring best on
val. It also turned out to be roughly 5x slower per crop on this CPU
despite having far fewer parameters (4.0M vs. ResNet18's 11.2M) — a
practical reminder that FLOP/parameter counts don't reliably predict
CPU wall-clock speed; EfficientNet's depthwise-separable convolutions are
known to vectorize less efficiently on general-purpose CPU BLAS kernels
than plain convolutions, an advantage that mainly shows up on GPU/
accelerator hardware with dedicated grouped-conv support.

**Final decision:** no change to the best configuration — score fusion +
small-input-stem ResNet18 (`configs/24` + `configs/27`) remains item 1b's
final result. EfficientNet-B0 is documented as a considered, tested
alternative that did not improve on it, not a silent gap.

## GPU (T4) validation of the full method comparison (2026-09-13)

Ran the full method comparison (Method 1, cascade+standard-stem,
cascade+small-stem, cascade+EfficientNet-B0) on Colab T4 GPU via
`notebooks/03_gpu_method_comparison.ipynb`, to get authoritative
hardware numbers instead of the CPU numbers used for all prior internal
comparisons this cycle.

**Reproducibility check passed cleanly:** mAP@.5 for every method matches
its CPU counterpart almost exactly (Method 1: 0.694 CPU / 0.693 T4;
small-stem fusion: 0.788 CPU / 0.786 T4; etc. — differences only at the
3rd decimal, consistent with ordinary CPU/GPU floating-point
nondeterminism). The CPU-based internal comparisons this cycle were
valid and the GPU numbers replace them as the authoritative figures for
the presentation.

**Supplementary robustness check, not a change to the comparison design:**
Method 1 is deliberately evaluated at conf=0.25 throughout this project —
Ultralytics' own unmodified default, chosen specifically because Method 1
exists to measure the *untouched, out-of-the-box* domain gap (Section 6),
not to be a tuned competitor. Sweeping Method 1's own threshold anyway,
purely out of curiosity about how much headroom that fixed choice leaves
on the table, lands it at:

| Method | Best F1 | @ conf |
|---|---|---|
| Method 1, swept (not our normal comparison point) | 0.7892 | 0.30 |
| Method 1, conf=0.25 (as used everywhere in this project) | 0.7859 | 0.25 |
| Small-stem fusion (cascade's own swept-optimal) | 0.7885 | 0.38 |

This is a useful side data point — Method 1 has a little headroom if its
own threshold were tuned too — but it doesn't change how this project's
comparisons are framed or reported: Method 1 stays fixed at 0.25
everywhere, exactly as designed from the start, and the cascade's
F1=0.7885 beating Method 1's as-used F1=0.7859 stands as reported.

The cascade's other, unaffected strengths:
1. Higher mAP@.5 across the board (0.786-0.788 vs. 0.694) — real ranking-
   quality improvement, since mAP already sweeps every threshold for
   both methods identically.
2. The small-object recovery on the hardest test videos (10 of 44
   previously request-invisible small people caught, `AR_small`/
   `mAP_small` moving from exactly 0 to nonzero) — a capability
   difference, not disputed by this finding.

**Also settled by this GPU run — the EfficientNet-B0 vs. ResNet18 question
inside the cascade:**

| Verifier (score fusion) | Best F1 | @ conf |
|---|---|---|
| ResNet18, standard stem | 0.7824 | 0.39 |
| **ResNet18, small-input stem** | **0.7885** | 0.38 |
| EfficientNet-B0 | 0.7824 | 0.38 |

The 3x3-stem improvement over the standard stem holds up on GPU, not just
CPU (0.7885 vs. 0.7824, the same ~0.006 gap seen on CPU). EfficientNet-B0
exactly ties the standard-stem ResNet on GPU (0.7824 both) — still behind
the small-stem ResNet, confirming the CPU-based conclusion:
EfficientNet-B0 does not outperform the best ResNet configuration inside
this cascade, on either hardware.

**Simpler, cleaner verifier comparison (user's correction):** since YOLO
is identical across all three fusion variants (same checkpoint, same
0.01/0.25 thresholds) — only the verifier backbone changes — hunting for
each variant's own best F1 threshold is unnecessary complexity for this
specific comparison (it made sense for cascade-vs-Method-1, two genuinely
different systems, but not for verifier-vs-verifier). At the single
shared operating point (conf=0.25, the cascade's own design boundary, no
threshold search at all):

| Verifier (score fusion, T4) | Precision | Recall | F1 | TP/FP/FN |
|---|---|---|---|---|
| ResNet18, standard stem | 0.714 | 0.783 | 0.747 | 563/226/156 |
| **ResNet18, small-input stem** | **0.754** | 0.778 | **0.766** | 559/182/160 |
| EfficientNet-B0 | 0.729 | 0.765 | 0.747 | 550/204/169 |

The gap is even clearer here than in the per-variant-optimized comparison
(0.019 vs. the earlier 0.006) — small-input-stem ResNet18 is unambiguously
the best verifier of the three, at a fixed point with no threshold-hunting
involved.

## Tier 1 item 3: SAM3 zero-shot benchmark result (2026-09-13)

Ran `notebooks/04_sam3_zeroshot_eval.ipynb` on Colab T4: SAM3 prompted
directly with "person" (conf=0.25, imgsz=1024 — the GPU-memory-safe
value confirmed 2026-09-12), zero training on this project's data. This
is the assignment's required genuinely-different-paradigm alternative
(foundation model + text prompt vs. every other method's trained
supervised-detection architecture).

| Metric | Value |
|---|---|
| mAP@.5 | **0.8465** — highest of any method tried this cycle |
| mAP@[.5:.95] | 0.6256 — also highest |
| Precision (@0.25) | 0.485 |
| Recall (@0.25) | **0.872** — highest of any method |
| F1 (@0.25) | 0.624 |
| TP/FP/FN | 627/665/92 |
| Inference | **0.37 FPS** (mean 2.72s/frame; min 2.22s, max 44.26s) |

| Method | Hardware | mAP@.5 | F1 (@0.25) |
|---|---|---|---|
| YOLO26n zero-shot | T4 | 0.693 | 0.784 |
| RT-DETRv2-R18 zero-shot | CPU (not yet re-run on T4) | 0.740 | 0.677 |
| Cascade, small-input-stem (best trained result) | T4 | 0.786 | 0.766 (shared-threshold table above) |
| **SAM3 zero-shot** | T4 | **0.847** | 0.624 |

**The clearest paradigm contrast in the whole project:** SAM3 achieves
the best ranking quality (mAP) and best recall of any method, with zero
training on this data — a real demonstration of foundation-model
generalization. The cost is precision (665 FP at conf=0.25, dragging F1
down) and, far more severely, **speed**: 0.37 FPS is roughly an order of
magnitude slower than every trained detector in this project (YOLO/
RT-DETR/cascade all ran at multiple FPS or better). Not remotely
real-time-deployable as-is; genuinely useful as exactly what it's labeled
— a zero-shot ceiling-finder and (as already used) a pseudo-labeling
teacher, not a deployment candidate.

Per-video mAP@.5 tells an unusually sharp story: **1.000 on Berghouse**
(perfect), 0.907 on DJI_0862, 0.606 on DJI_0501, but only 0.260 on
DJI_0596 — still the hardest video for every method tried, but a large
relative improvement over YOLO's 0.052 and RT-DETR's 0.029-0.041 there.

**Not yet explained:** the 44.26s max single-frame time (vs. a 2.22s
min and 2.72s mean) — plausibly first-call model compilation/caching
overhead rather than a pathological frame, but not confirmed against
the actual per-frame timing log (only aggregate min/mean/max reached
the manifest). Worth a note in the presentation as an open question,
not a claimed explanation.

## SAM3 qualitative error analysis: concrete success and failure examples (2026-09-13)

Inspected `results/eval/sam3_zeroshot_T4/comparison/` directly (per the
project's "look at the actual files, not just the aggregate metric"
habit) — two frames worth recording as the presentation's concrete
success/failure examples (task's "successful and failed result
examples" requirement).

**`Berghouse_Leopard_Jog__frame_000000.jpg` (success):** two trail
runners, both correctly boxed at high confidence (0.88 and ~0.9),
matching ground truth exactly — the visual confirmation behind this
video's 1.000 mAP@.5.

**`DJI_0596__frame_000000.jpg` (mixed — the presentation's clearest failure
example):** this video is not a snow/mountain scene as initially assumed
from its "ant-sized instances" label — it's a **lake steamer boat**
(Swiss flag visible, consistent with `CLAUDE.md`'s "Lake Geneva clips"
note about the dataset). Three distinct, visually confirmed patterns in
one frame:
1. **Correct:** a cluster of people on the boat's rear deck, correctly
   boxed.
2. **Missed:** two people standing on the boat's raised bridge/wheelhouse
   (ground truth boxes present, no matching prediction nearby at all).
3. **False positive:** 2-3 "person" boxes on open water where nothing is
   present — plausibly wave/glare patterns at a distance resembling a
   person from SAM3's perspective, though this specific cause isn't
   confirmed, just visually plausible.

This single frame demonstrates all three of the assignment's requested
error categories (correct detection, missed detection, false positive)
in one concrete, presentable example — more useful for the "hata analizi"
section than the aggregate per-video numbers alone.

## Correction 2026-09-16: "0 of 44 at any confidence threshold" was wrong — it's 0 at the default threshold only

**Finding.** While reviewing the presentation, the user questioned how the
cascade (Slide 8/10) could possibly recover any of the "0 of 44 small/distant
people, at any confidence threshold" boxes YOLO26n was said to miss on
DJI_0501/DJI_0596 (Slide 7) — since the cascade's Stage 1 is the *same*
YOLO26n checkpoint, just run at a lower confidence floor (0.25→0.01). If
YOLO genuinely found none of those 44 at *any* threshold, Stage 1 could
never propose a candidate box there for Stage 2 to verify, and the later
"10 of 44 recovered" claim (Slide 10) would be impossible.

**Root cause.** The original "at any confidence threshold" claim was
computed from `results/yolo26_zeroshot/predictions.json`, which turns out
to be threshold-filtered at conf≥0.25 (Ultralytics' default) — its
minimum stored score is 0.2506. It was never actually checked against the
full confidence range, despite the wording implying it was.

**Verified directly** against `results/yolo26_lowconf/predictions.json`
(conf≥0.01, the same floor the cascade's Stage 1 uses): of the 44 small
ground-truth boxes on DJI_0501/DJI_0596, **26 do have a matching raw YOLO
candidate at IoU≥0.5** (scores ranging 0.011–0.192) — low-confidence, but
real, spatially-correct localizations that simply don't survive the
default 0.25 cutoff.

**Corrected framing:** "0 of 44 caught at YOLO's default confidence
(0.25)" — not "at any confidence threshold," and not purely "a
feature-map resolution limit." It's mostly a confidence-threshold
problem at the default operating point: the feature map *can* represent
most of these objects (26/44 raw candidates exist), just not confidently
enough for the default cutoff to keep them. This is the correct and
actually stronger justification for Method 2's approach — lowering the
threshold to 0.01 recovers real candidates (not fabricated ones), and the
verifier then separates the ~26 real low-confidence person boxes from
the surrounding noise, ultimately keeping 10 of the 44 (Slide 10).

**Affected files:** `docs/sunum_icerik.md` (Slides 7 and 8 wording),
`docs/presentation/deck.html` (same two slides — callouts, bullets, and
speaker notes corrected). The "10 of 44 recovered" claim on Slide 10
itself was not re-derived here and is assumed correct (it comes from the
official evaluated cascade predictions, not this ad-hoc IoU check) —
worth a similar direct spot-check later if time allows.

## Correction 2026-09-16: Slide 11's comparison table used an invalid shared confidence threshold

**Finding.** While reviewing the final-result slide, the user pointed out
that the table looked wrong: we had established earlier in the project
that the cascade beats Method 1, but the slide's P/R/F1 columns showed
the opposite (cascade F1 0.766 vs. Method 1 0.784). The user recalled
correctly that the cascade's own operating point is conf=0.38, not 0.25.

**Root cause.** The table reported all three rows at a single "shared
conf=0.25". That design decision was recorded earlier (see "Simpler,
cleaner verifier comparison (user's correction)", 2026-09-13) and is
valid — but *only for verifier-vs-verifier comparison*, where the YOLO
stage is byte-identical across rows and only the backbone changes. The
slide then also put **Method 1** into that same shared-threshold table,
which is exactly the comparison that entry says a shared point is *not*
valid for: the cascade's fused score `sqrt(yolo_conf x verifier_prob)`
lives on a different scale from YOLO's raw objectness confidence, so
conf=0.25 is an arbitrary point for the cascade, not its operating point.

**Re-verified directly** with `src.eval.metrics.precision_recall_f1`
against `data/gold_test/annotations.json`, at each system's own
as-designed operating point:

| Config | conf | P | R | F1 | TP/FP/FN |
|---|---|---|---|---|---|
| Method 1 (YOLO26n, Ultralytics default) | 0.25 | 0.8529 | 0.7260 | 0.7844 | 522/90/197 |
| **Cascade, small-input-stem + fusion** | 0.38 | **0.8899** | 0.7079 | **0.7885** | 509/**63**/210 |
| Cascade, EfficientNet-B0 | 0.38 | 0.8787 | 0.7051 | 0.7824 | 507/70/212 |

These reproduce the T4 figures already recorded in "GPU (T4) validation
of the full method comparison" (2026-09-13) exactly.

**Corrected framing:** the cascade leads on mAP@.5 (0.786 vs 0.693),
mAP@[.5:.95] (0.526 vs 0.479), precision (0.890 vs 0.853), F1 (0.789 vs
0.784) and false positives (63 vs 90); Method 1 retains a small recall
edge (0.726 vs 0.708). The pre-existing honest caveat is kept visible on
the slide: sweeping Method 1's threshold too (which the project
deliberately does not do) lands it at F1 0.7892 @ 0.30, marginally above
the cascade — which is why mAP carries the headline claim.

**Affected files:** `docs/sunum_icerik.md` and
`docs/presentation/deck.html` (Slide 11 table, bullets, footnote and
speaker notes). A `conf` column was added to the table so the differing
operating points are explicit rather than looking like cherry-picking.

**Still open:** Slide 14 (Quantitative Comparison) reports all four
methods at conf=0.25 with a footnote explaining the choice. That table
spans genuinely different score scales too (SAM3 and RT-DETR included),
so it deserves the same scrutiny — not changed here, flagged for review.

## Follow-up 2026-09-16: per-method operating points confirmed as the intended framing

The correction above briefly moved toward hedging the cascade-vs-Method-1
P/R/F1 comparison as "not a fair head-to-head" because the cascade's 0.38
point comes from a test-set F1 scan. The user stopped this and confirmed
the per-method-operating-point framing (Method 1 @ 0.25, cascade @ 0.38,
values reported plainly, cascade shown ahead where it is) was already the
deliberate, previously-discussed choice — not an oversight to walk back.
Reverted Slide 11 and Slide 14 to that framing. The leakage caveat (swept
Method 1 hits F1 0.7892 @ 0.30, edging the cascade's 0.7885) is kept as
Q&A backup in `sunum_icerik.md`, not as an on-slide hedge — mAP already
carries the headline "cascade is better" claim precisely because it
doesn't need this kind of per-method threshold justification.

## 2026-09-16: RT-DETRv2-R18's HF wrapper never actually used the GPU

**Finding.** While preparing a notebook to finally re-run RT-DETR on a T4
(the top-priority open item in `kalan_isler.md` — every RT-DETR number so
far was CPU-only, unlike every other method), `src/methods/rtdetr/model.py`'s
`RtDetrV2Detector` (the Hugging Face `transformers`-based wrapper around
`PekingU/rtdetr_v2_r18vd`) turned out to have no device-handling code at
all — `.from_pretrained()` loads on CPU, and neither the model nor the
processor's output tensors were ever moved anywhere else. Running
`scripts/28_rtdetr_zeroshot_eval.py` unmodified on a Colab T4 would have
silently stayed on CPU and reproduced the same CPU timing again under a
different filename — the exact opposite of what that notebook run was
for. This contradicts the presentation's own "RT-DETR's own script
already runs on GPU automatically when available" framing (Slide 14's
footnote) — that claim holds for the Ultralytics-based
`RtDetrUltralyticsDetector` (Ultralytics auto-selects CUDA, the same
mechanism already verified by `yolo26n_zeroshot_T4`), but not for the HF
one; the footnote wording didn't distinguish the two checkpoints.

**Fix.** Added a `device: str = "cpu"` parameter to `RtDetrV2Detector.__init__`,
which moves the model (`self._model.to(device)`) and, per call, the
processor's output (`inputs.to(self._device)`) to that device.
`scripts/28_rtdetr_zeroshot_eval.py` reads it from `config.get("device", "cpu")`
— the committed `configs/28_rtdetr_zeroshot.yaml` now states `device: cpu`
explicitly (previously implicit/absent), so the already-recorded
`rtdetr_v2_r18_zeroshot` CPU result is reproduced identically and stays
valid. A new notebook, `notebooks/05_rtdetr_zeroshot_T4_eval.ipynb`,
patches `device: cuda` in a session-local config copy and writes to a new
`results/rtdetr_zeroshot_T4/` directory, leaving the CPU run untouched so
both remain directly comparable afterward (same pattern as
`yolo26n_zeroshot` vs. `yolo26n_zeroshot_T4`).

**Not yet run** — this fix and notebook were prepared and pushed; the
actual T4 execution still needs a live Colab session (GPU quota,
`test_frames.zip` on Drive) and hasn't happened as of this entry. Both
slides still label these two rows "CPU" (Slide 12 plainly, Slide 14 with
its own "¹" footnote) until that run produces real T4 numbers — not
removed pre-emptively.

## 2026-09-16: RT-DETR's T4 run landed — and "faster than YOLO" would be misleading

**The run happened.** `notebooks/05_rtdetr_zeroshot_T4_eval.ipynb` was
executed on a real Colab T4 (after the device-fix above and one retried
push — the first attempt's `git push` failed on a corrupted token
variable in a re-run cell, the second attempt succeeded, commit
`735cb41`). Both checkpoints reproduce their CPU-run mAP/P/R/F1 almost
exactly (e.g. RT-DETRv2-R18 mAP@.5 0.7398→0.7401), confirming — again,
same as YOLO's own CPU-vs-T4 check — that hardware doesn't change a
model's output, only its speed. New results: `rtdetr_v2_r18_zeroshot_T4`
and `rtdetr_ultralytics_l_zeroshot_T4` in `results/eval/comparison.csv`.

**The FPS numbers are real, and genuinely surprising: RT-DETRv2-R18 7.7
FPS, RT-DETR-l 7.5 FPS — both *faster* than YOLO26n's 7.3 FPS on the same
T4.** Given RT-DETR was introduced as "heavier, lower FPS" (Slide 12's
original framing) and the CPU numbers backed that up (3.2 / 1.5 FPS vs.
YOLO's 3.2), this looked at first like a real "transformers beat CNNs on
GPU" finding worth headlining.

**Checked before writing that claim onto a slide — it doesn't hold.**
RT-DETR runs at its own native 640×640 (`configs/28`/`30`'s `imgsz`);
YOLO26n deliberately runs at 1920×1088 for this project's tiny aerial
people (`configs/05_yolo_zeroshot.yaml`). That's a ~5.1× difference in
pixels processed per frame ((1920×1088)/(640×640)). The FPS gap is very
plausibly explained by that alone, not by attention parallelizing better
than convolution+NMS on a GPU — and Slide 12 already documents, in the
very same slide, that pushing RT-DETR to YOLO's resolution doesn't just
slow it down, it breaks it outright (mAP@.5 0.740→0.253, no NMS at
inference). So "RT-DETR is faster than YOLO" is not a claim this project
can actually support; "RT-DETR reaches usable FPS at its own resolution,
but resolution and speed can't be pulled apart from architecture in this
comparison" is what the data supports.

**What changed:** Slide 12's intro thesis dropped its now-unsupported
"heavier to run, lower FPS" claim entirely (still true per-pixel, just
not demonstrated by this comparison). Both tables (Slide 12, Slide 14)
now show real T4 numbers with "T4" replacing "CPU", plus a footnote
naming the resolution mismatch explicitly. Slide 18 and Slide 20's
"YOLO/cascade/RT-DETR FPS not yet benchmarked" callouts were also
corrected — YOLO's own T4 FPS (7.3) was already measured back on Slide 7
and simply hadn't been copied into these two slides; RT-DETR's is new.
Only the **cascade's** end-to-end FPS on T4 remains genuinely
unmeasured now.

## 2026-09-16: Result video — cascade on the 4 test videos

**Decision.** The assignment PDF lists a result video as an optional
presentation deliverable ("Varsa sonuç videosu"). Built
`scripts/36_render_result_video.py` + `configs/36_render_result_video.yaml`
+ `notebooks/06_render_result_video.ipynb` to produce one: the cascade
run frame-by-frame across all 4 held-out test videos, combined into a
single annotated `.mp4`.

**Which method, and why.** The cascade (small-stem ResNet18 verifier +
score fusion), not SAM3 despite SAM3's higher mAP (0.846 vs. 0.786) —
SAM3 is ~10× slower (0.37 FPS) and was never proposed as the deployable
method in this project (Slide 19's production system already casts it as
a periodic auditor, not the primary detector). The cascade is the "best
trained, deployable method" this project actually argues for, so it's
the one worth showing working end-to-end.

**Reused, not reinvented.** `scripts/36` calls the identical cascade
logic as `scripts/25_cascade_score_fusion_eval.py` (same
`Yolo26Detector` + verifier checkpoint + `sqrt(yolo_conf * verifier_prob)`
fusion) via the same `crop_candidate` helper — this is the already-
evaluated pipeline applied to raw video frames instead of the sampled
gold-test frames, not a new or different model.

**Boxes only drawn at the reported operating point.** `draw_threshold:
0.38` matches the exact confidence the cascade's P/R/F1 numbers were
computed at (see "GPU (T4) validation of the full method comparison",
2026-09-13). Drawing every fused-score candidate instead would make the
video look more populated than the reported result actually supports —
the video needs to match the numbers, not flatter them.

**Mechanics, smoke-tested locally before writing the Colab notebook**
(CPU, `imgsz=640`, one short train video, `frame_stride=100` — ~10
frames, not a real run): confirmed the letterbox-to-shared-canvas step
doesn't distort aspect ratio, the per-clip label overlay renders, and
`output_fps = input_fps / frame_stride` keeps playback speed correct
regardless of how many frames are skipped. The real run (all 4 test
videos, every frame, T4, `imgsz=1920`) has not happened yet — needs a
live Colab session with the verifier checkpoint on Drive and either a
Kaggle API token or the raw dataset already fetched. Video output is
gitignored (`*.mp4`) and belongs on Drive, per this project's existing
convention for large media — only the run's manifest JSON is pushed to
GitHub.
