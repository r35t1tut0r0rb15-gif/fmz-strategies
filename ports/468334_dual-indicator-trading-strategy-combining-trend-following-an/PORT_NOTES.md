# #468334 Dual Indicator Trading Strategy Combining Trend Following and Momentum -> `fmz_468334_macd_zero_cross_sma50_side_atr_bracket_reversal`

- FMZ source id: 468334 (lineage).
- Source: https://www.fmz.com/strategy/468334 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:14:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at entry |
| 2 | PASS | MACD zero crossings with an SMA filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_len` [50, 100] x `sl_mult` [1.5, 3.0] x `tp_mult` [2.0, 4.0]: **8 trials**; the MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
