# yolo26n_score_fusion_small_stem — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5263 |
| mAP@.5 | 0.7876 |
| mAP@.75 | 0.5668 |
| mAP_small | 0.0712 |
| mAP_medium | 0.5247 |
| mAP_large | 0.6912 |
| AR@1 | 0.1811 |
| AR@10 | 0.5705 |
| AR@100 | 0.6287 |
| AR_small | 0.2443 |
| AR_medium | 0.6200 |
| AR_large | 0.7847 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 560 |
| fp | 183 |
| fn | 159 |
| precision | 0.7537 |
| recall | 0.7789 |
| f1 | 0.7661 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9727 | 0.7333 | -1.0000 | 0.7247 | 0.8466 |
| DJI_0501 | 0.3587 | 0.1071 | 0.0715 | 0.1654 | -1.0000 |
| DJI_0596 | 0.2494 | 0.1190 | 0.0707 | 0.1578 | -1.0000 |
| DJI_0862 | 0.8551 | 0.5837 | 0.1452 | 0.4828 | 0.7230 |
