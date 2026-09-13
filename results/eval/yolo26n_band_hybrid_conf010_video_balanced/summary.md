# yolo26n_band_hybrid_conf010_video_balanced — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4990 |
| mAP@.5 | 0.7336 |
| mAP@.75 | 0.5444 |
| mAP_small | 0.0393 |
| mAP_medium | 0.4947 |
| mAP_large | 0.6864 |
| AR@1 | 0.1747 |
| AR@10 | 0.5381 |
| AR@100 | 0.5634 |
| AR_small | 0.0557 |
| AR_medium | 0.5551 |
| AR_large | 0.7610 |

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
| Berghouse_Leopard_Jog | 0.9604 | 0.7221 | -1.0000 | 0.7135 | 0.8466 |
| DJI_0501 | 0.2929 | 0.0908 | 0.0936 | 0.1494 | -1.0000 |
| DJI_0596 | 0.1244 | 0.0613 | 0.0234 | 0.0861 | -1.0000 |
| DJI_0862 | 0.8171 | 0.5623 | 0.0713 | 0.4556 | 0.7159 |
