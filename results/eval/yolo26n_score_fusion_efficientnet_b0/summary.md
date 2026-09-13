# yolo26n_score_fusion_efficientnet_b0 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5222 |
| mAP@.5 | 0.7787 |
| mAP@.75 | 0.5645 |
| mAP_small | 0.0475 |
| mAP_medium | 0.5190 |
| mAP_large | 0.6933 |
| AR@1 | 0.1748 |
| AR@10 | 0.5677 |
| AR@100 | 0.6287 |
| AR_small | 0.2443 |
| AR_medium | 0.6200 |
| AR_large | 0.7847 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 550 |
| fp | 203 |
| fn | 169 |
| precision | 0.7304 |
| recall | 0.7650 |
| f1 | 0.7473 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9726 | 0.7355 | -1.0000 | 0.7259 | 0.8466 |
| DJI_0501 | 0.3594 | 0.1037 | 0.1533 | 0.1521 | -1.0000 |
| DJI_0596 | 0.1542 | 0.0736 | 0.0308 | 0.1021 | -1.0000 |
| DJI_0862 | 0.8536 | 0.5818 | 0.1453 | 0.4790 | 0.7251 |
