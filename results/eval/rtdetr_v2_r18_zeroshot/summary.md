# rtdetr_v2_r18_zeroshot — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4676 |
| mAP@.5 | 0.7398 |
| mAP@.75 | 0.4848 |
| mAP_small | 0.0002 |
| mAP_medium | 0.4184 |
| mAP_large | 0.7427 |
| AR@1 | 0.1611 |
| AR@10 | 0.4964 |
| AR@100 | 0.5099 |
| AR_small | 0.0016 |
| AR_medium | 0.4761 |
| AR_large | 0.7768 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 547 |
| fp | 351 |
| fn | 172 |
| precision | 0.6091 |
| recall | 0.7608 |
| f1 | 0.6766 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9772 | 0.6662 | -1.0000 | 0.6564 | 0.7922 |
| DJI_0501 | 0.5590 | 0.2024 | 0.0208 | 0.2289 | -1.0000 |
| DJI_0596 | 0.0292 | 0.0040 | 0.0000 | 0.0075 | -1.0000 |
| DJI_0862 | 0.7745 | 0.4941 | 0.0000 | 0.2923 | 0.7406 |
