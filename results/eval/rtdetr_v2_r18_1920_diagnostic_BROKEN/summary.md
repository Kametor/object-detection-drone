# rtdetr_v2_r18_1920_diagnostic_BROKEN — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.0730 |
| mAP@.5 | 0.2525 |
| mAP@.75 | 0.0226 |
| mAP_small | 0.0277 |
| mAP_medium | 0.0718 |
| mAP_large | 0.1059 |
| AR@1 | 0.0698 |
| AR@10 | 0.2067 |
| AR@100 | 0.2327 |
| AR_small | 0.0410 |
| AR_medium | 0.2279 |
| AR_large | 0.3119 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 404 |
| fp | 1733 |
| fn | 315 |
| precision | 0.1891 |
| recall | 0.5619 |
| f1 | 0.2829 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.5010 | 0.1901 | -1.0000 | 0.2031 | 0.1023 |
| DJI_0501 | 0.3121 | 0.1110 | 0.0406 | 0.1278 | -1.0000 |
| DJI_0596 | 0.0897 | 0.0117 | 0.0267 | 0.0135 | -1.0000 |
| DJI_0862 | 0.2923 | 0.0834 | 0.0337 | 0.0673 | 0.1159 |
