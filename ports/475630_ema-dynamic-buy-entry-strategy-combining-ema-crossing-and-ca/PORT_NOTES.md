# #475630 EMA交叉与蜡烛体穿透结合动态买入策略-Dynamic-Buy-Entry-Strategy-Combining-EMA-Crossing-and-Candle-Body-Penetration -> `fmz_475630_ema14_candle_break_body_wick_long_no_exit`

- FMZ source id: 475630 (lineage).
- Source: https://www.fmz.com/strategy/475630 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 16:50:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA candle breaks; no exit, as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [14, 21]: **2 trials**; the candle shares fixed.

## Ambiguities resolved

- No exit, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
