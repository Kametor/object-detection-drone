# yolo26n_score_fusion_standard_stem_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5259 |
| mAP@.5 | 0.7847 |
| mAP@.75 | 0.5667 |
| mAP_small | 0.0765 |
| mAP_medium | 0.5194 |
| mAP_large | 0.7006 |
| AR@1 | 0.1789 |
| AR@10 | 0.5723 |
| AR@100 | 0.6289 |
| AR_small | 0.2541 |
| AR_medium | 0.6189 |
| AR_large | 0.7853 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 563 |
| fp | 226 |
| fn | 156 |
| precision | 0.7136 |
| recall | 0.7830 |
| f1 | 0.7467 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9733 | 0.7355 | -1.0000 | 0.7261 | 0.8466 |
| DJI_0501 | 0.3415 | 0.0986 | 0.1456 | 0.1448 | -1.0000 |
| DJI_0596 | 0.2428 | 0.1101 | 0.0742 | 0.1386 | -1.0000 |
| DJI_0862 | 0.8500 | 0.5826 | 0.1189 | 0.4753 | 0.7328 |
