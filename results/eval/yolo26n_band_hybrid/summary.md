# yolo26n_band_hybrid — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5029 |
| mAP@.5 | 0.7325 |
| mAP@.75 | 0.5495 |
| mAP_small | 0.0355 |
| mAP_medium | 0.5034 |
| mAP_large | 0.6799 |
| AR@1 | 0.1745 |
| AR@10 | 0.5426 |
| AR@100 | 0.5704 |
| AR_small | 0.0525 |
| AR_medium | 0.5696 |
| AR_large | 0.7508 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 523 |
| fp | 89 |
| fn | 196 |
| precision | 0.8546 |
| recall | 0.7274 |
| f1 | 0.7859 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9747 | 0.7370 | -1.0000 | 0.7277 | 0.8466 |
| DJI_0501 | 0.3154 | 0.0955 | 0.0000 | 0.1600 | -1.0000 |
| DJI_0596 | 0.0893 | 0.0499 | 0.0320 | 0.0616 | -1.0000 |
| DJI_0862 | 0.8171 | 0.5629 | 0.0713 | 0.4617 | 0.7087 |
