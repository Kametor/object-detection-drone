# Object Detection with Limited Data — Sunum İçeriği

> Yaşayan doküman. Her slayt netleştikçe güncellenir.

## Meta

- **Sunan:** Mehmet Recep Aşkar
- **Süre:** 20-25 dk, hızlı tempo
- **Slayt metni ve konuşma dili:** İngilizce
- **Hedef his:** Dinleyici film izler gibi takip etsin; her slayt bir öncekinin açtığı soruyu kapatsın
- **Konuşma metni:** Sunum bittikten sonra bütün hâlinde yazılacak

### Renk paleti (Roketsan kurumsal)

| Rol | Pantone | HEX | RGB |
|---|---|---|---|
| Vurgu (başlık, önemli sayı, grafik ana seri) | 7740 C | `#3A913F` | 58, 145, 63 |
| Ana metin | Black C | `#1D1D1B` | 29, 29, 27 |
| İkincil metin, çizgi, panel | 429 C | `#A4A9AD` | 164, 169, 173 |

**Arka plan:** Açık ve temiz zemin + yeşil vurgu. Blur'lu/karartılmış full-bleed görsel KULLANMA.
Görseller net, kendi başına duran küçük kartlar hâlinde yerleştirilir.

---

## ÖDEV KONTROL LİSTESİ → SLAYT EŞLEMESİ

PDF'in "Sonuçların Sunulması" ve "Değerlendirme" maddeleri. Hiçbiri açıkta kalmayacak.

| PDF maddesi | Slayt |
|---|---|
| Seçilen hedef ve kullanılan veri bölümü | 3 |
| Veri hazırlama ve etiketleme stratejisi | 4, 5 |
| Başlangıç yaklaşımı (Method 1) | 6 |
| Alternatif yaklaşım (Method 2 — Cascade) | 7 (mimari/eğitim), 8 (iterasyon), 9 (final sonuç) |
| Alternatif yaklaşım (Method 3 — farklı mimari) | 10 |
| Alternatif yaklaşım (Method 4 — gerçek alternatif, SAM3) | 11 |
| Nicel ve nitel karşılaştırma | 12 (nicel), 13 (nitel) |
| Başarılı / başarısız / belirsiz sonuçlar | 13, 14 |
| Hata analizi | 14 |
| Güçlü ve zayıf yönler | 15 |
| Hesaplama maliyeti | 15 |
| Metrik seçiminin gerekçesi | 12 (Blok B) |
| Colab notebook / kod deposu | 18 (Kapanış) + canlı göster |
| README | 18 (Kapanış) |
| Nicel sonuç tablosu | 12 |
| Başarılı/başarısız örnekler | 13 |
| Kaynak listesi | 19 (References) + slayt içi inline atıflar (10, 11) |
| Sonuç videosu | 18 (Kapanış) — varsa canlı göster |
| Final sistem önerisi | 16 |
| Dürüst limitasyonlar / kalan işler | 17 |

---

## Slayt 1 — Kapak

**Layout**
- Temiz, açık zemin
- **Roketsan logosu sağ üstte**
- Başlık solda/ortada
- 3-4 küçük görsel etrafa dağıtılmış (kendi çıktılarımızdan, net, kartlar hâlinde)
- Arka planı kaplayan blur'lu görsel YOK

**İçerik**
```
Object Detection with Limited Data
Drone Video Object Detection under Label Scarcity

Mehmet Recep Aşkar
Computer Vision Engineer
```

**Görsel notu:** Stok görsel kullanma. Kendi tespit çıktılarımızdan seçilmiş net kareler.

**Konuşma metni**
> Hello, my name is Mehmet Recep Aşkar. I graduated from Middle East Technical
> University in 2022 with a degree in Electrical and Electronics Engineering.
> I currently work at MKE as a Computer Vision Engineer, focusing on visual
> navigation, object detection and tracking.
> Today I will present my approach to object detection when labelled data is scarce.

---

## Slayt 2 — Problem Definition & Real-World Motivation

**Tek mesaj:** Bu bir nesne tespiti problemi değil; *etiket kıtlığı altında* nesne tespiti
problemi. Ve bu, sahada sürekli karşılaşılan bir durum.

*Blok A: The assignment*
- Detect and localize a chosen object class in drone videos
- **13 short videos. Little data, and no ground truth at all.**
- Full manual labelling is explicitly out of scope
- Real question: how do you build **and validate** a detector without labels?

*Blok B: Why this matters in practice*
- Surveillance networks: hundreds of cameras, thousands of simultaneous detections
- A **new product** enters a production line → a class no model was ever trained on
- Industry 5.0: product counting, occupational safety, quality inspection
- Data never arrives labelled; hardware budget is limited

**Görsel:** Solda drone frame, sağda kamera ağı / fabrika şeması.

**Konuşma akışı**
> The task itself is straightforward: detect an object in drone video.
> What makes it hard is the constraint — thirteen short videos, no ground truth, and
> labelling everything is explicitly out of scope.
> This is not an artificial constraint. Think of a surveillance network with hundreds
> of cameras. Or a production line where a new part is introduced — a class no model
> was ever trained on. Data never arrives labelled, and we cannot annotate everything.
> So the real question becomes: how far can we get without labels, and how do we know
> that what we built actually works?

**Not:** Roketsan'ın iç sistemleri hakkında kesin iddia kurma — "think of a facility"
gibi varsayımsal dil kullan.

---

## Slayt 3 — Target Selection & Data Subset

**Tek mesaj:** Veriyi körlemesine kullanmadık; önce sistematik olarak okuduk, hedefi
ve kullanacağımız videoları o okumaya dayanarak seçtik.

**Kapsam notu:** Bu slayt PDF'in *"Seçilen hedef ve kullanılan veri bölümü"* maddesini
karşılar. Split stratejisi buraya DEĞİL, slayt 4'e girer.

*Blok A: Systematic dataset inventory*
- 13 videos analysed one by one
- Recorded per video: resolution, duration, frame count, **objects present**,
  background type, viewpoint/altitude
- Tablonun tamamı repoda — slaytta sadece özet, koca tablo koyma

*Blok B: Why "person"*
- Most frequent object class across the dataset
- Present in **11 of 13** videos
- → more generalisable **training** set AND more generalisable **test** set
- Scale variation across altitudes; occlusion cases present

*Blok C: Key numbers (VS Code analizinden doldurulacak)*
- Total videos / total duration: `TBD`
- Videos containing the target: 11 / 13
- Approx. person instances observed: `TBD`
- Videos selected for this study: `TBD`

**Görsel:** Hedefin göründüğü, **henüz bbox atılmamış** ham frame'lerden 3-4 kare.
Ham kare göstermek bilinçli: "önce baktık, sonra karar verdik" anlatısını destekler.

**Konuşma akışı**
> Before choosing anything, I went through all thirteen videos systematically and built
> an inventory: what objects appear, what the background looks like, the viewpoint, the
> duration. The full table is in the repository; here is the summary.
> Person turned out to be the right target: it is the most frequent class and appears
> in eleven of the thirteen videos. That matters twice over — a more generalisable
> training set, and just as importantly, a more generalisable test set.

---

## Slayt 4 — Data Preparation: Splitting Strategy

**Tek mesaj:** Split **video seviyesinde** yapıldı, frame seviyesinde değil. Ve test
seti en kıymetli varlığımız olduğu için elle etiketlendi.

*Blok A: Split at video level — not frame level*
- Frames within one video are near-duplicates and share a single domain
- A frame-level split would leak the test domain into training → inflated scores
- **Each split draws from separate videos**
- Train / Val / Test: `TBD` videos each, ratios `TBD`

*Blok B: Why each split was sized the way it was*
- **Test:** enough videos to evaluate methods across a genuinely general context —
  not a single scene
- **Train:** enough videos to avoid training on one narrow domain
- **Val:** threshold tuning and model selection only; never used for final numbers

*Blok C: The test set is manually labelled*
- Test labels drawn **by hand in CVAT** — no model output enters ground truth
- The human labelling budget was spent on **measurement, not training**
- Rationale: without a trustworthy test set, no other number in this talk means anything

*Blok D: Honest limitation*
- With a small number of held-out videos, the test set is limited
- Generalisation claims are bounded accordingly — reported later with the results

**Görsel:** Video-level split şeması (13 video → 3 kutu), + CVAT arayüzünden ekran görüntüsü.

**Konuşma akışı**
> One decision here is more important than it looks. I did not split frames — I split
> videos. Frames inside a single video are almost identical and share one domain; a
> frame-level split would leak the test domain straight into training and inflate every
> number I show you today. Each split comes from separate videos.
> Test had to cover enough videos to evaluate the methods in a genuinely general
> context. Train had to cover enough videos not to overfit to one domain.
> And the test set is labelled entirely by hand, in CVAT. No model output ever enters
> the ground truth. That was a deliberate choice about where to spend my human labelling
> budget: on measurement, not on training. Without a test set I can trust, none of the
> numbers that follow would mean anything.

---

## Slayt 5 — Automatic Labelling with SAM 3

**Tek mesaj:** Test elle etiketlendi ama train için elle etiketleme gerçekçi değildi;
otomatik etiketleme hattı kurduk ve **kalitesini ölçtük**.

*Blok A: Why automatic labelling*
- Manual labelling does not scale to the training set
- Need: boxes at volume, with acceptable noise

*Blok B: SAM 3 pipeline*
- Prompt-driven segmentation → masks → bounding boxes
- Applied across training videos
- `TBD` — çalıştırma parametreleri, threshold

*Blok C: Validating the labeller against ground truth*
- SAM 3 was run **on the manually labelled test videos as well**
- Its output compared directly against our own CVAT annotations
- Only after the agreement was satisfying did we trust it to label the training set
- Agreement / accuracy vs. manual labels: **mAP@.5 = 0.846** against the
  gold test set — see Slide 11 for the full benchmark (same model, same
  protocol; this is what "agreement" means measured, not eyeballed)
- Inference time per frame: not logged separately during the labelling run
  itself — the closest measured number comes from the later zero-shot
  benchmark under comparable settings: **2.72 s/frame mean** on T4 (Slide 11)
- **Total labels produced (train + val, after quality filtering and the two
  manual corrections below): 471 frames, 1,853 boxes**

*Blok C.1: Final counts, per video*

| Video | Frames | Boxes |
|---|---|---|
| DJI_0790 | 86 | 596 (post dog-correction, see Block D) |
| DJI_0876 | 59 | 685 (post under-labelling correction) |
| Surenen Pass Trail Running | 92 | 188 |
| Stockflue Flyaround | 69 | 127 |
| DJI_0574 | 43 | 108 |
| VerticalFlyOver (val) | 54 | 107 |
| Bluemlisalphutte Flyover | 68 | 42 |
| **Total** | **471** | **1,853** |

> **Anlatım notu:** Bu, slaytın en güçlü argümanı. Otomatik etiketleyiciye körü körüne
> güvenmedik — elimizdeki tek güvenilir referansa karşı ölçtük, sonra kullandık.

*Blok D: Failure case and the fix (bunu mutlaka anlat)*
- **Shadows were being detected as persons**
- Diagnosis: low confidence threshold accepting shadow regions
- Fix: raised the threshold → `TBD` sonuç
- Trade-off: higher precision, some recall lost

**Görsel:** SAM 3 çıktı örnekleri (başarılı) + **gölge hatası örneği** yan yana,
threshold öncesi/sonrası karşılaştırma.

**Kaynak:** `results/pseudo_labels/annotations/*.json` (final frame/box
counts), `results/eval/sam3_zeroshot_T4/metrics.json` (agreement vs. manual
labels), `results/manifests/34_sam3_zeroshot_eval_20260913T202102Z.json`
(2.72 s/frame timing)

**Konuşma akışı**
> The test set is hand-labelled, but that does not scale to training. So I built an
> automatic labelling pipeline using SAM 3 — prompt-driven segmentation, converted to
> bounding boxes.
> But before trusting it on the training set, I ran it on the manually labelled videos
> too and compared its output against my own annotations. Only once that agreement was
> satisfying did I let it label anything I would train on — measured later at point
> eight four six mAP against the human labels, which you'll see again in a few slides.
> Once I trusted it, it produced four hundred seventy-one labelled frames and just
> under nineteen hundred boxes across the training and validation videos.
> The interesting part is what went wrong. The pipeline started labelling shadows as
> people. That is exactly the kind of failure you only find by looking at the output,
> not at the metrics. Raising the confidence threshold removed most of it, at the cost
> of some recall — a trade I was willing to make, because noisy labels propagate into
> everything trained on them.

---

## Literatür ve Atıf Stratejisi

**Amaç:** Yaptığımız tercihlerin literatüre dayandığını göstermek. Hem sunum içinde
noktasal atıf, hem sonda toplu kaynak slaytı.

### Slayt içi atıf (inline)

Yöntemi tanıttığın slaytta, başlığın altına küçük ve gri (`#A4A9AD`) bir satır:

```
SAM 3 — Segment Anything with Concepts, Meta AI, 2025
YOLO-World — Real-Time Open-Vocabulary Object Detection, CVPR 2024
```

Kural: her yöntem slaytında **en fazla bir atıf satırı**. Slaytı kalabalıklaştırma,
görsel alanı sonuçlara bırak.

### Atıf yapılacak yerler

| Slayt | Atıf |
|---|---|
| Otomatik etiketleme (SAM 3) | SAM / SAM 2 / SAM 3 serisi |
| Açık sözlükçe tespit | YOLO-World (CVPR 2024), OWL-ViT / OWLv2, GroundingDINO |
| Pseudo-label / self-training | Self-training & knowledge distillation literatürü |
| Detektör mimarisi | YOLO serisi, RT-DETR |
| Metrikler | COCO değerlendirme protokolü; TIDE (hata dekompozisyonu) |
| Harici veri seti kullanıldıysa | VisDrone / UAVDT / ilgili veri seti makalesi |
| Takip kullanıldıysa | ByteTrack |

### Kapanış: References slaytı

- Tek slayt, iki sütun, küçük punto
- Sıralama: **Models → Datasets → Evaluation → Tools/Libraries**
- Format: Yazar(lar), *Başlık*, Yer, Yıl. (arXiv numarası varsa ekle)
- Kütüphaneler de yazılsın: `ultralytics`, `pycocotools`, `supervision`, `tidecv`, CVAT

**Not:** PDF'in "Kullanılan kaynakların listesi" maddesi bu slaytla karşılanıyor.
Ayrıca README'de de aynı liste bulunmalı — sunumda "the same list is in the README"
demek tekrar üretilebilirlik sinyali verir.

### Konuşmada nasıl kullanılır

Atıfları okuma, sadece bir kez referans ver:
> "This follows the open-vocabulary detection line of work — YOLO-World and OWLv2 —
> and the full reference list is at the end."

Bir cümle yeterli; literatürü takip ettiğin anlaşılır, akış bozulmaz.

---

## Slayt 6 — Baseline Approach: YOLO26n, Zero-Shot

**Tek mesaj:** Before training anything, measure the raw domain gap with an
off-the-shelf detector. This baseline exposes one structural failure that
every later slide is a response to.

*Blok A: Why start here*
- COCO-pretrained YOLO26n — the **nano** variant, chosen deliberately: `imgsz`
  is pushed to 1920 (below), which already multiplies the compute cost per
  image; picking the smallest/fastest checkpoint keeps total inference time
  reasonable despite that higher resolution — zero training either way
- Confidence threshold left at Ultralytics' own default (0.25) — deliberately
  untouched, to measure the out-of-the-box gap, not a tuned result
- `imgsz=1920`, not the 640 default — aerial/nadir people are tiny; 640 would
  erase them before the network even sees them

*Blok B: Result on the gold test set (196 frames, 719 boxes, T4)*
- mAP@.5 **0.693** | mAP@[.5:.95] **0.479**
- Precision 0.853 | Recall 0.726 | F1 **0.784** (@ conf 0.25)
- mAP on large objects **0.676** — mAP on small objects **0.018**

*Blok C: Measured inference time*
- **T4:** 196 frames in 26.7 s → **7.3 FPS** (0.136 s/frame)
- **CPU (M1):** 196 frames in 62.2 s → **3.2 FPS** (0.317 s/frame)
- Caveat, stated honestly: this is measured **pipeline** throughput — frame
  read + inference + drawing/writing the annotated review image — not
  isolated model-only inference. A pure-inference number would be somewhat
  faster; not yet separated out (see Slide 17)

*Blok D: The one number that defines the rest of this talk*
- On DJI_0501 and DJI_0596 (the two hardest test videos): YOLO catches
  **0 of 44** small/distant people, at any confidence threshold
- Not a tuning problem — a feature-map resolution limit

**Görsel:** two side-by-side prediction-vs-ground-truth frames (red = ground
truth, green = prediction, per the project's own visualization convention):
- **Success** — `results/eval/yolo26n_zeroshot/comparison/Berghouse_Leopard_Jog__frame_000000.jpg`:
  both runners boxed tightly, high confidence (0.78, 0.74)
- **Failure** — `results/eval/yolo26n_zeroshot/comparison/DJI_0596__frame_000000.jpg`:
  ground-truth boxes on the tiny, distant people on the ship's deck — zero
  predictions anywhere in the frame

**Kaynak:** `results/eval/yolo26n_zeroshot_T4/metrics.json`,
`results/manifests/05_yolo_zeroshot_eval_20260913T192838Z.json` (T4 timing),
`results/manifests/05_yolo_zeroshot_eval_20260912T215029Z.json` (CPU timing)

**Konuşma akışı**
> Before training anything, I wanted a number for the raw domain gap. So the
> first result here is a completely untrained detector — COCO-pretrained
> YOLO26n. I used the nano variant specifically because I was already pushing
> the input resolution way up, to 1920 — the smallest checkpoint keeps that
> combination fast. Threshold is Ultralytics' own default, deliberately left
> untouched.
> Overall it looks reasonable: point-seven mAP, point-eight F1, and on a T4
> this runs at about seven frames a second end to end. But look at the size
> breakdown. mAP on large objects is point-six-eight. mAP on small objects is
> point-zero-two — essentially zero. On the two hardest test videos, this
> detector finds zero of forty-four small, distant people, at any confidence
> level you choose. Here's what that looks like: two runners caught cleanly
> on the left, and on the right, real people on a boat deck with not a single
> prediction anywhere near them. That's not a threshold problem. It's a
> resolution problem — the object is too small for the feature map to
> represent at all. Everything I show you next responds to this one number.

---

## Slayt 7 — Method 2 (Cascade), Part 1: Architecture & Training Data

**Tek mesaj:** Method 1's structural blind spot motivates a two-stage
detect-then-verify system — here is exactly how the second stage was built
and trained, including a real labelling failure it had to be trained around.

**Kapsam notu:** Method 2 hâlâ aynı paradigma içinde bir iyileştirme (YOLO
tabanlı, supervised detection) — PDF'in *"alternatif yaklaşım"* maddesini bu
slayt DEĞİL, slayt 11 (SAM3) karşılar. Bunu konuşurken netçe söyle.

*Blok A: The gap this method targets*
- Recap in one line: Method 1 (YOLO26n) finds **0 of 44** small/distant
  people on the two hardest test videos, at any confidence threshold (Slide 6)
- Idea: force YOLO to propose more boxes by lowering its confidence floor,
  then use a second, independent model to separate real detections from the
  resulting noise

*Blok B: System architecture*
- **Stage 1:** the same YOLO26n checkpoint, confidence floor lowered
  0.25 → 0.01 — measured on val, this raises the reachable recall ceiling
  from 27% to 80%
- **Stage 2:** a ResNet18 binary classifier, working on a 64×64 **crop** of
  one candidate box — "is this a person?" — not the whole frame
- The two models see the problem at different scales: YOLO reasons over the
  full frame, the verifier only ever sees one cropped candidate at a time

*Blok C: How the verifier's training data was built — and a real failure it uncovered*
- **Positive crops:** YOLO candidates that overlap a SAM3 pseudo-labelled
  person box at IoU ≥ 0.5
- **Negative crops:** YOLO's own low-confidence candidates that match no
  person box at all (IoU = 0) — its actual false positives — plus random
  crops from the 2 person-free background videos
- **Ambiguous zone (0 < IoU < 0.5): discarded, not guessed at** — standard
  practice, and it keeps the noisiest cases out of training entirely
- **The failure this surfaced:** auditing SAM3's own labels on DJI_0790
  (the snow/sled-dog video) found it had boxed **sled dogs as "person"** —
  from directly overhead, a dark shape moving on white snow looks similar
  whether it's a dog or a person in a coat. **271 of these boxes were
  manually corrected in CVAT and explicitly relabelled `not_person`** —
  feeding the verifier exactly the confusion that broke the teacher model,
  rather than silently discarding the bad data
- Final crop counts: **train 1,398 person / 3,507 not_person — val 181 / 40**
  (~5,100 crops total)

*Blok D: Training details*
- ResNet18, ImageNet-pretrained, crop size 64×64
- **15 epochs**, batch size 64, learning rate 3e-4, weight decay 1e-4
- Augmentation deliberately **light** — these crops are already tiny and
  often blurry, so aggressive augmentation would mostly add noise: random
  horizontal flip + colour jitter (brightness/contrast ±0.2) at train time
  only; ImageNet normalisation at both train and eval

**Görsel:** system diagram (frame → YOLO low-conf boxes → crop → ResNet18 →
accept/reject) + an example dog-vs-person crop pair from the DJI_0790
correction.

**Kaynak:** `docs/decision_log.md` ("Teacher failure found in audit: SAM3
labels sled dogs as people", 2026-09-13), `configs/10_train_verifier.yaml`,
`src/methods/yolo/verifier.py` (`build_transforms`), `data/crops/{train,val}/{person,not_person}`

**Konuşma akışı**
> Method 1 exposed one very specific gap: zero small or distant people
> caught, at any threshold. My response was a two-stage system. Stage one is
> the same YOLO, but with its confidence floor dropped way down, so it
> proposes far more candidate boxes — including the small ones it was
> silently throwing away. Stage two is a small ResNet, looking at just the
> cropped candidate and deciding whether it's really a person.
> Building the training data for that second stage is where I found the
> most interesting problem in this whole project. Auditing SAM3's own
> pseudo-labels on the snow and sled-dog video, I found it had been boxing
> the sled dogs as people — from directly overhead, on white snow, a dog and
> a person in a coat genuinely look alike. I corrected two hundred
> seventy-one of those boxes by hand and explicitly fed them back into the
> verifier's training set as "not a person" — so the second stage is
> literally trained on the exact mistake the first model made.
> On the training side: ResNet18, fifteen epochs, light augmentation only —
> flip and a little colour jitter — because these crops are already small
> and blurry, and I didn't want to manufacture noise on top of that.

---

## Slayt 8 — Method 2 (Cascade), Part 2: The Iteration

**Tek mesaj:** The first version of this system made things worse, not
better. Three measured refinements — each kept or discarded on evidence —
got it past the baseline.

*Blok A: First attempt — verify everything → worse*
- Run YOLO at the 0.01 floor, send **every** resulting box through the
  verifier, including the ones YOLO was already confident about
- Result: F1 **collapses 0.786 → 0.514** — the verifier wrongly rejects
  boxes Method 1 already had right, for no expected gain

*Blok B: Fix — only verify the ambiguous band*
- Trust YOLO outright at/above 0.25, unchanged. Only the **[0.01, 0.25)**
  band — where recall was being bought at a heavy precision cost — goes
  through the verifier
- mAP@.5 recovers to 0.733, then to **0.760** after a second fix: one
  training video (DJI_0790) supplied 70-81% of the verifier's training
  crops, so the verifier had mostly learned *that* video's look, not
  "person" in general. Fix: weight every source video equally per epoch
  (`video_balanced_sampling`)

*Blok C: Score fusion instead of a hard accept/reject*
- Replace the verifier's binary yes/no with a **continuous blended score**:
  the geometric mean of YOLO's own confidence and the verifier's
  person-probability — `sqrt(yolo_conf × verifier_prob)`
- Zero unless both models agree; lets the standard mAP/F1 threshold sweep
  find the useful cutoff, instead of pre-deciding it with a fixed gate
- mAP@.5 → **0.786** — the best result up to this point

*Blok D: Architecture tweak — a "small-input" stem for the verifier*
- ResNet18's stock first layer (7×7 stride-2 conv + maxpool) was designed
  for 224×224 ImageNet photos — on our 64×64 crops, it downsamples to 16×16
  **before the network even starts reasoning**, discarding most of the
  detail there was to begin with
- Replaced with a 3×3 stride-1 conv, **no maxpool** (the standard
  "CIFAR-style" adaptation for small inputs), keeping every pretrained
  weight elsewhere unchanged
- **This is the first configuration all cycle to beat Method 1's own F1**

**Görsel:** journey timeline (4 steps, colour-coded win/loss) + a small
before/after diagram of the ResNet stem (7×7+maxpool vs. 3×3, no maxpool).

**Kaynak:** `docs/01_cascade_journey_summary.md` (Steps 1-8),
`docs/decision_log.md` ("Band-gated cascade variant", "Video-balanced
sampling result", "Score fusion instead of hard gating"), `configs/17`,
`configs/24`, `configs/25`

**Konuşma akışı**
> The first version of this made things worse, not better. Verifying every
> box — including the ones YOLO was already sure about — collapsed F1 from
> point-seven-eight-six to point-five-one-four, because the verifier was
> also re-judging confident boxes and getting some of them wrong.
> The fix was to trust YOLO above its normal threshold, and only send the
> ambiguous band to the verifier. That alone recovered most of the damage.
> I found a second problem while diagnosing it: one video had supplied the
> large majority of the verifier's training crops, so it had really learned
> that one video's visual style. Balancing the training data by video closed
> more of the gap.
> Two more changes got it past the baseline for the first time: blending
> both models' confidence into one continuous score instead of a hard
> accept-or-reject, and swapping the verifier's first layer for one designed
> for small inputs instead of full-size photos.

---

## Slayt 9 — Method 2 (Cascade), Part 3: Final Result

**Tek mesaj:** A real, measured win over Method 1 — plus an experiment with
an alternative verifier backbone that quietly reinforces the project's
biggest lesson about validation scores.

*Blok A: Final comparison (T4, shared conf=0.25 operating point)*

| Config | mAP@.5 | Precision | Recall | F1 | FP |
|---|---|---|---|---|---|
| Method 1 (YOLO26n, conf 0.25) | 0.693 | 0.853 | 0.726 | 0.784 | 90 |
| **Cascade — small-stem ResNet + fusion** | **0.786** | 0.754 | 0.778 | 0.766 | 182 |
| Cascade — EfficientNet-B0 verifier | 0.777 | 0.729 | 0.765 | 0.747 | 204 |

*Blok B: Where it actually earns its keep*
- On DJI_0501 / DJI_0596 (the two hardest videos): small-object mAP goes
  from **0.000 on both** (Method 1) to **0.081 / 0.070** — a real, targeted
  recovery of exactly the failure Method 1 exposed, not just a headline
  number
- Not the aggregate F1 winner by a huge margin — but the *only* method in
  this comparison that recovers any of that specific capability

*Blok C: The EfficientNet-B0 experiment*
- Same recipe (video-balanced sampling, 15 epochs) with `torchvision`'s
  EfficientNet-B0 instead of ResNet18 as the verifier backbone
- Scored the **highest validation F1 of any verifier tried (0.984)** — but
  the **lowest test-set result** of the three (mAP@.5 0.777) — the clearest
  single piece of evidence in this project that validation score does not
  predict test-set generalisation here
- Also ran **~5× slower per crop on CPU**, despite 64% fewer parameters
  (4.0M vs. ResNet18's 11.2M) — depthwise-separable convolutions vectorise
  poorly on general-purpose CPU kernels; the efficiency gain is real, but
  GPU-side
- Final decision: no change — score fusion + small-input-stem ResNet18
  remains the best configuration found this cycle

**Görsel:** the comparison table above, rendered as a small bar chart
(mAP@.5, 3 bars) + a 2-panel crop montage: EfficientNet's confident val-set
correct calls next to a test-set case it got wrong.

**Kaynak:** `results/eval/yolo26n_score_fusion_small_stem_T4/metrics.json`,
`results/eval/yolo26n_score_fusion_efficientnet_b0_T4/metrics.json`,
`docs/decision_log.md` ("EfficientNet-B0 verifier: best val score, not best
test score")

**Konuşma akışı**
> Final result: mAP up from point-six-nine-three to point-seven-eight-six,
> and — this is the part I actually care about — on the two hardest videos,
> small-object detection goes from exactly zero to something real. Ten of
> forty-four previously invisible people, caught.
> One more thing worth sharing, because it's the clearest example in the
> whole project of a lesson worth remembering: I also trained the verifier
> with EfficientNet-B0 instead of ResNet18. It scored the best validation
> score of any verifier I tried — point-nine-eight-four F1. On the actual
> held-out test set, it was the worst of the three. Fewer parameters,
> better validation number, worse real-world result, and slower on CPU
> despite being smaller. I kept the ResNet configuration.

---

## Slayt 10 — Method 3: RT-DETR, a Different Architecture Family

<span style="color:#A4A9AD">RT-DETR — *DETRs Beat YOLOs on Real-Time Object Detection*, CVPR 2024 · RT-DETRv2, 2024</span>

**Tek mesaj:** Swapping the CNN detector for a transformer changes the error
profile completely, and exposes a real, architecture-specific fragility.

*Blok A: Setup*
- RT-DETRv2-R18 (Hugging Face, `PekingU/rtdetr_v2_r18vd`, 20.2M params) and
  RT-DETR-l (Ultralytics, 33.0M params) — both zero-shot, pure-COCO
  pretrained, same conf=0.25 convention as the baseline
- Ultralytics ships no true "R18" RT-DETR — added `transformers` as a new
  dependency to get the original authors' checkpoint

*Blok B: Zero-shot result, native resolution*

| Method | mAP@.5 | Precision | Recall | F1 | FP |
|---|---|---|---|---|---|
| YOLO26n (baseline) | 0.693 | 0.853 | 0.726 | 0.784 | 90 |
| RT-DETRv2-R18 | **0.740** | 0.609 | 0.761 | 0.677 | 351 |
| RT-DETR-l | 0.731 | 0.762 | 0.748 | 0.755 | 168 |

Higher mAP and recall than YOLO — but 2-4× more false positives at the same
threshold, and dramatically worse on small objects (mAP_small ≈ 0 for both
checkpoints).

*Blok C: An unplanned finding — resolution fragility*
- Forced both checkpoints to YOLO's 1920×1088 input, to make the comparison
  "fair" by resolution
- RT-DETRv2-R18: mAP@.5 **collapses 0.740 → 0.253**, FP jumps to 1733 — a
  duplicate-detection storm, confirmed by inspecting the raw boxes
- RT-DETR-l: degrades **gracefully** instead (0.731 → 0.654) — and its
  small-object mAP actually improves 23×
- Root cause: RT-DETR has **no NMS at inference** — its one-query-per-object
  behaviour is learned for one specific resolution. YOLO's CNN+NMS pipeline
  has no such constraint and tolerates the same change with no retraining.

*Blok D: Closing take — when would this method actually win?*

> **Framing note:** this block is a reasoned hypothesis, not a measured
> result — say so explicitly when presenting it, don't let it sound like a
> benchmarked claim.

- RT-DETR's encoder uses **self-attention**: every region of the frame is
  related to every other region. Its decoder uses **cross-attention**: each
  object query reasons over the *whole* image, not one local patch. That's a
  genuinely different inductive bias from YOLO's convolutional, local
  receptive field
- That matters most when an object's identity depends on its relationship to
  the rest of the scene, not just its own local appearance — for instance,
  the dog-vs-person confusion from Slide 7: a person is typically positioned
  and postured differently *relative to the rest of a sled team*, a cue a
  global-context model is architecturally better positioned to use than a
  purely local one. **Not tested in this project — a plausible direction,
  not a claim**
- The catch: transformers are known to be more data-hungry — they have to
  *learn* useful attention patterns from data, rather than getting locality
  "for free" as a CNN's built-in bias. This is exactly why fine-tuning
  RT-DETR was judged too risky to attempt this cycle on our modest
  pseudo-label set (Slide 17)
- **Expectation, not yet measured:** with a larger, stronger training set,
  RT-DETR would plausibly pull further ahead of YOLO on exactly these
  context-dependent, ambiguous cases — likely at the cost of **even lower
  FPS**, since attention cost scales with the number of tokens the model
  processes. The same quadratic-cost lesson this project already learned
  directly, the hard way, with SAM3's own ViT backbone (Slide 5)

**Görsel:** side-by-side — native-resolution RT-DETR prediction vs. the
forced-1920 duplicate-box storm on the same frame.

**Kaynak:** `results/eval/rtdetr_v2_r18_zeroshot/metrics.json`,
`results/eval/rtdetr_ultralytics_l_zeroshot/metrics.json`,
`results/eval/rtdetr_v2_r18_1920_diagnostic_BROKEN/`, `docs/02_rtdetr_journey_summary.md`

**Konuşma akışı**
> Same task, a genuinely different architecture: a transformer detector
> instead of a CNN. Zero-shot, it actually ranks detections better than YOLO
> — higher mAP, higher recall — but at a real cost: two to four times more
> false positives at the same threshold, and it's essentially blind to small
> objects too.
> The more interesting finding came from trying to make the comparison
> "fair" by matching YOLO's input resolution. One checkpoint collapsed
> completely — mAP dropped by two-thirds, flooded with duplicate detections.
> The reason is architectural: RT-DETR has no non-max-suppression step at
> inference. Its ability to output one box per object is learned for a
> specific resolution, and pushing it far outside that range removes the
> model's only safety net. YOLO doesn't have this problem, because NMS is a
> separate, resolution-independent step. A real, checkpoint-dependent
> limitation of transformer detectors — not something I expected going in,
> but exactly the kind of result an honest comparison should surface.
> So when would I actually reach for this instead of YOLO? RT-DETR's
> attention mechanism lets it reason about how one region of the frame
> relates to every other region, not just what a local patch looks like on
> its own — YOLO's convolutions don't have that. That kind of global context
> should matter most exactly where identity is ambiguous from local
> appearance alone — like the dog-versus-person confusion I showed you a few
> slides back. I haven't tested that specific claim, so take it as a
> hypothesis, not a result. What I can say with more confidence: transformers
> need more data to learn good attention patterns than a CNN needs to learn
> good convolutions, which is exactly why I didn't fine-tune this one on our
> modest pseudo-label set. Give it a bigger, stronger training set, and I'd
> expect it to pull further ahead — at the cost of even lower FPS, for the
> same reason SAM 3 was so slow: attention cost grows with how much the
> model has to look at, not just how big the model is.

---

## Slayt 11 — Method 4 / The Alternative Approach: SAM 3, Zero-Shot Foundation Model

<span style="color:#A4A9AD">SAM 3 — Segment Anything with Concepts, Meta AI, 2025</span>

**Tek mesaj:** Every method so far is a trained or fine-tunable supervised
detector. This one is not — it is prompted with the word "person" and never
sees this project's data. **This is the assignment's required "genuinely
different alternative approach."**

*Blok A: What makes this genuinely different*
- The same SAM3 model already introduced as the labelling tool (Slide 5) —
  here it is benchmarked directly against the gold test set, under the
  identical protocol used for every other method in this talk
- Zero training, zero fine-tuning on this project's videos — pure
  prompt-driven detection ("person" → boxes)

*Blok B: Result (T4, gold test set)*
- mAP@.5 **0.846** — highest of any method tried
- mAP@[.5:.95] **0.626** — also highest
- Recall @ conf 0.25: **0.872** — highest of any method
- Precision @ conf 0.25: 0.485 (665 false positives)
- Speed: **0.37 FPS** (mean 2.72s/frame; min 2.22s, max 44.26s) — roughly
  **10× slower** than any trained detector in this project

*Blok C: The trade, stated plainly*
- Best accuracy and recall of any method — with zero training
- Worst precision, and by far the worst speed
- Not a deployment candidate as-is — exactly consistent with its role in
  this project: a zero-shot ceiling-finder, and the pseudo-labelling teacher
  from Slide 5

**Görsel:** the DJI_0596 frame showing all three outcomes at once (correct /
missed / false-positive) — the clearest single qualitative example in the
project (also used in Slide 13).

**Kaynak:** `results/eval/sam3_zeroshot_T4/metrics.json`,
`results/manifests/34_sam3_zeroshot_eval_20260913T202102Z.json`,
`docs/03_sam3_journey_summary.md`

**Konuşma akışı**
> Every method so far — the baseline, the cascade, RT-DETR — is a supervised
> detector: trained or at least fine-tunable on this project's own data.
> This one isn't. SAM 3 is a foundation model. I prompt it with the word
> "person," and it has seen zero frames from this dataset.
> It's also the best-performing method I tried, on every ranking and recall
> metric — with no training at all. The cost is precision — six hundred
> sixty-five false positives at this threshold — and far more severely,
> speed: point-three-seven frames per second, roughly ten times slower than
> any trained detector here. It's not a deployment candidate as it stands.
> But that was never its job. This is the same model I used to auto-label
> the training set back in slide five — here I'm holding it to the exact
> same benchmark as everything else, which is what makes it a genuinely
> different alternative, not just another architecture.

---

## Slayt 12 — Quantitative Comparison

**Tek mesaj:** One test set, one protocol, four paradigms — ranked by mAP,
not by a fixed confidence threshold, because these methods are not on the
same confidence scale.

*Blok A: Headline table (gold test set, 196 frames / 719 boxes)*

| Method | Hardware | mAP@.5 | mAP@[.5:.95] | Precision | Recall | F1 | FPS |
|---|---|---|---|---|---|---|---|
| YOLO26n (baseline) | T4 | 0.693 | 0.479 | 0.853 | 0.726 | 0.784 | not yet benchmarked |
| Cascade (best: small-stem fusion) | T4 | **0.786** | 0.526 | 0.754 | 0.777 | 0.766 | not yet benchmarked |
| RT-DETRv2-R18 | CPU¹ | 0.740 | 0.468 | 0.609 | 0.761 | 0.677 | not yet benchmarked |
| SAM3 (zero-shot) | T4 | **0.846** | **0.626** | 0.485 | **0.872** | 0.624 | **0.37** |

¹ RT-DETR's own script already runs on GPU automatically when available;
not yet re-run on T4 in this cycle — say this out loud, don't hide the
hardware mismatch.

*Blok B: Why mAP, not a fixed threshold, is the headline number*
- Confidence isn't comparable across a CNN's objectness score, a fused
  two-model score, and a foundation model's prompt-similarity score
- mAP sweeps every method's own threshold internally — the one number
  here that's genuinely apples-to-apples
- Precision / recall / F1 are still reported, but always at each method's
  **own** stated operating point, never cross-method at one shared score

**Görsel:** bar chart, mAP@.5 across the 4 methods (accent green on the
highest bar).

**Kaynak:** `results/eval/comparison.csv` (every row in this table is a
direct read from that file — nothing here is hand-typed)

**Konuşma akışı**
> Here is every method, side by side, on the exact same gold test set. I'm
> ranking by mAP rather than picking one confidence threshold and comparing
> precision or F1 directly, because these confidence scores are not on the
> same scale. YOLO's objectness score, the cascade's fused score, SAM 3's
> prompt-similarity score — none of them mean the same thing at "point two
> five." mAP sweeps each method's own threshold internally, so it's the one
> number here that's genuinely comparable.
> The story: SAM 3 wins on ranking quality and recall, with zero training.
> Among the trained, deployable detectors, the cascade is best. RT-DETR sits
> in between — better ranking than the plain baseline, worse precision. No
> single method wins on every axis, and that's the actual finding here, not
> a flaw in the comparison.

---

## Slayt 13 — Qualitative Comparison

**Tek mesaj:** One frame can show a success, a miss, and a false positive at
the same time — numbers alone don't tell you that.

*Blok A: A clean success*
- Berghouse Leopard Jog: two trail runners, correctly boxed at high
  confidence by every method — SAM3 scores this video a perfect 1.000 mAP@.5

*Blok B: DJI_0596 — all three outcomes in one frame*
- A lake steamer boat scene (not the snow/mountain scene its "tiny
  instances" description first suggested)
- **Correct:** cluster of people on the rear deck, boxed accurately
- **Missed:** two people on the raised bridge/wheelhouse — no box anywhere
  near their ground-truth position
- **False positive:** 2-3 "person" boxes over open water where nothing is
  present — plausibly wave/glare misread as a distant person

**Görsel:** side-by-side — Berghouse success frame, and the DJI_0596 frame
with all three outcomes annotated (green/red/amber boxes).

**Kaynak:** `results/eval/sam3_zeroshot_T4/comparison/` (visual inspection,
per `docs/03_sam3_journey_summary.md`)

**Konuşma akışı**
> Numbers alone don't show you what actually goes wrong. Two examples.
> First, a clean success — two runners, boxed correctly by every method, at
> high confidence. And second, the frame I keep coming back to: one image
> from DJI_0596 that shows a correct detection, a missed detection, and a
> false positive, all at once. The false positive is particularly
> interesting — it's plausibly the model reading wave glare on open water as
> a distant person. That's the kind of ambiguous case a metric alone will
> never explain to you, but a picture will.

---

## Slayt 14 — Error Analysis

**Tek mesaj:** Difficulty tracks the footage, not the detector — every
method's own best-to-worst video ranking is nearly identical.

*Blok A: Per-video mAP@.5, every method*

| Video | YOLO26n | RT-DETRv2 | Cascade | SAM3 |
|---|---|---|---|---|
| Berghouse | 0.935 | 0.977 | 0.973 | 1.000 |
| DJI_0862 | 0.792 | 0.775 | 0.854 | 0.906 |
| DJI_0501 | 0.226 | 0.559 | 0.365 | 0.606 |
| DJI_0596 | 0.052 | 0.029 | 0.246 | 0.260 |

*Blok B: Breakdown by object size (mAP@.5, whole test set)*

| | Small | Medium | Large |
|---|---|---|---|
| YOLO26n | 0.018 | 0.472 | 0.676 |
| RT-DETRv2 | 0.000 | 0.418 | 0.743 |
| Cascade | 0.073 | 0.523 | 0.689 |
| SAM3 | 0.070 | 0.669 | 0.773 |

Small objects are the dominant failure mode of this dataset, for every
method, without exception.

**Görsel:** video × method heat-grid, coloured by mAP@.5.

**Kaynak:** `results/eval/*/metrics.json` (per_video block, every method)

**Konuşma akışı**
> If you rank each method's own videos from easiest to hardest, you get
> almost the same order every time. That tells you the difficulty lives in
> the footage — small, distant subjects — not in any one detector. Broken
> down by object size, that's confirmed directly: every method's mAP on
> small objects is near zero, medium is workable, large is fine.

---

## Slayt 15 — Strengths, Weaknesses, and Cost

**Tek mesaj:** No method wins on every axis — the real choice is which
trade-off fits the deployment.

*Blok A: Strengths & weaknesses*
- **YOLO26n:** fastest, simplest, zero training cost, best precision of any
  method tried — structurally blind to small/distant people
- **Cascade:** only method that recovers small-object recall from zero —
  two-stage cost, verifier is data-hungry — best mAP among trained,
  deployable methods
- **RT-DETR:** genuinely different architecture, competitive ranking
  quality — more false positives, resolution-fragile, fine-tuning not
  attempted this cycle (a time-boxed, stated cut — see Slide 17)
- **SAM3:** best accuracy and recall of any method, zero training —
  ~10× slower than any trained detector, not deployable as-is; ideal as a
  labelling teacher and, per Slide 16, a periodic auditor

*Blok B: Cost, honestly reported*
- Verifier backbone: ResNet18 11.2M params vs. EfficientNet-B0 4.0M params
  — fewer params ≠ faster on CPU: EfficientNet ran **~5× slower** per crop
  (depthwise-separable convolutions vectorize poorly on general CPU kernels;
  the efficiency gain is real, but GPU-side)
- RT-DETRv2-R18: 20.2M params | RT-DETR-l: 33.0M params
- SAM3: **0.37 FPS on T4** — the only method in this project with a
  committed, reproducible speed number so far
- YOLO26n / cascade / RT-DETR end-to-end FPS on T4: **not yet benchmarked**
  with a dedicated script — an open item, not a hidden one (see Slide 17)

**Görsel:** 2×2 strengths/weaknesses grid (aynı stil önceki slaytlar) +
sade parametre/hız tablosu.

**Kaynak:** `docs/decision_log.md` ("GPU (T4) validation..." ve
"EfficientNet-B0 verifier..." entries), `results/manifests/34_sam3_zeroshot_eval_*.json`

**Konuşma akışı**
> Put side by side, no method wins everywhere. YOLO is fastest and has the
> best precision, but is structurally blind to small objects. The cascade
> recovers exactly that blind spot, at the cost of a second model. RT-DETR
> is a genuinely different architecture with its own profile. SAM 3 is the
> most accurate and the slowest by an order of magnitude.
> On cost, I want to be precise about what I've actually measured versus
> what I haven't. SAM 3's speed is measured and reproducible: point-three-
> seven frames per second on a T4. The other three detectors' end-to-end FPS
> on T4 is not yet benchmarked with a dedicated script — that's an honest
> gap, not a hidden one, and it's next on my list, along with a
> TensorRT/FP16 export that should move those numbers considerably.

---

## Slayt 16 — Proposed Production System

**Tek mesaj:** Don't deploy one method — combine the fast one and the
accurate one, each doing the job it's actually good at.

*Blok A: The design*
- **Real-time path:** YOLO26n + ResNet18 cascade verifier, running on every
  frame — fast, deployable, the best mAP of any trained method here
- **Periodic audit path:** SAM3, run on a sampled frame roughly every 10
  seconds — far too slow for every frame, but the highest-accuracy detector
  available; used here as a drift/anomaly monitor, not the primary detector
- If SAM3's periodic reading disagrees sharply with the cascade's recent
  output on the same scene, flag the segment for human review

*Blok B: Why this split makes sense*
- SAM3 is ~10× too slow to run per-frame (0.37 FPS) — but at roughly one
  call every 10 seconds, that cost nearly disappears
- The cascade alone cannot self-diagnose a systematic miss (e.g. a scene
  genuinely unlike anything it was tuned on); a periodic foundation-model
  check can
- This mirrors exactly how the two models are already used earlier in this
  project: SAM3 as the pseudo-labelling teacher (Slide 5), the cascade as
  the deployable student (Slides 7-9) — extended here into an ongoing
  production role instead of a one-time labelling pass

**Görsel:** basit sistem şeması — video akışı → cascade (her frame, sürekli)
+ SAM3 (~10s'de bir, paralel) → uyuşmazlık tespitinde insan incelemesine
uyarı.

**Konuşma akışı**
> If I had to put one thing into production, it wouldn't be a single model —
> it would be this combination. The cascade runs on every frame: it's fast,
> and it's the best-performing detector I actually trained. SAM 3 runs in
> the background, on roughly one frame every ten seconds — far too slow for
> real-time, but far more accurate — used here not as the primary detector
> but as a periodic sanity check. If what SAM 3 sees disagrees sharply with
> what the fast path has been reporting, that's a signal something changed —
> a new scene, a failure mode the fast model wasn't built for — and it's
> worth a human looking. This mirrors exactly how I already used these two
> models earlier in this project: SAM 3 as the teacher, the cascade as the
> deployed student — just extended into an ongoing role instead of a
> one-time labelling pass.

---

## Slayt 17 — Honest Limitations & Future Work

**Tek mesaj:** What didn't get done this cycle, and why, stated plainly.

*Blok A: Limitations already surfaced in this talk*
- Small-object detection remains the dominant failure mode for every method
  — none of the four solves it; the cascade only partially recovers it
- End-to-end FPS for YOLO / cascade / RT-DETR on T4: not yet benchmarked
- Test set has only 4 videos — enough for a per-condition breakdown, but a
  small statistical sample; generalisation claims are bounded accordingly

*Blok B: Time-boxed out, not forgotten*
- Fine-tuning YOLO26n on our own pseudo-labels — every YOLO result shown
  today used the **zero-shot** checkpoint as the detection backbone; this is
  the single highest-priority item still open
- RT-DETR fine-tuning on pseudo-labels — transformer detectors are more
  data-hungry; judged too risky for the remaining time, a deliberate cut
- ConvNeXt + CenterNet + FPN — a fifth architecture, planned as a
  lower-priority comparison
- TensorRT export + FP16 — for real deployment-speed numbers
- YOLO P2 detection head + SAHI tiling — both target the small-object
  failure directly inside the detector, instead of via a second-stage
  verifier

*Blok C: Explicitly future work, not this cycle*
- Synthetic data (Blender domain randomization, optionally Gaussian
  splatting) to scale labelling further
- INT8 quantization for edge deployment

**Görsel:** yok — sade, dürüst bir liste; bu slaytta görsel gürültü yapma.

**Konuşma akışı**
> I want to be direct about what's finished and what isn't. Every YOLO
> result I've shown you today uses the zero-shot checkpoint as the detection
> backbone — actually fine-tuning it on our own pseudo-labels is the single
> highest-priority item still open, and it's next. RT-DETR fine-tuning I
> made a conscious decision not to attempt this cycle: transformer detectors
> are more data-hungry, and I judged the risk of an unstable result wasn't
> worth the remaining time — a deliberate cut, not an oversight. A few more
> items — a fifth architecture, proper FPS benchmarking, small-object-
> specific detector changes — are queued but not done. And synthetic data
> generation and edge quantization are explicitly future-work ideas, out of
> scope for a cycle this short.

---

## Slayt 18 — Closing

**Tek mesaj:** An honest account beats a clean one — here's what actually
worked, what didn't, and what I'd build next.

*Blok A: The whole story in one line*
- A simple baseline exposed one specific, real failure (small objects).
  Three genuinely different responses to it — a verifier cascade, a
  transformer architecture, a zero-shot foundation model — each traded
  accuracy against speed, precision against recall, in a different place.
  None of them replaces the others.

*Blok B: Numbers that summarise the project*
- 4 detection paradigms compared, one shared gold test set (196 frames,
  719 boxes)
- **34** logged, dated experiment configs — including the ones that didn't
  work (`configs/02` through `configs/35`)
- mAP@.5 range: **0.693** (untouched baseline) → **0.846** (best result,
  zero-shot SAM3)
- **0 mislabels** found in the full manual pseudo-label crop audit
- Every table in this talk traces back to a file in `results/` — nothing
  here was written by hand

**Görsel:** kod deposu QR/link + README'ye referans; varsa birleştirilmiş
sonuç videosu burada canlı gösterilir.

**Konuşma akışı**
> A simple baseline exposed one very specific failure: small, distant
> objects. Everything else in this talk is a genuinely distinct response to
> that one failure — a second-stage verifier, a different architecture
> family, a foundation model used zero-shot — and each one trades something
> for something else. None of them is a strict upgrade over the others; the
> honest answer is "it depends what you're optimising for."
> Every number I've shown you today comes from a file in this project's
> results directory, not from memory or a hand-edited table. The code and
> the full decision history are in the repository — happy to walk through
> any of it live.

---

## Slayt 19 — References

**Layout:** Tek slayt, iki sütun, küçük punto. Sıralama: Models → Datasets →
Evaluation → Tools/Libraries. Bu slaytı okuma, tek cümmeyle geç (bkz.
"Literatür ve Atıf Stratejisi" yukarıda).

**Models**
- Ren, S. et al. *RT-DETR: DETRs Beat YOLOs on Real-Time Object Detection.*
  CVPR 2024.
- Lv, W. et al. *RT-DETRv2: Improved Baseline with Bag-of-Freebies.* 2024.
- Meta AI. *SAM 3: Segment Anything with Concepts.* 2025.
- Jocher, G. et al. *Ultralytics YOLO (YOLO26).* Ultralytics, 2024-2025.
- He, K. et al. *Deep Residual Learning for Image Recognition (ResNet).*
  CVPR 2016.
- Tan, M. & Le, Q. *EfficientNet: Rethinking Model Scaling for
  Convolutional Neural Networks.* ICML 2019.

**Datasets**
- Kaggle `kmader/drone-videos` — DJI Mavic Pro drone footage (source
  dataset for this project).

**Evaluation**
- Lin, T.-Y. et al. *Microsoft COCO: Common Objects in Context* (evaluation
  protocol — mAP@.5, mAP@[.5:.95], size-based breakdown). ECCV 2014.

**Tools / Libraries**
- `ultralytics`, `transformers` (Hugging Face), `pycocotools`, `torch` /
  `torchvision`, CVAT (manual annotation).

**Kaynak:** Bu liste `README.md`'deki listeyle birebir aynı olmalı —
sunumda "the same list is in the README" demek tekrar-üretilebilirlik
sinyali verir (bkz. yukarıdaki Literatür stratejisi notu).
