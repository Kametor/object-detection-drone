# yolo26n_zeroshot_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4789 |
| mAP@.5 | 0.6933 |
| mAP@.75 | 0.5241 |
| mAP_small | 0.0178 |
| mAP_medium | 0.4725 |
| mAP_large | 0.6764 |
| AR@1 | 0.1700 |
| AR@10 | 0.5160 |
| AR@100 | 0.5364 |
| AR_small | 0.0197 |
| AR_medium | 0.5243 |
| AR_large | 0.7475 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 522 |
| fp | 90 |
| fn | 197 |
| precision | 0.8529 |
| recall | 0.7260 |
| f1 | 0.7844 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9348 | 0.7021 | -1.0000 | 0.6902 | 0.8466 |
| DJI_0501 | 0.2257 | 0.0712 | 0.0000 | 0.1273 | -1.0000 |
| DJI_0596 | 0.0520 | 0.0309 | 0.0000 | 0.0480 | -1.0000 |
| DJI_0862 | 0.7915 | 0.5498 | 0.0713 | 0.4389 | 0.7050 |
