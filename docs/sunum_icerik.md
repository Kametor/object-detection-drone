# Object Detection with Limited Data — Sunum İçeriği

> Yaşayan doküman. Her slayt netleştikçe güncellenir.

## Meta

- **Sunan:** Mehmet Recep Aşkar
- **Süre:** 20-25 dk, hızlı tempo
- **Slayt metni ve konuşma dili:** İngilizce
- **Hedef his:** Dinleyici film izler gibi takip etsin; her slayt bir öncekinin açtığı soruyu kapatsın
- **Konuşma metni:** Sunum bittikten sonra bütün hâlinde yazılacak

### Renk paleti (Roketsan kurumsal — 2026-09-16'da resmî marka kılavuzuyla
[roketsan.com.tr/uploads/docs/1709195136_roketsanmarkakilavuzu.pdf] doğrulandı)

| Rol | Pantone | HEX | RGB | CMYK |
|---|---|---|---|---|
| Vurgu (başlık, önemli sayı, grafik ana seri) | 7740 C (ana) | `#3A913F` | 58, 145, 63 | 80/20/100/5 |
| Ana metin | Black C (ana) | `#1D1D1B` | 29, 29, 27 | 0/0/0/100 |
| İkincil metin, çizgi, panel | 429 C (tamamlayıcı) | `#A2AAAD` | 162, 170, 173 | 35/23/19/2 |
| **İkincil vurgu** (gerekli yerlerde — ör. tablo highlight, ikinci seri) | **729 C (tamamlayıcı)** | **`#B58150`** | **181, 129, 80** | **30/47/73/7** |

**Karar (2026-09-16):** Arka plan **beyaz/açık zemin** — kılavuz hem beyaz hem
tam yeşil zeminde logo kullanımını onaylı gösteriyor, ama 20 slaytlık teknik
bir sunumda okunabilirlik/kontrast riski nedeniyle beyaz seçildi. Bronz
(729 C) gerekli yerlerde ikincil vurgu olarak kullanılır. Blur'lu/karartılmış
full-bleed görsel KULLANMA. Görseller net, kendi başına duran küçük kartlar
hâlinde yerleştirilir.

**Not — font:** Kılavuz tasarım için `Campton` fontunu, **ofis dokümanları
(Word/PowerPoint/Excel) için Arial veya Calibri**'yi resmî font olarak
belirtiyor. `docs/presentation/deck.html` şu an Google Fonts'tan Archivo +
IBM Plex kullanıyor (Campton lisanslı, CSP'de izinli font host'larında yok)
— nihai PowerPoint'te Calibri/Arial'e geçilecek, bu HTML önizleme amaçlı.

**Tema notu:** `deck.html` artık görüntüleyenin sistem koyu/açık temasından
bağımsız, hep açık/beyaz zeminle render ediliyor (sabit sunum çıktısı için
bilinçli tercih — kişiye göre değişen bir arayüz değil).

---

## ÖDEV KONTROL LİSTESİ → SLAYT EŞLEMESİ

PDF'in "Sonuçların Sunulması" ve "Değerlendirme" maddeleri. Hiçbiri açıkta kalmayacak.

| PDF maddesi | Slayt |
|---|---|
| Seçilen hedef ve kullanılan veri bölümü | 3, 4 |
| Veri hazırlama ve etiketleme stratejisi | 4, 5, 6 |
| Başlangıç yaklaşımı (Method 1) | 7 |
| Alternatif yaklaşım (Method 2 — Cascade) | 8 (mimari/güven eşiği), 9 (verifier eğitimi), 10 (iterasyon), 11 (final sonuç) |
| Alternatif yaklaşım (Method 3 — farklı mimari) | 12 |
| Alternatif yaklaşım (Method 4 — gerçek alternatif, SAM3) | 13 |
| Nicel ve nitel karşılaştırma | 14 (nicel), 15 (nitel) |
| Başarılı / başarısız / belirsiz sonuçlar | 15, 16 |
| Hata analizi | 17 |
| Güçlü ve zayıf yönler | 18 |
| Hesaplama maliyeti | 18 |
| Metrik seçiminin gerekçesi | 14 (Blok B, C) |
| Colab notebook / kod deposu | 21 (Kapanış) + canlı göster |
| README | 21 (Kapanış) |
| Nicel sonuç tablosu | 14 |
| Başarılı/başarısız örnekler | 15, 16 |
| Kaynak listesi | 22 (References) + slayt içi inline atıflar (12, 13) |
| Sonuç videosu | 21 (Kapanış) — varsa canlı göster |
| Final sistem önerisi | 19 |
| Dürüst limitasyonlar / kalan işler | 20 |

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
Computer Vision — Technical Presentation

Object Detection
Under Label Scarcity

Thirteen short drone video clips, almost no ground truth —
how do you build and validate an object detection system anyway?

Mehmet Recep Aşkar
Computer Vision Engineer
```

**Kicker tartışması (2026-09-16):** "Computer Vision — Technical
Presentation" yerine ödevin adını yazmak düşünüldü, ama başlığın kendisi
zaten konuyu ("Object Detection Under Label Scarcity") söylüyor —
kicker'ın işi farklı: bu bir CV teknik sunumu olduğu bağlamını vermek.
İkisi çakışmadığı için kicker değiştirilmedi.

**Başlık kontrolü:** "Under Label Scarcity" hem küçük veri seti hem de
etiket eksikliğini tek ifadede birleştiriyor (label scarcity = az miktarda
etiketli veri, nedeni ister az veri ister az etiketleme olsun) — ayrı ayrı
belirtmeye gerek yok.

**Byline:** isim/unvan büyütüldü ve aşağı kaydırıldı (`.cover .byline`
CSS'i — font-size ve margin-top artırıldı).

**Görsel notu:** Stok görsel kullanma. Kendi tespit çıktılarımızdan seçilmiş
net kareler — kullanılan 4'lü seçim (hepsi `docs/presentation/media/`
altında): `slide06_yolo_success_berghouse.jpg` (YOLO, 2 runner, temiz —
gölge tespit edilmemiş), `slide05_dji0790_ground_truth.jpg` (kızak takımı,
farklı video/ortam için), `slide14_statue_dji0501.jpg` (ilginç/tartışmalı
bir kare, merak uyandırır), `slide11_13_sam3_three_outcomes_dji0596.jpg`
(SAM3, gemi güvertesi).

**Değişiklik notu (2026-09-16):** Önceki seçimde `slide13_sam3_success_berghouse.jpg`
de vardı (Slayt 15'te hâlâ kullanılıyor) — kapaktan çıkarıldı çünkü hem
Slayt 7'nın görseliyle aynı videoydu (tekrar) hem de yakından bakınca
ikinci koşucunun yanında küçük bir gölge yanlış-pozitifi görünüyor (tam
Slayt 6'in anlattığı hata). Yerine DJI_0790 görseli kondu.

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

**Görsel:** Solda drone frame
(`docs/presentation/media/slide02_drone_frame_raw.jpg`), sağda Blok B'nin
iki senaryosunu somutlaştıran gerçek örnekler, alt alta:
1) `docs/presentation/media/slide02_perimeter_intrusion.jpg` — termal
kamera, çitten atlayan bir kişiyi kutulamış ve yolunu (kırmızı çizgi)
takip etmiş; "surveillance networks" senaryosu.
2) `docs/presentation/media/slide02_factory_bottle_inspection.webp` —
şişeleme hattında kalite kontrol, kusurlu şişe kırmızı kutuyla
işaretlenmiş; "production line / quality inspection" senaryosu.
İkisi de kullanıcının bulup verdiği gerçek örnek görseller (2026-09-16),
eski soyut "camera network" şeması yerine kondu.

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

## Slayt 3 — Target Selection

**Tek mesaj:** Hedefi körlemesine seçmedik — açık kriterlere karşı test
ettik, alternatifleri elemeyle kaydettik, ve `person` her kriterde kazandı.

**Kapsam notu (2026-09-16 revizyonu):** Bu slayt artık **sadece hedef
seçimi**. Split'in kendisi (hangi video hangi sette, neden video
seviyesinde) slayt 4'e taşındı — eskiden burada "direkt 6/4/1 sayılarını
veriyoruz sonra slayt 4'te neden video seviyesinde ayırdığımızı
anlatıyoruz" gibi tuhaf bir sıralama vardı. Şimdi akış doğru: önce hedefi
seçtik (burada), sonra veriyi nasıl ayırdığımızı anlattık (slayt 4), sonra
test setinin neden elle etiketlendiğini anlattık (slayt 5).

*Blok A: Systematic dataset inventory*
- 13 videos analysed one by one — at least 1 frame per video, plus 4-5
  extra sampled frames from six of them in the first pass
- Recorded per video: resolution, duration, **objects present**, object
  size, background type, occlusion
- Full table lives in the repo (`results/dataset_overview/table.csv`) —
  summary only here, koca tablo koyma

*Blok B: Selection criteria, checked against every candidate*
- Needed: present in **≥2-3 different videos**, real **scale variation**
  (altitude changes), **~500+ instances**, genuine occlusion/hard-negative
  material — not just "picked the obvious one"
- `person`: present in **11 of 13** videos (a full manual re-watch
  corrected an initial 6/13 sparse-frame estimate — small/distant figures
  don't reliably land in a sparse sample), strong altitude-driven scale
  variation, easily 500+ instances, rich occlusion material (vegetation,
  footbridge crossings, shadow/rock blending, small figures blending with
  sled dogs in snow)

*Blok C: Alternatives considered and rejected*

| Candidate | Videos | Verdict |
|---|---|---|
| boat / sailboat | 2 | mostly static, weak scale variation — poor fit |
| vehicle (pickup) | 1 | single fleeting frame |
| dog (sled team) | 1 | high per-video count, but fails the "2-3 videos" rule |
| static objects (statue, lagoon) | 1 each | no scale variation, no repeated instances |
| **person** | **11** | wins on every criterion |

*Blok D: Why staying inside COCO's own vocabulary matters*
- `person` is already a COCO class — keeps the baseline method's
  **domain-gap measurement meaningful** (Slide 7)
- We're testing whether unusual angle, small scale, and low resolution
  defeat a class the model already knows — not testing an unfamiliar class
- Bonus: the footage itself spans multiple countries/terrains (Scotland,
  likely Iceland, Switzerland, and more) — that geographic spread is
  actually an asset for `person`'s appearance diversity, not a complication

**Kaynak:** `docs/00_target_selection.md`, `results/dataset_overview/table.csv`,
`results/inventory/video_inventory.csv`

**Görsel:** Hedefin göründüğü, **henüz bbox atılmamış** ham frame'lerden
3 kare — `docs/presentation/media/slide03_raw_dji0862.jpg` (Iceland,
volcanic black-sand terrain, kadrajda ayrıca ikinci bir drone var),
`slide03_raw_surenen.jpg` (2 power-walker, dağ patikası),
`slide03_raw_dji0790.jpg` (kızak köpek takımı + musher, kar).
Ham kare göstermek bilinçli: "önce baktık, sonra karar verdik" anlatısını destekler.

**Konuşma akışı**
> Before choosing anything, I went through all thirteen videos systematically and built
> an inventory: what objects appear, what the background looks like, the viewpoint, the
> duration. Then I checked every candidate class against four criteria: does it appear in
> several videos, does it show real scale variation, are there enough instances, is there
> genuine occlusion material to learn from. A boat, a vehicle, a sled dog, a statue — each
> failed at least one of those. Person passed all four: eleven of thirteen videos, strong
> scale variation from altitude, easily five hundred-plus instances, and rich occlusion
> material. It also happens to already be a COCO class, which matters later — it means
> the very first baseline measures a genuine domain gap, not just an unfamiliar class.

---

## Slayt 4 — Data Preparation: Splitting Strategy

**Tek mesaj:** Split **video seviyesinde** yapıldı, frame seviyesinde değil — ve her
split kasıtlı olarak farklı domain'lerden geliyor, sonraki her mAP sayısını
anlamlı kılan da bu.

*Blok A: Split at video level — not frame level*
- Frames within one video are near-duplicates and share a single domain
- A frame-level split would leak the test domain into training → inflated scores
- **Each split draws from separate videos**
- Train / Val / Test: **6 / 1 / 4 videos** (of the 11 person-containing
  videos — roughly 55% / 9% / 36%), plus **2** person-free videos held out
  separately as hard-negative background sources (`data/splits/*.txt`)

*Blok B: Why each split was sized the way it was*
- **Test:** enough videos to evaluate methods across a genuinely general context —
  not a single scene
- **Train:** enough videos to avoid training on one narrow domain
- **Val:** threshold tuning and model selection only; never used for final numbers

*Blok C: Deliberate domain diversity — the part that makes it work*
- **Test** spans 4 genuinely different domains: grass trail (Berghouse),
  hilltop monument (DJI_0501), open water/ship deck (DJI_0596), volcanic
  terrain (DJI_0862)
- **Train** spans 6 more, non-overlapping domains: snow ridge, vineyard/lake
  shoreline, snow field/village, glacial lagoon, rocky summit, grass trail
- **Val** is one single, representative "easy" video (grass ridge trail) —
  its only job is checkpoint selection, not testing generalisation
- Not a coincidence: every split draws from **genuinely different
  conditions**, not near-duplicate footage of the same scene

*Blok D: Key numbers*
- Total videos / total duration: **13 videos, 7 min 52 s** combined
- Videos containing the target: **11 / 13**
- Split composition: **4 test, 6 train, 1 val, 2 background** (person-free,
  kept as hard-negative source — Creux du Van, Isles of Glencoe)

**Kaynak:** `data/splits/*.txt`, `results/dataset_overview/table.csv`

**Görsel:** Video-level split şeması
(`docs/presentation/media/slide04_split_scheme.png` — 13 video → 4 kutu:
train/val/test/background).

**Konuşma akışı**
> One decision here is more important than it looks. I did not split frames — I split
> videos. Frames inside a single video are almost identical and share one domain; a
> frame-level split would leak the test domain straight into training and inflate every
> number I show you today. Each split comes from separate videos.
> Test had to cover enough videos to evaluate the methods in a genuinely general
> context. Train had to cover enough videos not to overfit to one domain. And this
> wasn't just about counts — test spans four genuinely different domains, train spans
> six more, and none of them overlap. That's what makes every mAP number later in this
> talk actually mean something.

---

## Slayt 5 — The Test Set: Why It's Labelled by Hand

**Tek mesaj:** Test setimiz en kıymetli varlığımız — bu konuşmadaki her sayı ona
bağlı, o yüzden tamamen elle, CVAT ile etiketlendi.

*Blok A: The test set is manually labelled*
- Test labels drawn **by hand in CVAT** — no model output enters ground truth
- The human labelling budget was spent on **measurement, not training**
- Rationale: without a trustworthy test set, no other number in this talk means anything

*Blok B: Honest limitation*
- With only 4 held-out videos, the test set is limited
- Generalisation claims are bounded accordingly — reported later with the results

**Kaynak:** `data/gold_test/annotations.json`, `docs/decision_log.md`
("Gold test set complete", 2026-09-12)

**Görsel:** CVAT arayüzünden ekran görüntüsü
(`docs/presentation/media/slide04_cvat_annotation_ui.png` — glacial lagoon
sahnesinde küçük, uzak kişilerin elle kutulandığı an).

**Konuşma akışı**
> And the test set is labelled entirely by hand, in CVAT. No model output ever enters
> the ground truth. That was a deliberate choice about where to spend my human labelling
> budget: on measurement, not on training. Without a test set I can trust, none of the
> numbers that follow would mean anything.
> Honestly: with only four held-out videos, this test set is small. My generalisation
> claims are bounded accordingly, and I'll say so again when the results come in.

---

## Slayt 6 — Automatic Labelling with SAM 3

**Tek mesaj:** Test elle etiketlendi ama train için elle etiketleme gerçekçi değildi;
otomatik etiketleme hattı kurduk ve **kalitesini ölçtük**.

*Blok A: Why automatic labelling*
- Manual labelling does not scale to the training set
- Need: boxes at volume, with acceptable noise

*Blok B: SAM 3 pipeline*
- Prompt-driven segmentation → masks → bounding boxes
- Applied across training videos
- `imgsz=1024` — not Ultralytics' 640 default (source is mostly 4K, would
  erase small people) and not 1920 either — SAM3's ViT backbone has
  quadratic-cost self-attention, and 1920 OOM'd on a T4 (wanting 10.81GB
  on a 14.56GB GPU); 1024 is the safe middle ground
- `confidence_threshold=0.5` (see the shadow fix in Block D below)
- Dedup threshold 8.0, max frame gap 2.0s between kept detections

*Blok C: Validating the labeller against ground truth*
- SAM 3 was run **on the manually labelled test videos as well**
- Its output compared directly against our own CVAT annotations
- Only after the agreement was satisfying did we trust it to label the training set
- Agreement / accuracy vs. manual labels: **mAP@.5 = 0.846** against the
  gold test set — see Slide 13 for the full benchmark (same model, same
  protocol; this is what "agreement" means measured, not eyeballed)
- Inference time per frame: not logged separately during the labelling run
  itself — the closest measured number comes from the later zero-shot
  benchmark under comparable settings: **2.72 s/frame mean** on T4 (Slide 13)
- **Total labels produced (train + val, after quality filtering and the
  manual corrections below): 471 frames, 1,411 boxes**

*Blok C.1: Final counts, per video*

| Video | Frames | Boxes |
|---|---|---|
| DJI_0790 | 86 | 596 (post dog-correction, see Block D) |
| DJI_0876 | 59 | 243 (post under-labelling **and** tracker-drift correction — see note below) |
| Surenen Pass Trail Running | 92 | 188 |
| Stockflue Flyaround | 69 | 127 |
| DJI_0574 | 43 | 108 |
| VerticalFlyOver (val) | 54 | 107 |
| Bluemlisalphutte Flyover | 68 | 42 |
| **Total** | **471** | **1,411** |

> **DJI_0876 tracker-drift correction (2026-09-15):** a second CVAT pass
> found that interpolated tracker boxes had kept propagating a person box
> across frames after the person had actually left the shot — a flat,
> unchanging ~14-box cluster repeated identically from frame 760 through
> frame 1220 (roughly the back half of the labelled range), instead of
> dropping to zero. Corrected export: 243 boxes, down from 685. A second,
> independent example of the same underlying lesson as the shadow fix
> above — an automated/semi-automated labelling step needs a human to
> actually watch it run to the end, not just check the first few frames.

> **Anlatım notu:** Bu, slaytın en güçlü argümanı. Otomatik etiketleyiciye körü körüne
> güvenmedik — elimizdeki tek güvenilir referansa karşı ölçtük, sonra kullandık.

*Blok D: Failure case and the fix (bunu mutlaka anlat)*
- **Shadows were being detected as persons** — a smoke-test frame (Berghouse
  Leopard Jog) showed a 0.47-confidence box next to, not on, a runner:
  the runner's shadow, not a duplicate detection
- Diagnosis: low confidence threshold (0.3) accepting shadow regions
- Fix: threshold raised **0.3 → 0.5** (via 0.4 as an intermediate step) —
  deliberately high enough to exclude the observed 0.47 shadow box outright
- Trade-off, accepted explicitly: higher precision, but genuine hard/small
  instances scoring similarly low (Bluemlisalphutte, DJI_0596) are at risk
  of being excluded too — the manual review of the full train+val labelling
  run (Block C.1 counts) was the actual backstop against that risk, not a
  fully automated safeguard

**Görsel:** İki görsel, sağ kolonda alt alta —
1) Before/after karşılaştırması: `docs/presentation/media/slide05_shadow_before_after.png`
(2026-09-15, Colab'da tek frame yeniden koşularak üretildi: aynı Berghouse
frame 0, solda conf=0.3 — 2 runner + gölge kutusu 0.47, sağda conf=0.5 —
sadece 2 runner, gölge dışlanmış).
2) Farklı bir videodan çeşitlilik: `docs/presentation/media/slide05_dji0790_ground_truth.jpg`
(2026-09-16, Drive'daki `trainval_frames.zip`'ten gerçek `DJI_0790/frame_000000.jpg`
karesi indirilip final ground-truth kutuları [`results/pseudo_labels/annotations/DJI_0790.json`]
üzerine yerelde çizildi) — kızak takımının 6-8 köpeği kutusuz, sadece
musher + yolcu `person` olarak kutulu; Slayt 9'daki köpek-düzeltme
hikâyesinin görsel kanıtı. Not: bu kare şüphesi net bir "gölge" örneği
değil, asıl amacı görsel çeşitlilik ve etiket kalitesi kanıtı.

**Kaynak:** `results/pseudo_labels/annotations/*.json` (final frame/box
counts), `results/eval/sam3_zeroshot_T4/metrics.json` (agreement vs. manual
labels), `results/manifests/34_sam3_zeroshot_eval_20260913T202102Z.json`
(2.72 s/frame timing), `configs/04_label_video.yaml` (run parameters),
`docs/decision_log.md` ("Bug found — smoke test wasn't previewing the real
threshold" entry chain, 2026-09-12, for the shadow-box story and the
0.3→0.4→0.5 threshold decision)

**Konuşma akışı**
> The test set is hand-labelled, but that does not scale to training. So I built an
> automatic labelling pipeline using SAM 3 — prompt-driven segmentation, converted to
> bounding boxes.
> But before trusting it on the training set, I ran it on the manually labelled videos
> too and compared its output against my own annotations. Only once that agreement was
> satisfying did I let it label anything I would train on — measured later at point
> eight four six mAP against the human labels, which you'll see again in a few slides.
> One honest number while I'm here: this model is slow — about two point seven seconds
> per frame on a T4, well under half a frame per second. Fine for a one-time labelling
> pass, not fine for anything real-time, which matters again later.
> Once I trusted it, it produced four hundred seventy-one labelled frames and just
> over fourteen hundred boxes across the training and validation videos.
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

## Slayt 7 — Baseline Approach: YOLO26n, Zero Fine-Tuning

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
- mAP on large objects (COCO def., area **>96×96px**) **0.676** — mAP on
  small objects (area **<32×32px**) **0.018**

*Blok C: Measured inference time*
- **T4:** 196 frames in 26.7 s → **7.3 FPS** (0.136 s/frame)
- **CPU (M1):** 196 frames in 62.2 s → **3.2 FPS** (0.317 s/frame)
- Caveat, stated honestly: this is measured **pipeline** throughput — frame
  read + inference + drawing/writing the annotated review image — not
  isolated model-only inference. A pure-inference number would be somewhat
  faster; not yet separated out (see Slide 20)

*Blok D: The one number that defines the rest of this talk*
- On DJI_0501 and DJI_0596 (the two hardest test videos): YOLO catches
  **0 of 44** small/distant people at its **default confidence (0.25)**
- **Correction (2026-09-16):** checked directly against
  `results/yolo26_lowconf/predictions.json` (conf≥0.01) — **26 of 44**
  actually do get a matching low-confidence candidate box (IoU≥0.5,
  scores 0.01–0.19), just not confident enough to survive the default
  cutoff. So this is **not** purely a feature-map resolution limit as
  earlier phrasing claimed ("at any confidence threshold") — it's mostly a
  confidence-threshold problem at the default operating point, which is
  exactly why Method 2's lower threshold + verifier (Slide 8) is able to
  recover 10 of these 44 (Slide 11)

**Görsel:** two side-by-side prediction-vs-ground-truth frames (red = ground
truth, green = prediction, per the project's own visualization convention):
- **Success** — `results/eval/yolo26n_zeroshot/comparison/Berghouse_Leopard_Jog__frame_000000.jpg`
  (deck copy: `docs/presentation/media/slide06_yolo_success_berghouse.jpg`):
  both runners boxed tightly, high confidence (0.78, 0.74)
- **Failure** — `results/eval/yolo26n_zeroshot/comparison/DJI_0596__frame_000000.jpg`
  (deck copy: `docs/presentation/media/slide06_yolo_failure_dji0596.jpg`):
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
> detector finds zero of forty-four small, distant people, at its default
> confidence. But I checked lower thresholds too — twenty-six of those
> forty-four actually do get a candidate box, just too low-confidence to
> survive the default cutoff. Here's what that looks like: two runners
> caught cleanly on the left, and on the right, real people on a boat deck
> with not a single prediction anywhere near them at conf 0.25. That's not
> a dead end — it's exactly the opening the next method uses. Everything I
> show you next responds to this one number.

---

## Slayt 8 — Method 2 (Cascade), Part 1: Architecture & Confidence Selection

**Tek mesaj:** Method 1's blind spot motivates a two-stage system — but
lowering YOLO's confidence floor alone trades recall for a flood of false
candidates, which is exactly why a second, independent model has to sit
downstream of it.

**Kapsam notu:** Method 2 hâlâ aynı paradigma içinde bir iyileştirme (YOLO
tabanlı, supervised detection) — PDF'in *"alternatif yaklaşım"* maddesini bu
slayt DEĞİL, slayt 13 (SAM3) karşılar. Bunu konuşurken netçe söyle.

*Blok A: The gap this method targets*
- Recap in one line: Method 1 (YOLO26n) alone, at its **default confidence**
  (Slide 7), finds **0 of 44** small/distant people on the two hardest test
  videos
- Idea: force YOLO to propose more boxes by lowering its confidence floor,
  then use a second, independent model to separate real detections from the
  resulting noise

*Blok B: System architecture*
- **Stage 1:** the same YOLO26n checkpoint, confidence floor lowered
  0.25 → 0.01
- **Stage 2:** a ResNet18 binary classifier, working on a 64×64 **crop** of
  one candidate box — "is this a person?" — not the whole frame (training
  recipe on the next slide)
- The two models see the problem at different scales: YOLO reasons over the
  full frame, the verifier only ever sees one cropped candidate at a time

*Blok C: Choosing the confidence floor — a precision/recall tradeoff, measured not guessed*
- Swept YOLO26n's own confidence threshold on the validation split, checking
  candidate boxes against SAM3 pseudo-labels (IoU ≥ 0.5, 107 person boxes):

  | Confidence | Candidates (val) | Candidates / frame | Recall |
  |---|---|---|---|
  | **0.01** | 329 | 6.09 | **80.4%** |
  | 0.05 | 109 | 2.02 | 62.6% |
  | 0.10 | 69 | 1.28 | 47.7% |
  | 0.15 | 52 | 0.96 | 41.1% |
  | 0.20 | 40 | 0.74 | 35.5% |
  | 0.25 (YOLO default) | 30 | 0.56 | 27.1% |
  | 0.30 | 28 | 0.52 | 25.2% |

- Dropping the floor to 0.01 lifts the reachable recall **ceiling** from
  27.1% to 80.4% — a near-3× gain — but candidate volume grows more than
  10× (0.56 → 6.09 boxes/frame). Ground-truth object density per frame
  doesn't grow 10×, so most of that extra volume has to be noise: **this is
  the precision half of the tradeoff, and it's the reason Stage 1 alone
  can't just be run at 0.01 and trusted**
- 0.01 was picked because it sits at the recall ceiling with headroom to
  spare — **agreed fallback to 0.05** if the downstream cascade
  underperformed (it didn't — see Slide 11)
- This table is exactly why the system has two stages: Stage 1 is tuned
  purely for recall (accept the noise), Stage 2's only job is to claw the
  precision back by looking at each candidate individually

**Görsel:** system diagram
(`docs/presentation/media/slide07_cascade_system_diagram.png` — frame →
YOLO low-conf boxes → crop → ResNet18 → score fusion).

**Kaynak:** `docs/decision_log.md` (confidence-floor sweep decision,
2026-09-13), `results/eval/val_threshold_sweep.md`, `configs/10_train_verifier.yaml`

**Konuşma akışı**
> Method 1 exposed one very specific gap: zero small or distant people
> caught, at any threshold. My response was a two-stage system. Stage one is
> the same YOLO, but with its confidence floor dropped way down, so it
> proposes far more candidate boxes — including the small ones it was
> silently throwing away. Stage two is a small ResNet, looking at just the
> cropped candidate and deciding whether it's really a person.
> I didn't pick 0.01 arbitrarily — I swept the threshold on validation data
> and measured recall against the pseudo-labels at each point. Recall
> triples going from the default 0.25 down to 0.01, twenty-seven percent up
> to eighty percent. But the number of candidate boxes per frame goes up
> more than ten times over the same range, and the actual number of people
> in a frame obviously isn't growing ten times — so almost all of that extra
> volume is noise. That's the precision side of the tradeoff, and it's
> exactly why I couldn't just lower the threshold and call it done: I needed
> a second model whose only job is separating the real detections out of
> that flood. 0.01 sits right at the recall ceiling, with 0.05 as an agreed
> fallback if the second stage didn't pull its weight — it did.

---

## Slayt 9 — Method 2 (Cascade), Part 2: Training the Verifier

**Tek mesaj:** How the second stage's training data and training recipe
were built — including the most interesting failure this project surfaced.

*Blok A: How the training data was built — and a real failure it uncovered*
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
- Final crop counts: **train 4,905 (1,398 person / 3,507 not_person) — val
  221 (181 person / 40 not_person)**, built with `torchvision.datasets.ImageFolder`

*Blok B: Training recipe (slide bullets — keep it to this on screen)*
- ResNet18, ImageNet-pretrained — plain **PyTorch + torchvision**
- Input 64×64 crops (40% context padding) · **Adam optimizer**
- **15 epochs**, batch 64
- Augmentation — flip + colour jitter

*Full detail, for verbal answers / Q&A only — do not put back on the slide*
- Technically **AdamW**, lr 3e-4, weight decay 1e-4, constant LR (no
  scheduler) — "Adam" on the slide is the casual/interview-safe short
  form; if pressed, the decoupled weight decay is the actual detail
- Loss: cross-entropy with inverse-class-frequency weighting — handles
  the 3,507:1,398 not_person/person imbalance directly in the loss rather
  than by resampling
- No Lightning/timm — deliberately kept out to avoid a new dependency
- Augmentation is deliberately light because these crops are already tiny
  and blurry — aggressive augmentation would mostly add noise; ImageNet
  normalisation at both train and eval
- Trained on **CPU**, not GPU — a deliberate project convention (kept local
  work off the GPU) given how small this model and dataset are; exact
  wall-clock time wasn't logged, so don't quote one live

*Blok C: The verifier's own numbers*
- Checkpoint selection: **best validation person-F1**, not accuracy — val
  is ~82% person (181/221), so accuracy alone would hide a classifier that
  just predicts "person" most of the time
- Best checkpoint (epoch 7 of 15): **val loss 0.0623, val accuracy 98.2%,
  person precision/recall/F1 all 98.9%**

**Görsel:** dog-vs-person crop pair
(`docs/presentation/media/slide07_18_dog_vs_person.png` — from the DJI_0790
correction, produced 2026-09-15 from
`data/crops/train/{not_person,person}/DJI_0790__*`).

**Kaynak:** `docs/decision_log.md` ("Teacher failure found in audit: SAM3
labels sled dogs as people", 2026-09-13), `configs/10_train_verifier.yaml`,
`configs/09_build_crop_dataset.yaml`, `src/methods/yolo/verifier.py`
(`build_transforms`), `scripts/10_train_verifier.py`,
`results/cascade_verifier/training_history.json`,
`data/crops/{train,val}/{person,not_person}`

**Konuşma akışı**
> Building the training data for the second stage is where I found the most
> interesting problem in this whole project. Auditing SAM3's own
> pseudo-labels on the snow and sled-dog video, I found it had been boxing
> the sled dogs as people — from directly overhead, on white snow, a dog and
> a person in a coat genuinely look alike. I corrected two hundred
> seventy-one of those boxes by hand and explicitly fed them back into the
> verifier's training set as "not a person" — so the second stage is
> literally trained on the exact mistake the first model made.
> On the recipe: ResNet18 pretrained on ImageNet, plain PyTorch, AdamW at a
> constant learning rate, fifteen epochs over about five thousand crops,
> batch size sixty-four. The classes are imbalanced — about two and a half
> times more negative crops than positive — so I weight the loss by inverse
> class frequency instead of resampling. Augmentation is deliberately light,
> just a flip and a little colour jitter, because these crops are already
> small and blurry and I didn't want to manufacture noise on top of that.
> It trained on CPU — small model, small dataset, no need for a GPU there.
> The best checkpoint, picked by validation F1 on the person class, hit
> ninety-eight point nine percent precision and recall.

---

## Slayt 10 — Method 2 (Cascade), Part 3: The Iteration

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
- **This is the first configuration all cycle to beat Method 1 on mAP@.5
  by the widest margin yet** (0.786 vs 0.693) — mAP is the right metric to
  lean on here, not a single-threshold F1: a fused two-model score and
  YOLO's raw objectness score aren't on the same scale (Slide 14), so a
  "beats it at conf=X" F1 claim would need its own threshold search per
  method, and (checked, see `docs/decision_log.md`, "GPU (T4) validation
  of the full method comparison", 2026-09-13) doing that search on the
  gold test set for *both* methods actually lands Method 1 slightly
  **ahead** (F1 0.7892 @ its own swept conf=0.30) — an honest reminder
  that a threshold chosen because it maximises test-set F1 is not a
  trustworthy comparison point for either method. mAP avoids that problem
  entirely, which is exactly why it stays the headline number throughout
  this talk

**Görsel:** journey timeline
(`docs/presentation/media/slide08_journey_timeline.png` — 4 adım,
kırmızı=loss/yeşil=win) + ResNet stem before/after diyagramı
(`docs/presentation/media/slide08_resnet_stem.png` — 64×64 → 16×16 vs.
64×64 unchanged).

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
> for small inputs instead of full-size photos. This is the biggest mAP
> jump of the whole cycle — point-seven-eight-six against Method 1's
> point-six-nine-three. I'm deliberately not quoting a single-threshold F1
> win here: I checked, and if you let both methods search for their own
> best threshold on the test set, Method 1 actually edges back ahead
> slightly. That's not a real result either way — it's what happens when
> you pick a threshold because it flatters the test set — which is exactly
> why mAP, not a cherry-picked operating point, is the number I'm standing
> behind.

---

## Slayt 11 — Method 2 (Cascade), Part 4: Final Result

**Tek mesaj:** A real, measured win over Method 1 — plus an experiment with
an alternative verifier backbone that quietly reinforces the project's
biggest lesson about validation scores.

*Blok A: Verifier backbone comparison (T4, shared conf=0.25)* — the three
fusion variants below share the same YOLO stage and the same fusion
formula, so their scores really are on one scale; comparing them at one
fixed point is legitimate here in a way it wouldn't be for Method 1 vs.
Cascade (Slide 10 already made that case on mAP, not F1, for exactly that
reason).

| Config | mAP@.5 | Precision | Recall | F1 | FP |
|---|---|---|---|---|---|
| Method 1 (YOLO26n, conf 0.25) | 0.693 | 0.853 | 0.726 | 0.784 | 90 |
| **Cascade — small-stem ResNet + fusion** | **0.786** | 0.754 | 0.778 | 0.766 | 182 |
| Cascade — EfficientNet-B0 verifier | 0.777 | 0.729 | 0.765 | 0.747 | 204 |

At this **shared** point the gap between verifier backbones is actually
clearer (0.766 vs 0.747, a 0.019 F1 gap) than at each backbone's own
optimized threshold (0.006 gap) — exactly why this table intentionally
does *not* hunt for each row's best threshold the way Slide 10 does for
the single cascade-vs-Method-1 claim.

*Blok B: Where it actually earns its keep*
- On DJI_0501 / DJI_0596 (the two hardest videos): small-object mAP goes
  from **0.000 on both** (Method 1) to **0.081 / 0.070** — a real, targeted
  recovery of exactly the failure Method 1 exposed, not just a headline
  number
- Not the aggregate F1 winner by a huge margin — but the *only* method in
  this comparison that recovers any of that specific capability

*Blok C: Also tried — EfficientNet-B0 backbone*
- Tried as an alternative verifier architecture; **not adopted** — its
  actual test-set result was weaker (mAP@.5 0.777 vs. 0.786), despite
  scoring better on validation

**Görsel:** the comparison table above, rendered as a small bar chart
(`docs/presentation/media/slide09_cascade_bar_chart.png`).

**Kaynak:** `results/eval/comparison.csv`, `docs/decision_log.md`
("EfficientNet-B0 verifier: best val score, not best test score",
2026-09-13)

**Konuşma akışı**
> Final result: mAP up from point-six-nine-three to point-seven-eight-six,
> and — this is the part I actually care about — on the two hardest videos,
> small-object detection goes from exactly zero to something real. Ten of
> forty-four previously invisible people, caught.
> I also tried EfficientNet-B0 as a different verifier architecture — didn't
> keep it, the actual test result was weaker despite a better validation
> score. Stuck with ResNet.

---

## Slayt 12 — Method 3: RT-DETR, a Different Architecture Family

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

*Blok D: A concrete, measured example of RT-DETR's resistance — the
DJI_0501 statue*
- Slide 16 documents a human statue (Scottish hilltop monument) that both
  YOLO26n (8 of 10 sampled frames, conf 0.81–0.89) and SAM3 (7 of 10
  frames, conf 0.58–0.71) confidently box as `person` — ground truth
  correctly excludes it
- **Both RT-DETR checkpoints resist this specific trap:** RT-DETRv2-R18
  fires on it in only 1 of 10 frames, and even then below the 0.25
  operating threshold used everywhere else in this project (effectively a
  non-detection); RT-DETR-l fires in 2 of 10 frames
- This is the one point in this project where "RT-DETR generalises
  differently" is a **directly measured** result, not just a plausible
  story — pulled from each checkpoint's own prediction file across all 10
  sampled frames, not eyeballed from one image

*Blok E: Closing take — when would this method actually win?*

> **Framing note:** Blok D's statue result above is measured. The
> sled-team/dog-vs-person extension below is still a reasoned hypothesis,
> not a measured result — say so explicitly when presenting it, don't let
> it sound like a benchmarked claim.

- RT-DETR's encoder uses **self-attention**: every region of the frame is
  related to every other region. Its decoder uses **cross-attention**: each
  object query reasons over the *whole* image, not one local patch. That's a
  genuinely different inductive bias from YOLO's convolutional, local
  receptive field
- That matters most when an object's identity depends on its relationship to
  the rest of the scene, not just its own local appearance — for instance,
  the dog-vs-person confusion from Slide 9: a person is typically positioned
  and postured differently *relative to the rest of a sled team*, a cue a
  global-context model is architecturally better positioned to use than a
  purely local one. **Not tested in this project — a plausible direction,
  not a claim**
- The catch: transformers are known to be more data-hungry — they have to
  *learn* useful attention patterns from data, rather than getting locality
  "for free" as a CNN's built-in bias. This is exactly why fine-tuning
  RT-DETR was judged too risky to attempt this cycle on our modest
  pseudo-label set (Slide 20)
- **Expectation, not yet measured:** with a larger, stronger training set,
  RT-DETR would plausibly pull further ahead of YOLO on exactly these
  context-dependent, ambiguous cases — likely at the cost of **even lower
  FPS**, since attention cost scales with the number of tokens the model
  processes. The same quadratic-cost lesson this project already learned
  directly, the hard way, with SAM3's own ViT backbone (Slide 6)

**Görsel:** side-by-side — native-resolution RT-DETR prediction vs. the
forced-1920 duplicate-box storm, aynı frame (Berghouse, frame 720)
(`docs/presentation/media/slide10_rtdetr_resolution_comparison.png`,
2026-09-15). Görsel dosya hiç kaydedilmemiş olsa da kutu koordinatları
`results/rtdetr_zeroshot/predictions.json` (native) ve
`results/rtdetr_resolution_diagnostic/predictions.json` (forced-1920)
içinde zaten duruyordu — GPU'ya gerek kalmadan `src/eval/visualize.py`'nin
`draw_comparison`'ı ile yerelde render edildi: solda 3 temiz kutu, sağda
aynı 2 kişi üzerinde 8 çakışan kutu.

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
> One more finding, and this one I did measure directly: there's a human
> statue in one of our test videos. Both YOLO and SAM3 confidently box it
> as a person in most sampled frames — it's human-shaped, after all.
> Both RT-DETR checkpoints almost never do. That's a real, checked-against-
> the-prediction-files difference, not a guess.
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

## Slayt 13 — Method 4 / The Alternative Approach: SAM 3, Zero-Shot Foundation Model

<span style="color:#A4A9AD">SAM 3 — Segment Anything with Concepts, Meta AI, 2025</span>

**Tek mesaj:** Every method so far is a trained or fine-tunable supervised
detector. This one is not — it is prompted with the word "person" and never
sees this project's data. **This is the assignment's required "genuinely
different alternative approach."**

*Blok A: What makes this genuinely different*
- The same SAM3 model already introduced as the labelling tool (Slide 6) —
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
  from Slide 6

**Görsel:** the DJI_0596 frame showing all three outcomes at once (correct /
missed / false-positive) — the clearest single qualitative example in the
project (also used in Slide 15). Confirmed and saved 2026-09-15:
`docs/presentation/media/slide11_13_sam3_three_outcomes_dji0596.jpg` —
correct cluster on the rear deck, missed pair near the wheelhouse, 2-3
false-positive boxes over open water at the top-right.

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

## Slayt 14 — Quantitative Comparison

**Tek mesaj:** One test set, one protocol, four paradigms — ranked by mAP,
not by a fixed confidence threshold, because these methods are not on the
same confidence scale.

*Blok A: Headline table (gold test set, 196 frames / 719 boxes)*

| Method | Hardware | mAP@.5 | mAP@[.5:.95] | Precision | Recall | F1 | FPS |
|---|---|---|---|---|---|---|---|
| YOLO26n (baseline) | T4 | 0.693 | 0.479 | 0.853 | 0.726 | 0.784 | not yet benchmarked |
| Cascade (best: small-stem fusion) | T4 | **0.786** | 0.526 | 0.754 | 0.777 | 0.766² | not yet benchmarked |
| RT-DETRv2-R18 | CPU¹ | 0.740 | 0.468 | 0.609 | 0.761 | 0.677 | not yet benchmarked |
| SAM3 (zero-shot) | T4 | **0.846** | **0.626** | 0.485 | **0.872** | 0.624 | **0.37** |

¹ RT-DETR's own script already runs on GPU automatically when available;
not yet re-run on T4 in this cycle — say this out loud, don't hide the
hardware mismatch.

² This row is at conf=0.25 for consistency with every other row in this
machine-generated table (`results/eval/comparison.csv`, nothing here
hand-typed) — but 0.25 is YOLO's convention, not the cascade's own fused
score's natural point. Deliberately **not** swapped for the cascade's own
best-F1 threshold (0.38): that number is picked by scanning thresholds
against this same gold test set and keeping the best one, which is a form
of test-set leakage — checked directly, doing the identical scan for
Method 1 lands it at F1 0.7892 @ its own swept conf=0.30, *higher* than
the cascade's 0.7885. Neither swept number is trustworthy enough to
report as a comparison; mAP (threshold-free by construction) is, which is
why it — not F1 — carries the "cascade is better" claim in this talk.

*Blok B: Why mAP, not a fixed threshold, is the headline number*
- Confidence isn't comparable across a CNN's objectness score, a fused
  two-model score, and a foundation model's prompt-similarity score
- mAP sweeps every method's own threshold internally, as part of its
  definition — not by trying values and keeping the best one, which is
  exactly the difference that makes it trustworthy where a swept F1 isn't
  (footnote 2)
- Precision / recall / F1 above are each read at **0.25** — each method's
  own natural default (YOLO's, SAM3's/RT-DETR's own convention) — never
  hunted for per method, never silently mixed at different scales

*Blok C: Evaluation methodology — why these tools and breakdowns*
- COCO-style protocol via `pycocotools` (`src/eval/metrics.py`) — the
  standard, reproducible tool, not a hand-rolled mAP implementation
- Report both **mAP@.5** (a lenient bar — did you find the person at all)
  and **mAP@[.5:.95]** (a stricter one — how tight is the box) — the gap
  between the two tells you whether a method's boxes are loose or precise,
  not just whether it fires
- **Size-based breakdown (small/medium/large) built in from the start** —
  this is what actually surfaces this project's central finding (Slide 7);
  a single pooled mAP number would have hidden it completely
- **Per-video breakdown** — needed to show performance across genuinely
  different conditions, not one averaged-away number (feeds directly into
  Slide 17's error analysis)
- mAP itself sweeps confidence internally and never produces a single
  precision/recall/F1 triple, so a separate, custom
  `precision_recall_f1()` function (greedy IoU matching at one stated
  operating point) was written specifically for that complementary view

**Görsel:** bar chart, mAP@.5 across the 4 methods, accent green on the
highest bar (`docs/presentation/media/slide12_map_bar_chart.png`).

**Kaynak:** `results/eval/comparison.csv` (every row in this table is a
direct read from that file — nothing here is hand-typed), `src/eval/metrics.py`,
`docs/decision_log.md` ("YOLO26n zero-shot baseline...", 2026-09-13;
footnote 2's swept F1 figures — cascade 0.7885 @ 0.38, Method 1 0.7892 @
0.30 — from "GPU (T4) validation of the full method comparison",
2026-09-13, a real Colab T4 run not itself saved as a separate `results/`
file, hence a footnote rather than a table edit)

**Konuşma akışı**
> Here is every method, side by side, on the exact same gold test set. I'm
> ranking by mAP rather than picking one confidence threshold and comparing
> precision or F1 directly, because these confidence scores are not on the
> same scale. YOLO's objectness score, the cascade's fused score, SAM 3's
> prompt-similarity score — none of them mean the same thing at "point two
> five." mAP sweeps each method's own threshold internally, so it's the one
> number here that's genuinely comparable.
> A word on the evaluation itself: this uses the standard COCO protocol via
> `pycocotools`, not a hand-rolled metric. I report both mAP@.5 and the
> stricter mAP@[.5:.95] — one asks "did you find it," the other "how tight
> is the box." And I broke everything down by object size and by video
> from day one, because a single pooled number would have completely
> hidden this project's central finding: the small-object gap you saw on
> Slide 7.
> The story: SAM 3 wins on ranking quality and recall, with zero training.
> Among the trained, deployable detectors, the cascade is best. RT-DETR sits
> in between — better ranking than the plain baseline, worse precision. No
> single method wins on every axis, and that's the actual finding here, not
> a flaw in the comparison.

---

## Slayt 15 — Qualitative Comparison

**Tek mesaj:** One frame can show a success, a miss, and a false positive at
the same time — numbers alone don't tell you that.

*Blok A: A clean success*
- DJI_0862 (volcanic terrain): five people, correctly boxed by SAM3 at
  0.70-0.86 confidence — DJI_0862 scores 0.906 mAP@.5, SAM3's second-best
  test video

*Blok B: DJI_0596 — all three outcomes in one frame*
- A lake steamer boat scene (not the snow/mountain scene its "tiny
  instances" description first suggested)
- **Correct:** cluster of people on the rear deck, boxed accurately
- **Missed:** two people on the raised bridge/wheelhouse — no box anywhere
  near their ground-truth position
- **False positive:** 2-3 "person" boxes over open water where nothing is
  present — plausibly wave/glare misread as a distant person

**Görsel:** side-by-side, her ikisi de `aspect-ratio:16/9` + `object-fit:contain`
ile (2026-09-16 düzeltmesi — önceden `flex:1` ile zorlanan varsayılan 4:3
kutu, gerçek 16:9 görselleri kırpıyordu) — DJI_0862 success frame
(`docs/presentation/media/slide13_sam3_success_dji0862.jpg`, 2026-09-16,
`results/eval/sam3_zeroshot_T4/comparison/DJI_0862__frame_000000.jpg`'den
insan kümesine kırpıldı, gökteki 0.27-güvenli drone/uçak kutusu kadraj
dışı bırakıldı) ve DJI_0596 frame with all three outcomes
(`docs/presentation/media/slide11_13_sam3_three_outcomes_dji0596.jpg`,
shared with Slide 13).

**Değişiklik notu (2026-09-16):** Önceki Berghouse görseli hem Slayt 1/6
ile aynı videoydu (tekrar) hem de yakından bakınca gölge yanlış-pozitifi
içeriyordu (Slayt 6'in hikâyesi) — DJI_0862 ile değiştirildi, gerçek test
setinden, gerçek SAM3 sonucuyla (0.906 mAP@.5, `docs/decision_log.md`
"Tier 1 item 3: SAM3 zero-shot benchmark result").

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

## Slayt 16 — Ambiguous Results: Is It Even a Person?

**Tek mesaj:** Some of the hardest cases here aren't detection failures at
all — they're genuine "is this the target class or not" questions, and
different architectures answer them differently. This directly answers the
assignment's "belirsiz sonuçlar" requirement: not every wrong-looking box
is a bug, some are a real disagreement about what "person" even means for
this specific object.

*Blok A: The statue that fools two of four methods, not four (DJI_0501)*
- A stone monument on a grassy Scottish hilltop — human-shaped, human-
  posed, standing on a plinth — but not alive
- Manual ground truth (CVAT): deliberately **not** labelled as `person` —
  a real annotator judgment call, not an oversight
- Measured directly from each method's own prediction file, across all 10
  sampled DJI_0501 frames — not eyeballed from one image:

| Method | Boxes the statue as `person` | Confidence range |
|---|---|---|
| YOLO26n | 8 of 10 frames | 0.81 – 0.89 |
| SAM3 (zero-shot) | 7 of 10 frames | 0.58 – 0.71 |
| RT-DETR-l (Ultralytics) | 2 of 10 frames | 0.27 – 0.73 |
| RT-DETRv2-R18 | 1 of 10 frames | 0.31 (below the 0.25 op. threshold used everywhere else, so effectively a non-detection) |

- **A genuine, measured architectural difference, not a training
  artifact:** none of these four checkpoints were ever trained or
  fine-tuned on this project's data — every one is meeting this exact
  object zero-shot. YOLO (CNN) and SAM3 (ViT, prompted purely by visual
  similarity to "person") both key on local shape/texture and get fooled.
  Both RT-DETR checkpoints are markedly more resistant — see Slide 12 for
  what this suggests about *why*.

**Görsel:** `results/eval/yolo26n_zeroshot/comparison/DJI_0501__frame_000000.jpg`
(deck copy: `docs/presentation/media/slide14_statue_dji0501.jpg`) — the
statue boxed green at 0.83 confidence with no red (ground-truth) box
anywhere near it, the cleanest single-frame illustration of the disagreement.

**Kaynak:** `results/yolo26_zeroshot/predictions.json`,
`results/sam3_zeroshot/predictions.json`, `results/rtdetr_zeroshot/predictions.json`,
`results/rtdetr_ultralytics_zeroshot/predictions.json` (statue-region box
scores, all 10 sampled DJI_0501 frames, matched by bounding-box location),
`data/gold_test/annotations.json` (confirms no ground-truth box at that
location)

**Konuşma akışı**
> Not every hard case in this project is a detector making a mistake —
> some are genuinely ambiguous questions about what counts as the target
> class at all. Here's one that turned out to be a real dividing line
> between architectures.
> This is a stone statue on a Scottish hilltop. Human-shaped, human-posed
> — but not alive, and our own ground truth correctly leaves it unlabelled.
> YOLO boxes it as a person at over point-eight confidence in most sampled
> frames. SAM3 does too, a bit less confidently. Both RT-DETR checkpoints
> almost never do. I didn't guess this from looking at one picture — I
> pulled every method's own prediction file and checked all ten sampled
> frames. This is a real, measured difference in what these architectures
> key on, on an object none of them were ever trained on.

---

## Slayt 17 — Error Analysis

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

**Görsel:** video × method heat-grid, coloured by mAP@.5
(`docs/presentation/media/slide15_heatgrid.png`).

**Kaynak:** `results/eval/*/metrics.json` (per_video block, every method)

**Konuşma akışı**
> If you rank each method's own videos from easiest to hardest, you get
> almost the same order every time. That tells you the difficulty lives in
> the footage — small, distant subjects — not in any one detector. Broken
> down by object size, that's confirmed directly: every method's mAP on
> small objects is near zero, medium is workable, large is fine.

---

## Slayt 18 — Strengths, Weaknesses, and Cost

**Tek mesaj:** No method wins on every axis — the real choice is which
trade-off fits the deployment.

*Blok A: Strengths & weaknesses*

| Method | Strengths | Weaknesses |
|---|---|---|
| **YOLO26n** | Fastest, simplest, zero training cost, best precision of any method tried | Structurally blind to small/distant people |
| **Cascade** | Only method that recovers small-object recall from zero; best mAP among trained, deployable methods | Two-stage cost; verifier is data-hungry |
| **RT-DETR** | Genuinely different architecture; competitive ranking quality; measurably more resistant to the DJI_0501 statue false-positive (Slide 12, 15) | More false positives; resolution-fragile; fine-tuning not attempted this cycle (a time-boxed, stated cut — see Slide 20) |
| **SAM3** | Best accuracy and recall of any method, zero training | ~10× slower than any trained detector; not deployable as-is; ideal as a labelling teacher and, per Slide 19, a periodic auditor |

*Blok B: Cost, honestly reported*
- Verifier backbone: ResNet18 11.2M params vs. EfficientNet-B0 4.0M params
  — fewer params ≠ faster on CPU: EfficientNet ran **~5× slower** per crop
  (depthwise-separable convolutions vectorize poorly on general CPU kernels;
  the efficiency gain is real, but GPU-side)
- RT-DETRv2-R18: 20.2M params | RT-DETR-l: 33.0M params
- SAM3: **0.37 FPS on T4** — the only method in this project with a
  committed, reproducible speed number so far
- YOLO26n / cascade / RT-DETR end-to-end FPS on T4: **not yet benchmarked**
  with a dedicated script — an open item, not a hidden one (see Slide 20)

**Görsel:** Blok A'nın kendisi tablo olarak slaytta yer alır (ayrı bir 2×2
grid'e gerek yok) + Blok B için sade bir parametre/hız tablosu.

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

## Slayt 19 — Proposed Production System

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
  project: SAM3 as the pseudo-labelling teacher (Slide 6), the cascade as
  the deployable student (Slides 8-10) — extended here into an ongoing
  production role instead of a one-time labelling pass

**Görsel:** basit sistem şeması —
`docs/presentation/media/slide17_production_system.png` (video akışı →
cascade her frame + SAM3 ~10s'de bir, paralel → agreement check →
uyuşmazlıkta insan incelemesi). Şema altında/yanında, cascade'in bir test
videosu üzerinde uçtan uca çalıştığı **kısa bir klip** hâlâ eksik —
sistemi diyagram olarak değil, çalışırken göstermek burada tam yerine
oturur ama bu klip GPU/Colab'a bağlı (`kalan_isler.md`, yarınki YOLO
eğitimi/test-video inference adımıyla aynı çıktı); üretilince buraya ve
Slayt 21'a aynı klip konur.

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

## Slayt 20 — Honest Limitations & Future Work

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

## Slayt 21 — Closing

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
- Every training and inference step ran in the Colab notebooks in
  `notebooks/`, and the full project runs end-to-end from the README in
  the repository

**Görsel:** kod deposu QR kodu
(`docs/presentation/media/slide19_repo_qr.png` →
github.com/Kametor/object-detection-drone) + README'ye referans; varsa
birleştirilmiş sonuç videosu burada canlı gösterilir (henüz üretilmedi,
GPU'ya bağlı — bkz. Slayt 19 notu).

**Konuşma akışı**
> A simple baseline exposed one very specific failure: small, distant
> objects. Everything else in this talk is a genuinely distinct response to
> that one failure — a second-stage verifier, a different architecture
> family, a foundation model used zero-shot — and each one trades something
> for something else. None of them is a strict upgrade over the others; the
> honest answer is "it depends what you're optimising for."
> Every number I've shown you today comes from a file in this project's
> results directory, not from memory or a hand-edited table. Every training
> and inference step ran in the Colab notebooks you see in the repository,
> and the whole project runs end-to-end straight from the README. The code
> and the full decision history are in the repository — happy to walk
> through any of it live.

---

## Slayt 22 — References

**Layout:** Tek slayt, iki sütun, küçük punto. Sıralama: Models → Datasets →
Evaluation → Tools/Libraries. Bu slaytı okuma, tek cümmeyle geç (bkz.
"Literatür ve Atıf Stratejisi" yukarıda).

**Models**
- Ren, S. et al. *RT-DETR: DETRs Beat YOLOs on Real-Time Object Detection.*
  CVPR 2024.
- Lv, W. et al. *RT-DETRv2: Improved Baseline with Bag-of-Freebies.* 2024.
- Meta AI. *SAM 3: Segment Anything with Concepts.* 2025.
- Redmon, J. et al. *You Only Look Once: Unified, Real-Time Object
  Detection (YOLO).* CVPR 2016.
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
