# yolo26n_lowconf_verifier_hybrid — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.2020 |
| mAP@.5 | 0.3678 |
| mAP@.75 | 0.1934 |
| mAP_small | 0.0047 |
| mAP_medium | 0.2577 |
| mAP_large | 0.1605 |
| AR@1 | 0.1410 |
| AR@10 | 0.3960 |
| AR@100 | 0.4036 |
| AR_small | 0.0328 |
| AR_medium | 0.5150 |
| AR_large | 0.2288 |

## Operating point (confidence=0.25, IoU=0.5)

| Metric | Value |
|---|---|
| tp | 396 |
| fp | 426 |
| fn | 323 |
| precision | 0.4818 |
| recall | 0.5508 |
| f1 | 0.5140 |

## Per-video breakdown

| Video | mAP@.5 | mAP@[.5:.95] | mAP_small | mAP_medium | mAP_large |
|---|---|---|---|---|---|
| Berghouse_Leopard_Jog | 0.6581 | 0.4133 | -1.0000 | 0.4122 | 0.7329 |
| DJI_0501 | 0.4836 | 0.1610 | 0.0000 | 0.1802 | -1.0000 |
| DJI_0596 | 0.0204 | 0.0098 | 0.0130 | 0.0080 | -1.0000 |
| DJI_0862 | 0.2724 | 0.1553 | 0.0000 | 0.2194 | 0.1321 |
