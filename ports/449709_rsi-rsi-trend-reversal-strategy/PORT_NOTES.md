# #449709 RSI趋势反转策略-RSI-Trend-Reversal-Strategy -> `fmz_449709_rsi_atr_adaptive_threshold_ha_cross_reversal`

- FMZ source id: 449709 (lineage).
- Source: https://www.fmz.com/strategy/449709 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 13:33:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signals are one bar old |
| 2 | PASS | Adaptive RSI / ATR threshold crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [8, 14] x `rsi_mult` [1.5, 3.0]: **4 trials**; the delay 1 and the 10 % difference fixed.

## Ambiguities resolved

- Variable windows from bars since the last cross; signals one bar late. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
