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
