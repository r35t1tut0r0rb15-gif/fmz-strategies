# #488517 基于核平滑多重均线的自适应趋势追踪系统-Adaptive-Trend-Following-System-with-Kernel-Smoothed-Multiple-Moving-Averages -> `fmz_488517_kernel_ma_ribbon_confirmed`

- FMZ source id: 488517 (lineage).
- Source: https://www.fmz.com/strategy/488517 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:13:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail pending (mark). |
| 2 | PASS | Kernel moving averages and oscillators. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the trail quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cross_req` [3, 4] x `confirm` [4, 2]: **4 trials**; defaults 3 / 4 (the source's); the five kernels (Beta 20,
Gaussian 100, Epanechnikov 150, Beta 200, Gaussian 250; alpha = beta = 3, bandwidth 0.3), RSI 7 (40 / 60) and trend
strength 7 (0.5) fixed.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, on every bar in a long: once the close is 2 % above the average price, `close x (1 - 1 %)` ratchets the
trail up; an ATR(1) x 200 level competes (far below the price: inert on the author's market); a confirmed signal bar
resets the trail to na, so no stop is placed on it; `strategy.exit(stop = trail)` (shorts mirrored). A level built
from bar closes and reset by signals is not expressible in the house trail: not emitted. The hard stop and the ATR
target are off by default (not ported).

## Ambiguities resolved

- Kernel index 0 is the current bar; each MA is na until `length` bars exist. The two confirmations cannot hold on
  one bar (they need opposite stacking). REVERSAL INTENDED. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_ribbon"`.

## Marks

`trailing_stop_pending`
