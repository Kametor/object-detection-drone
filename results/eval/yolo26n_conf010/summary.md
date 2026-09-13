# yolo26n_conf010 — evaluation vs. gold test set

## Overall

| Metric | Value |
|---|---|
| mAP@[.5:.95] | 0.5106 |
| mAP@.5 | 0.7554 |
| mAP@.75 | 0.5558 |
| mAP_small | 0.0436 |
| mAP_medium | 0.5074 |
| mAP_large | 0.6934 |
| AR@1 | 0.1745 |
| AR@10 | 0.5466 |
| AR@100 | 0.5801 |
| AR_small | 0.0738 |
| AR_medium | 0.5742 |
| AR_large | 0.7706 |

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
| Berghouse_Leopard_Jog | 0.9606 | 0.7248 | -1.0000 | 0.7157 | 0.8466 |
| DJI_0501 | 0.3210 | 0.0955 | 0.0735 | 0.1543 | -1.0000 |
| DJI_0596 | 0.1590 | 0.0726 | 0.0124 | 0.1193 | -1.0000 |
| DJI_0862 | 0.8483 | 0.5763 | 0.1232 | 0.4711 | 0.7237 |
