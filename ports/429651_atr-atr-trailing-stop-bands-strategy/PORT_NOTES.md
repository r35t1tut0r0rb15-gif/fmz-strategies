# #429651 基于ATR指标的自适应跟踪止损策略ATR-Trailing-Stop-Bands-Strategy -> `fmz_429651_atr_band_flip`

- FMZ source id: 429651 (lineage).
- Source: https://www.fmz.com/strategy/429651 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-19 12:42:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples and wick averages from the bars. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [5, 14] x `mult` [4.0, 2.5]: **4 trials**; wick protection 30 (average) fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
