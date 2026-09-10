# Karar Günlüğü

Her önemli teknik karar burada tarihli bir girdi olarak tutulur: ne karar
verildi, hangi alternatifler değerlendirildi, neden bu seçildi. Bu kayıtlar
doğrudan sunum slaytlarına dönüşecektir.

## 2026-09-10 — Repo iskeleti ve yöntem planının teyidi

**Karar:** Proje katmanlı bir düzende kuruldu (`configs/`, `data/`, `docs/`,
`notebooks/`, `scripts/`, `src/{data,methods,eval}`, `results/`). Literatür
taraması `docs/reference/` altına kondu, günlük çalışma planı
`docs/00_plan.md`'ye yazıldı. Görev PDF'i referans amacıyla repo dışında
tutuluyor.

**Alternatifler:** Tek büyük notebook içinde çalışmak değerlendirildi ve
reddedildi — görev, kod kalitesi ve tekrar üretilebilirliği açıkça
değerlendirme kriteri olarak sayıyor (PDF, "Değerlendirme" bölümü);
notebook-only mantık bu yüzden tercih edilmedi.

**Gerekçe:** `src/` içindeki saf fonksiyonlar hem test edilebilir hem de
notebook'tan import edilerek Colab'da tekrar üretilebilir; `scripts/`
numaralı giriş noktaları ise çalışma sırasını dokümante eder.

**Yöntem planı:**

1. Baseline A — klasik CV, sıfır etiket: ego-motion compensation
   (ORB+RANSAC homography) → warp → frame differencing → morphology →
   connected components. Skor = normalize hareket enerjisi.
2. Baseline B — hazır referans: COCO-pretrained YOLO, zero-shot. Yarışmacı
   değil, domain gap'i ölçen bir cetvel.
3. Alternatif 1 — açık-kelime dağarcığı tespiti: metin destekli
   vision-language dedektör (OWLv2 / YOLO-World / GroundingDINO). Skor =
   görüntü-metin benzerliği. Baseline A'dan tamamen farklı bir paradigma.
4. Alternatif 2 — pseudo-label self-training: Alternatif 1 teacher olarak
   kullanılır, eğitim videolarında pseudo-label üretilir, filtrelenir,
   küçük bir supervised student (YOLO-s / RT-DETR-R18) eğitilir. Başlık
   sonuç: neredeyse sıfır etiketleme maliyeti + deploy edilebilir hız.

**Not — yöntem planı literatürle teyit edildi:** `docs/reference/`'daki
literatür taramasının "reference architecture" bölümü (Katman 2-5), yukarıda
tarif edilen Baseline A/B → Alternatif 1 → Alternatif 2 sırasıyla bağımsız
olarak örtüşüyor. Taramadan alınan iki somut uygulama detayı:

- Pseudo-label onayı **tracklet seviyesinde** yapılmalı, frame seviyesinde
  değil — taramada en büyük verimlilik kazançları (%96, %78) bu
  granülariteden geliyor.
- Teacher dondurulmamalı (STAC'ın tuzağı); EMA ile güncellenmeli.

## 2026-09-11 — Hedef sınıf seçimi

_(Gün 1 sonunda doldurulacak — bkz. `docs/00_target_selection.md`)_
