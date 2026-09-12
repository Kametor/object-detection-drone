# yolo26n_zeroshot — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4815 |
| mAP@.5 | 0.6935 |
| mAP@.75 | 0.5316 |
| mAP_small | 0.0178 |
| mAP_medium | 0.4735 |
| mAP_large | 0.6799 |
| AR@1 | 0.1702 |
| AR@10 | 0.5166 |
| AR@100 | 0.5380 |
| AR_small | 0.0197 |
| AR_medium | 0.5254 |
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
| Berghouse_Leopard_Jog | 0.9348 | 0.7021 | -1.0000 | 0.6902 | 0.8466 |
| DJI_0501 | 0.2257 | 0.0712 | 0.0000 | 0.1281 | -1.0000 |
| DJI_0596 | 0.0520 | 0.0317 | 0.0000 | 0.0495 | -1.0000 |
| DJI_0862 | 0.8002 | 0.5514 | 0.0713 | 0.4413 | 0.7087 |
