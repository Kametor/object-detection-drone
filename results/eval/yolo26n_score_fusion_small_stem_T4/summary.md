# yolo26n_score_fusion_small_stem_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5255 |
| mAP@.5 | 0.7858 |
| mAP@.75 | 0.5648 |
| mAP_small | 0.0734 |
| mAP_medium | 0.5228 |
| mAP_large | 0.6894 |
| AR@1 | 0.1797 |
| AR@10 | 0.5690 |
| AR@100 | 0.6289 |
| AR_small | 0.2541 |
| AR_medium | 0.6189 |
| AR_large | 0.7853 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 559 |
| fp | 182 |
| fn | 160 |
| precision | 0.7544 |
| recall | 0.7775 |
| f1 | 0.7658 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9727 | 0.7333 | -1.0000 | 0.7247 | 0.8466 |
| DJI_0501 | 0.3647 | 0.1098 | 0.0815 | 0.1673 | -1.0000 |
| DJI_0596 | 0.2457 | 0.1155 | 0.0698 | 0.1545 | -1.0000 |
| DJI_0862 | 0.8541 | 0.5829 | 0.1711 | 0.4796 | 0.7224 |
