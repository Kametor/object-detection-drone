# rtdetr_ultralytics_l_1920 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.3436 |
| mAP@.5 | 0.6542 |
| mAP@.75 | 0.3345 |
| mAP_small | 0.0925 |
| mAP_medium | 0.3598 |
| mAP_large | 0.3941 |
| AR@1 | 0.1729 |
| AR@10 | 0.4127 |
| AR@100 | 0.4245 |
| AR_small | 0.1279 |
| AR_medium | 0.4399 |
| AR_large | 0.4847 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 509 |
| fp | 442 |
| fn | 210 |
| precision | 0.5352 |
| recall | 0.7079 |
| f1 | 0.6096 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.8140 | 0.5321 | -1.0000 | 0.5312 | 0.5505 |
| DJI_0501 | 0.4913 | 0.2355 | 0.1970 | 0.2467 | -1.0000 |
| DJI_0596 | 0.3728 | 0.1263 | 0.0948 | 0.1803 | -1.0000 |
| DJI_0862 | 0.6426 | 0.3042 | 0.0653 | 0.2533 | 0.3854 |
