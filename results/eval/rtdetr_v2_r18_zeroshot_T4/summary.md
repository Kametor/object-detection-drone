# rtdetr_v2_r18_zeroshot_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4694 |
| mAP@.5 | 0.7401 |
| mAP@.75 | 0.4899 |
| mAP_small | 0.0002 |
| mAP_medium | 0.4196 |
| mAP_large | 0.7414 |
| AR@1 | 0.1615 |
| AR@10 | 0.4967 |
| AR@100 | 0.5107 |
| AR_small | 0.0016 |
| AR_medium | 0.4778 |
| AR_large | 0.7757 |

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
| Berghouse_Leopard_Jog | 0.9770 | 0.6677 | -1.0000 | 0.6566 | 0.7922 |
| DJI_0501 | 0.5650 | 0.2028 | 0.0208 | 0.2293 | -1.0000 |
| DJI_0596 | 0.0292 | 0.0037 | 0.0000 | 0.0068 | -1.0000 |
| DJI_0862 | 0.7746 | 0.4956 | 0.0000 | 0.2959 | 0.7398 |
