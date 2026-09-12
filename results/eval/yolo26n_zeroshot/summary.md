# yolo26n_zeroshot — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.3639 |
| mAP@.5 | 0.5463 |
| mAP@.75 | 0.3966 |
| mAP_small | 0.0067 |
| mAP_medium | 0.3163 |
| mAP_large | 0.6694 |
| AR@1 | 0.0558 |
| AR@10 | 0.3797 |
| AR@100 | 0.4081 |
| AR_small | 0.0117 |
| AR_medium | 0.3589 |
| AR_large | 0.7417 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 314 |
| fp | 79 |
| fn | 227 |
| precision | 0.7990 |
| recall | 0.5804 |
| f1 | 0.6724 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Bluemlisalphutte_Flyover | 0.0000 | 0.0000 | 0.0000 | -1.0000 | -1.0000 |
| DJI_0501 | 0.2257 | 0.0712 | 0.0000 | 0.1281 | -1.0000 |
| DJI_0596 | 0.0520 | 0.0317 | 0.0000 | 0.0495 | -1.0000 |
| DJI_0862 | 0.8002 | 0.5514 | 0.0713 | 0.4413 | 0.7087 |
