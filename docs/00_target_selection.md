# Target Class Selection

_Status: DECIDED — 2026-09-11, after visual triage._

## Selection criteria

- Appears in at least 2-3 different videos
- Has scale variation (altitude changes)
- ~500+ instances available
- Includes occlusion / hard negatives worth analyzing

## Triage method

At least 1 frame was extracted from each of the 13 videos, plus 4-5
additional frames (evenly spaced across the video) from six of them, and
inspected visually. The decision was based on the recurring appearance
across the whole video, not a single lucky/unlucky frame.

## Candidate classes

| Candidate | # videos seen in | Scale variation | Estimated instance count | Note |
|---|---|---|---|---|
| **person** | 6 (Berghouse Leopard Jog, Surenen Pass Trail Running, VerticalFlyOver, Stockflue Flyaround, DJI_0790, DJI_0862) | Yes — drops from a clear figure to a few-pixel dot as altitude changes | Easily 500+ (6 videos × ~25-40s usable duration each × 1-2 people/frame) | Occlusion: footbridge/vegetation crossings (Berghouse), distant figures blending into shadow/rock (DJI_0862), small person blending with dogs in snow (DJI_0790) |
| boat/sailboat | 2 (DJI_0596 single ship, moored sailboats at Isles of Glencoe) | Weak — mostly static, fixed framing distance | Low (mostly stationary, poor fit for the motion-based method) | Barely meets the criteria, not preferred |
| vehicle (pickup truck) | 1 (a single frame in DJI_0790) | — | Very low | Single video, fleeting appearance — eliminated |
| dog (sled team) | 1 (DJI_0790) | Yes but single video | High per-video (6-8 dogs) but only one video | Fails the "2-3 different videos" criterion — eliminated |
| static objects (statue, glacial lagoon) | 1 video each | None (fixed object) | 1 per video | No scale variation, no repeated instances — eliminated |

## Decision

**Selected class: `person`**

Rationale: appears consistently in 6/13 videos (well above the threshold),
has strong scale variation from altitude/distance changes, easily yields
500+ instances, and offers rich occlusion/hard-negative material
(vegetation and footbridge occlusion, distant figures blending into
rock/shadow, small human silhouettes blending with sled dogs in snow).
`person` is also already a COCO class, which keeps the YOLO26s zero-shot
sanity check's domain-gap measurement meaningful — the model isn't
being tested on an unfamiliar class, it's being tested on whether the
unusual angle, small scale, and low resolution defeat a class it already
knows.

Other candidates (boat, vehicle, dog, static objects) were eliminated for
failing the video-count or instance-density criteria.

## Correction 2026-09-12: full manual review found `person` in 11/13 videos

The initial triage above sampled only 1 + 4-5 extra frames per video and
concluded `person` appears in 6/13 videos. The user then manually watched
all 13 videos in full and found `person` actually appears in **11 of 13**
— the initial triage missed several appearances because they involve very
small/distant figures that don't reliably land in a sparse frame sample.
This doesn't change the target-class decision (if anything it strengthens
it), but it materially changes which videos are usable as person-free
background and reframes several videos as deliberate hard-case material:

| Video | What's there | Difficulty / role |
|---|---|---|
| Berghouse Leopard Jog | 2 runners | Easy, good visibility |
| Bluemlisalphutte Flyover | A few people, ant-sized (drone very high) | Very hard — likely undetectable, a genuine "too small" failure case |
| DJI_0501 | A human statue (false-positive trap) + real tiny people nearby | Ambiguous/qualitative case — short clip (8.2s) |
| DJI_0574 | Cyclists (person partly occluded by the bicycle) | Occlusion case — bicycle hides person-defining features |
| DJI_0596 | People on a ship's deck, very small | Hard — small-object case, candidate for a SAHI discussion |
| DJI_0790 | A musher + a crowd at the end | Easy-medium, good volume |
| DJI_0862 | People near a helicopter wreck, good size | Easy-medium, good size despite dark/low-contrast terrain |
| DJI_0876 | One person walking by a house, brief | Short appearance, low volume |
| Stockflue Flyaround | People on a hilltop, intermittently occluded by bushes | Occlusion case |
| Surenen Pass Trail Running | 2 women power-walking | Easy, good visibility |
| VerticalFlyOver | 2 people hiking a ridge | Easy, good visibility |

**Only 2 videos are genuinely person-free: Creux du Van Flight and Isles
of Glencoe.** The `data/splits/background.txt` hard-negative list (which
had 7 entries) is corrected to just these 2 — see the 2026-09-12 decision
log entry for why the other 5 were removed from it.

## Full object census across all 13 videos

The user also catalogued every other object visible in each video (see
`docs/video_notes.csv`, `other_objects` column, and the generated
`results/dataset_overview/table.csv`), which sharpens the case for
`person` beyond the original candidate table: across the 13 videos,
`person` appears in 11, far ahead of every other recurring object —
house/building (7 videos: Creux du Van, DJI_0574, DJI_0596, DJI_0790,
DJI_0876, Isles of Glencoe, Stockflue — but static/architectural, so it
offers altitude-driven scale variation only, none of the pose/occlusion
diversity a moving subject gives), boat/ship (2: DJI_0596, Isles of
Glencoe), and single-video appearances of a car, bicycles, sled dogs, a
statue, a flag, birds, another in-frame drone, and crashed-plane wreckage.
No other object comes close to `person`'s combination of frequency,
scale range, and occlusion/failure-case richness.

The user's framing for the hard cases (ant-sized people, occlusion,
statue false-positive) is explicitly to keep them as honest failure/
ambiguous-case material rather than aim for a model that scores well
everywhere — this directly matches the assignment's "honest error
analysis, including failures and ambiguous cases" grading criterion
(`CLAUDE.md` Section 1).

## Side observation: the dataset is not from a single country

`CLAUDE.md` had described the dataset as "Switzerland," but visual triage
showed the footage is from mixed locations: Scotland (Isles of Glencoe —
loch/village), likely Iceland (DJI_0862 volcanic terrain, DJI_0876 glacial
lagoon/icebergs), likely South Africa or another region (Berghouse Leopard
Jog — grassland/shrub trail), alongside genuine Swiss footage
(DJI_0501/0574/0596/0790, Bluemlisalphutte, Creux du Van, Stockflue — Alps
scenery, Lake Geneva). This was corrected in `CLAUDE.md` Section 1. It has
no practical effect on the outcome (doesn't change the target-class
decision), but the geographic diversity is actually an advantage for the
`person` class in terms of appearance diversity (different clothing,
terrain, lighting conditions).
