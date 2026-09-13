# sam3_zeroshot_T4 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.6256 |
| mAP@.5 | 0.8465 |
| mAP@.75 | 0.6500 |
| mAP_small | 0.0703 |
| mAP_medium | 0.6688 |
| mAP_large | 0.7733 |
| AR@1 | 0.2128 |
| AR@10 | 0.6277 |
| AR@100 | 0.6707 |
| AR_small | 0.1279 |
| AR_medium | 0.6904 |
| AR_large | 0.8040 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 627 |
| fp | 665 |
| fn | 92 |
| precision | 0.4853 |
| recall | 0.8720 |
| f1 | 0.6236 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 1.0000 | 0.9902 | -1.0000 | 0.9901 | 1.0000 |
| DJI_0501 | 0.6060 | 0.1651 | 0.1646 | 0.1821 | -1.0000 |
| DJI_0596 | 0.2600 | 0.1116 | 0.0168 | 0.1798 | -1.0000 |
| DJI_0862 | 0.9065 | 0.6092 | 0.2031 | 0.5187 | 0.7572 |
