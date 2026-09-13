# yolo26n_lowconf — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5326 |
| mAP@.5 | 0.8010 |
| mAP@.75 | 0.5706 |
| mAP_small | 0.0641 |
| mAP_medium | 0.5310 |
| mAP_large | 0.7006 |
| AR@1 | 0.1805 |
| AR@10 | 0.5777 |
| AR@100 | 0.6287 |
| AR_small | 0.2443 |
| AR_medium | 0.6200 |
| AR_large | 0.7847 |

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
| Berghouse_Leopard_Jog | 0.9802 | 0.7389 | -1.0000 | 0.7307 | 0.8466 |
| DJI_0501 | 0.3883 | 0.1140 | 0.1553 | 0.1739 | -1.0000 |
| DJI_0596 | 0.2558 | 0.1114 | 0.0315 | 0.1744 | -1.0000 |
| DJI_0862 | 0.8613 | 0.5867 | 0.1444 | 0.4831 | 0.7313 |
