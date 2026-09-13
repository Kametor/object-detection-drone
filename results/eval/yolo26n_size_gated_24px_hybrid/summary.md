# yolo26n_size_gated_24px_hybrid — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5135 |
| mAP@.5 | 0.7604 |
| mAP@.75 | 0.5602 |
| mAP_small | 0.0632 |
| mAP_medium | 0.5099 |
| mAP_large | 0.6936 |
| AR@1 | 0.1801 |
| AR@10 | 0.5548 |
| AR@100 | 0.5873 |
| AR_small | 0.1082 |
| AR_medium | 0.5802 |
| AR_large | 0.7718 |

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
| Berghouse_Leopard_Jog | 0.9746 | 0.7368 | -1.0000 | 0.7277 | 0.8466 |
| DJI_0501 | 0.3642 | 0.1082 | 0.0936 | 0.1707 | -1.0000 |
| DJI_0596 | 0.1929 | 0.0865 | 0.0583 | 0.1053 | -1.0000 |
| DJI_0862 | 0.8314 | 0.5705 | 0.0713 | 0.4618 | 0.7243 |
