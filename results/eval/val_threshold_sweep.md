# Cascade threshold choice (val split)

YOLO26n @ imgsz=1920, one inference pass at conf>=0.01, then filtered per threshold.

Coverage is measured against the val split's **SAM3 pseudo-labels** (107 boxes) at IoU>=0.5 — val has no human ground truth by design, so this is a knob-choosing proxy, not an accuracy result.

| conf | candidates | per frame | covered | recall |
|---|---|---|---|---|
| 0.01 | 329 | 6.09 | 86 | 0.804 |
| 0.05 | 109 | 2.02 | 67 | 0.626 |
| 0.10 | 69 | 1.28 | 51 | 0.477 |
| 0.15 | 52 | 0.96 | 44 | 0.411 |
| 0.20 | 40 | 0.74 | 38 | 0.355 |
| 0.25 | 30 | 0.56 | 29 | 0.271 |
| 0.30 | 28 | 0.52 | 27 | 0.252 |
