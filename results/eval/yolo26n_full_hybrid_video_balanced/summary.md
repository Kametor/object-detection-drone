# yolo26n_full_hybrid_video_balanced — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.2305 |
| mAP@.5 | 0.3932 |
| mAP@.75 | 0.2313 |
| mAP_small | 0.0307 |
| mAP_medium | 0.2563 |
| mAP_large | 0.2912 |
| AR@1 | 0.1289 |
| AR@10 | 0.4645 |
| AR@100 | 0.5075 |
| AR_small | 0.0885 |
| AR_medium | 0.5393 |
| AR_large | 0.5655 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 503 |
| fp | 607 |
| fn | 216 |
| precision | 0.4532 |
| recall | 0.6996 |
| f1 | 0.5500 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.6100 | 0.4058 | -1.0000 | 0.4179 | 0.5166 |
| DJI_0501 | 0.3048 | 0.0930 | 0.0333 | 0.1015 | -1.0000 |
| DJI_0596 | 0.0828 | 0.0331 | 0.0531 | 0.0312 | -1.0000 |
| DJI_0862 | 0.4644 | 0.2778 | 0.0000 | 0.2696 | 0.4131 |
