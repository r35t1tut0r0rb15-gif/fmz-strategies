# #451399 EMA交叉策略与RSI背离30分钟趋势识别和价格竭尽-EMA-Cross-Strategy-with-RSI-Divergence-30-Minute-Trend-Identification-and-Price-Exhaustion -> `fmz_451399_ema13_26_cross_rsi_divergence_reversal`

- FMZ source id: 451399 (lineage).
- Source: https://www.fmz.com/strategy/451399 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 16:23:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with RSI divergence entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 9] x `slow` [26, 50] x `rsi_len` [7, 14]: **8 trials**; the RSI levels and the EMA 5 / 10 trend fixed.

## Ambiguities resolved

- Call order with id tracking; a close only on its own id. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
