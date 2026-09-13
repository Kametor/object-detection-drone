# yolo26n_score_fusion — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5262 |
| mAP@.5 | 0.7861 |
| mAP@.75 | 0.5678 |
| mAP_small | 0.0758 |
| mAP_medium | 0.5210 |
| mAP_large | 0.7001 |
| AR@1 | 0.1791 |
| AR@10 | 0.5713 |
| AR@100 | 0.6287 |
| AR_small | 0.2443 |
| AR_medium | 0.6200 |
| AR_large | 0.7847 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 565 |
| fp | 228 |
| fn | 154 |
| precision | 0.7125 |
| recall | 0.7858 |
| f1 | 0.7474 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9733 | 0.7355 | -1.0000 | 0.7261 | 0.8466 |
| DJI_0501 | 0.3377 | 0.0963 | 0.1718 | 0.1422 | -1.0000 |
| DJI_0596 | 0.2436 | 0.1111 | 0.0745 | 0.1406 | -1.0000 |
| DJI_0862 | 0.8513 | 0.5825 | 0.1076 | 0.4783 | 0.7318 |
