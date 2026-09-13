# rtdetr_ultralytics_l_zeroshot — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.4598 |
| mAP@.5 | 0.7309 |
| mAP@.75 | 0.4836 |
| mAP_small | 0.0040 |
| mAP_medium | 0.4136 |
| mAP_large | 0.7254 |
| AR@1 | 0.1669 |
| AR@10 | 0.4857 |
| AR@100 | 0.4976 |
| AR_small | 0.0033 |
| AR_medium | 0.4640 |
| AR_large | 0.7593 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 538 |
| fp | 168 |
| fn | 181 |
| precision | 0.7620 |
| recall | 0.7483 |
| f1 | 0.7551 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.9898 | 0.6844 | -1.0000 | 0.6692 | 0.8454 |
| DJI_0501 | 0.4468 | 0.1522 | 0.0000 | 0.1846 | -1.0000 |
| DJI_0596 | 0.0413 | 0.0089 | 0.0000 | 0.0132 | -1.0000 |
| DJI_0862 | 0.7660 | 0.4676 | 0.0119 | 0.2592 | 0.7181 |
