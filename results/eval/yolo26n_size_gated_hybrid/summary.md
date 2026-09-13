# yolo26n_size_gated_hybrid — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5119 |
| mAP@.5 | 0.7525 |
| mAP@.75 | 0.5602 |
| mAP_small | 0.0556 |
| mAP_medium | 0.5078 |
| mAP_large | 0.6936 |
| AR@1 | 0.1801 |
| AR@10 | 0.5541 |
| AR@100 | 0.5853 |
| AR_small | 0.0984 |
| AR_medium | 0.5784 |
| AR_large | 0.7718 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 519 |
| fp | 88 |
| fn | 200 |
| precision | 0.8550 |
| recall | 0.7218 |
| f1 | 0.7828 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9746 | 0.7368 | -1.0000 | 0.7277 | 0.8466 |
| DJI_0501 | 0.3642 | 0.1082 | 0.0936 | 0.1707 | -1.0000 |
| DJI_0596 | 0.1929 | 0.0865 | 0.0583 | 0.1053 | -1.0000 |
| DJI_0862 | 0.8153 | 0.5654 | 0.0356 | 0.4573 | 0.7243 |
