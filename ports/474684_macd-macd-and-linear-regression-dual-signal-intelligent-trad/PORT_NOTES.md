# #474684 MACD与线性回归双重信号智能交易策略-MACD-and-Linear-Regression-Dual-Signal-Intelligent-Trading-Strategy -> `fmz_474684_macd_cross_rising_linreg24_slope_long_bracket_pending`

- FMZ source id: 474684 (lineage).
- Source: https://www.fmz.com/strategy/474684 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-11 15:46:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with a regression-slope filter; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lr_length` [24, 48] x `signal_len` [9, 5]: **4 trials**; EMA method, Rising Linear, both switches on.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
