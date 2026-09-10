# Çalışma Planı — Roketsan Bilgisayarlı Görü Mülakat Görevi

Bu doküman, belirlenen yöntem planının (bkz. `docs/decision_log.md`) zamana
yayılmış, kontrol edilebilir versiyonudur. Her gün sonunda "bitti" sayılması
için somut bir çıktı (dosya, tablo, commit) tanımlanmıştır — "üzerinde
çalıştım" değil, "elimde şu var" ölçütü geçerlidir.

Görev PDF'i: `../bilgisayarli_goru_mulakat_gorevi.pdf` (repo dışında, izlenmez)
Literatür taraması: `docs/reference/Autonomous_Labeling_Literature_Review.pptx`

## Zaman çerçevesi

Teslim: 2026-09-17 (bugünden 7 takvim günü). 5 hafta içi akşamı + 2 hafta
sonu günü kullanılabilir.

| Gün | Tarih | Tür | Odak |
|---|---|---|---|
| 0 | Per 09-10 (bu gece) | — | Plan, repo iskeleti, literatür özeti okuma |
| 1 | Cum 09-11 | akşam (~3-4h) | Veri envanteri + hedef sınıf seçimi |
| 2 | Cmt 09-12 | tam gün | Frame sampling, split, gold test set, Baseline A + B |
| 3 | Paz 09-13 | tam gün | Alternatif 1 (açık-kelime dağarcığı tespit) + değerlendirme pipeline'ı |
| 4 | Pzt 09-14 | akşam | Alternatif 2: pseudo-label üretimi + tracklet onayı + gürültü denetimi |
| 5 | Sal 09-15 | akşam | Student model eğitimi + tam nicel/nitel karşılaştırma |
| 6 | Çar 09-16 | akşam | Hata analizi, sonuç videosu, README, Colab T4 doğrulama |
| 7 | Per 09-17 | akşam (tampon) | Sunum, decision log gözden geçirme, son kontrol, teslim |

Prensip: bir görev bir akşamdan uzun sürecek gibi görünüyorsa, önce
küçültülmüş bir versiyonunu öner. Pipeline'ı uçtan uca bitirmek, tek bir
bileşeni cilalamaktan önceliklidir.

---

## Gün 1 — Cuma akşamı: Envanter ve hedef seçimi

**Neden ilk bu:** Hedef sınıf seçimi her şeyin üzerine kurulduğu karardır;
yanlış seçilirse Cumartesi'nin tamamı boşa gider.

- [ ] Kaggle `kmader/drone-videos` setini indir (Drive'a koy — Colab Pro
      oradan okuyacak)
- [ ] `scripts/01_inventory.py`: her videodan düzenli aralıklarla örnek
      frame çıkar, video başına süre/çözünürlük/FPS kaydet
- [ ] Görsel triage: hangi nesneler tekrar tekrar görünüyor, ölçek
      değişimi var mı, ~500+ örnek var mı, occlusion/zor negatif var mı
- [ ] Kararı `docs/00_target_selection.md`'ye yaz (aday sınıflar, neden
      elenenler, neden seçilen — mülakatta sorulacak ilk soru budur)

**Çıktı:** `docs/00_target_selection.md`, `results/inventory/` altında
video başına özet tablo, seçilmiş hedef sınıf.

## Gün 2 — Cumartesi: Veri hazırlama + iki başlangıç noktası

- [ ] `scripts/02_sample_frames.py`: temporal diversity gözeten frame
      örnekleme (near-duplicate elenir), **video seviyesinde** train/val/test
      split (asla frame seviyesinde değil — bkz. README → Proje kuralları)
- [ ] Gold test set: ~100-200 frame'i elle etiketle (CVAT/Roboflow/LabelImg).
      Bu set hiçbir pseudo-label akışına girmeyecek
- [ ] Baseline A (motion): ORB+RANSAC ego-motion compensation → frame
      differencing → morphology → connected components; skor = normalize
      hareket enerjisi
- [ ] Baseline B (zero-shot COCO-YOLO): domain gap'i ölçmek için, yarışmacı
      değil cetvel olarak çalıştır
- [ ] Her ikisini gold test set üzerinde ilk kez skorla (henüz final değil)

**Çıktı:** `data/splits/{train,val,test}.txt` (video listeleri),
`data/gold_test/` etiketli set, `src/methods/baseline_motion/`,
Baseline A/B için ilk sonuçlar `results/baseline_a/`, `results/baseline_b/`.

## Gün 3 — Pazar: Alternatif 1 ve değerlendirme altyapısı

- [ ] Açık-kelime dağarcığı dedektörü kur (OWLv2 / GroundingDINO / YOLO-World)
      — literatür taramasında önerilen eşikler (kutu 0.30, metin 0.25)
      başlangıç noktası; prompt varyantlarını küçük bir örnekte karşılaştır
- [ ] `src/eval/`: mAP@0.5, mAP@0.5:0.95, PR eğrisi, boyuta göre kırılım
      (küçük/orta/büyük), TIDE hata ayrıştırması
- [ ] **Sabit skor eşiğinde karşılaştırma yok** — motion energy, class
      confidence, text-image similarity aynı ölçekte değil
- [ ] Baseline A, Baseline B, Alternatif 1 için ilk üçlü nicel tablo

**Çıktı:** `src/methods/openvocab/`, `src/eval/metrics.py`,
`results/comparison_v1/` (3 yöntemli ilk tablo + PR eğrileri).

## Gün 4 — Pazartesi akşamı: Pseudo-label self-training

- [ ] Alternatif 1'i teacher olarak kullanıp eğitim videolarında pseudo-label
      üret
- [ ] Gürültü filtreleme: yüksek güven eşiği → ByteTrack ile temporal
      consistency (kısa track'leri at, flicker çoğunlukla yanlış pozitif) →
      NMS → min kutu alanı → kenar kırpma kuralları
- [ ] **~100 pseudo-label'i elle denetle, ölçülen gürültü oranını
      raporla** — bu sayı sunuma girecek
- [ ] Sonuçları `docs/decision_log.md`'ye tarihli girdi olarak kaydet

**Çıktı:** `src/data/pseudo_label.py`, `results/pseudo_labels/audit.md`
(gürültü oranı + örnekler).

## Gün 5 — Salı akşamı: Student model + tam karşılaştırma

- [ ] Küçük supervised student (YOLO-s veya RT-DETR-R18) pseudo-label'lerle
      eğit — bu, sunumun başlık sonucu (near-zero labeling cost + deploy
      edilebilir hız)
- [ ] Tüm yöntemleri (Baseline A, Baseline B, Alt 1, Alt 2/student) tek
      tabloda nicel karşılaştır: mAP, PR, boyut kırılımı, video/koşul
      kırılımı, hesaplama maliyeti (params, GFLOPs, VRAM, T4 FPS, ve
      insan-etiketleme-dakikası)
- [ ] Nitel karşılaştırma: başarılı, başarısız, belirsiz örnek seçimi

**Çıktı:** `src/methods/student/`, `results/final_comparison/table.csv`
(elle değil, script'ten üretilmiş).

## Gün 6 — Çarşamba akşamı: Hata analizi ve teslim materyali

- [ ] Hata analizi: TIDE kırılımı + temporal stabilite (ardışık frame'ler
      arası flicker oranı) yorumlanır
- [ ] Sonuç videosu (varsa) üretilir
- [ ] `README.md`: kurulum + çalıştırma adımları, tek komutla tekrar
      üretilebilirlik
- [ ] Notebook'un Colab **free-tier T4**'te uçtan uca doğrulanması —
      geliştirme ortamı (Pro/L4) değil, teslim ortamı esas alınır

**Çıktı:** `README.md`, `notebooks/` içindeki teslim notebook'u T4'te
yeşil, sonuç videosu (varsa) `results/`.

## Gün 7 — Perşembe akşamı (tampon): Sunum ve son kontrol

- [ ] Sunumu PDF'teki "Sonuçların Sunulması" listesine birebir eşle
      (seçilen hedef, veri hazırlama stratejisi, başlangıç yaklaşımı,
      alternatif yaklaşım, nicel/nitel karşılaştırma, başarılı/başarısız/
      belirsiz sonuçlar, hata analizi, güçlü/zayıf yönler, hesaplama
      maliyeti)
- [ ] `docs/decision_log.md` gözden geçirilir — her teknik karar
      gerekçesiyle sunumda karşılığını buluyor mu?
- [ ] Kod temizliği: `pathlib`, type hint, config-driven çalıştırma
      (hardcoded hiperparametre yok) kontrolü
- [ ] Son uçtan uca reproducibility kontrolü, teslim

**Çıktı:** Sunum dosyası, teslime hazır repo.

---

## İzleme kuralları

- Her scriptin ürettiği sonuç `results/` altına, script'in kendisi
  tarafından yazılır — elle düzenlenmez.
- Her akşamın sonunda bu dosyadaki ilgili checkbox'lar işaretlenir ve
  varsa sapma (planlanan yapılamadıysa neden) bir satırla not edilir.
- Bir gün planın gerisinde kalınırsa önce kapsam küçültülür (production
  serving, çoklu sınıf tespiti, geniş hyperparameter sweep, tüm veri
  setinin elle etiketlenmesi kapsam dışı), süre uzatılmaz.
