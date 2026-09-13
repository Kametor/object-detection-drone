# yolo26n_score_fusion_efficientnet_b0_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5214 |
| mAP@.5 | 0.7765 |
| mAP@.75 | 0.5623 |
| mAP_small | 0.0488 |
| mAP_medium | 0.5178 |
| mAP_large | 0.6913 |
| AR@1 | 0.1745 |
| AR@10 | 0.5668 |
| AR@100 | 0.6289 |
| AR_small | 0.2541 |
| AR_medium | 0.6189 |
| AR_large | 0.7853 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 550 |
| fp | 204 |
| fn | 169 |
| precision | 0.7294 |
| recall | 0.7650 |
| f1 | 0.7468 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9728 | 0.7355 | -1.0000 | 0.7260 | 0.8466 |
| DJI_0501 | 0.3773 | 0.1116 | 0.1556 | 0.1586 | -1.0000 |
| DJI_0596 | 0.1561 | 0.0740 | 0.0296 | 0.1046 | -1.0000 |
| DJI_0862 | 0.8492 | 0.5806 | 0.1459 | 0.4756 | 0.7237 |
