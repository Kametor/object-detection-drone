# Drone Videolarında Nesne Tespiti — Roketsan Mülakat Görevi

**Durum: kurulum aşaması — sonuçlar henüz üretilmedi.**
Bu README, sonuçlar üretildikçe `docs/00_plan.md`'deki her gün sonunda
güncellenecektir. Kurulum/çalıştırma adımları ve nicel sonuç tablosu
Gün 6'da (bkz. plan) buraya eklenecek.

## Görev

Görev tanımı: `../bilgisayarli_goru_mulakat_gorevi.pdf` (repo dışında tutulur, izlenmez)
Veri seti: [Kaggle — kmader/drone-videos](https://www.kaggle.com/datasets/kmader/drone-videos)

## Proje düzeni

```
configs/        # her deney için bir YAML; hardcoded hiperparametre yok
data/           # gitignored — Drive/Colab'da tutulur
docs/           # karar günlüğü, hedef seçimi, plan, referans materyaller (Türkçe)
notebooks/      # teslim edilecek Colab notebook
scripts/        # numaralı giriş noktaları: 01_inventory.py, 02_sample_frames.py, ...
src/
  data/         # örnekleme, split, pseudo-labeling
  methods/      # baseline_motion/, openvocab/, student/
  eval/         # metrikler, TIDE sarmalayıcı, grafikler
results/        # üretilen tablo/figür/log — elle düzenlenmez
```

## Çalışma planı ve karar günlüğü

- [`docs/00_plan.md`](docs/00_plan.md) — gün gün yürütme planı
- [`docs/decision_log.md`](docs/decision_log.md) — teknik kararlar ve gerekçeleri
- [`docs/00_target_selection.md`](docs/00_target_selection.md) — hedef sınıf seçimi (TBD)
- [`docs/reference/`](docs/reference/) — literatür taraması (görev PDF'i repo dışında)

## Proje kuralları

- **Train/val/test split'leri video seviyesinde yapılır, frame seviyesinde
  değil.** Ardışık frame'ler neredeyse birebir aynıdır; frame seviyeli split
  test verisinin eğitime sızmasına ve tüm metriklerin yapay şekilde
  yükselmesine yol açar. Split her zaman tutulan (held-out) videolar
  üzerinden yapılır.
- **Altın (gold) test seti tamamen insan tarafından etiketlenir ve hiçbir
  pseudo-labeling adımına girmez.** Hiçbir model çıktısı ground truth'a
  karışmaz.
- **Raporlanan her sayı tekrar üretilebilir olmalıdır:** sabit seed,
  commit'lenmiş config dosyası, çalıştırma komutu README'de yazılı.
- **Her şey standart, tek GPU'lu bir Colab oturumunda çalışmalıdır.**
  Teslimden önce notebook uçtan uca ücretsiz T4 katmanında doğrulanır
  (geliştirme L4/Pro'da yapılsa bile).
- **Sonuçlar asla uydurulmaz.** Bir koşum yapılmadıysa bu açıkça belirtilir;
  tablolar elle değil `results/` altındaki dosyalardan script ile üretilir.
