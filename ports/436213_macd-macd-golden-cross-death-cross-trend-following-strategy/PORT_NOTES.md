# #436213 MACD金叉死叉趋势跟踪策略MACD-Golden-Cross-Death-Cross-Trend-Following-Strategy -> `fmz_436213_macd_signal_types_atr_bracket`

- FMZ source id: 436213 (lineage).
- Source: https://www.fmz.com/strategy/436213 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 11:45:54). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Forex-points bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The pip adjuster and year inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`signal` ["Continuation", "Reversal", "Histogram", "MACD Line ZC", "Signal Line ZC"] x `sl_mult` [1.5, 2.5]: **10 trials**; target 1 ATR, MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Forex-points bracket -> ATR multiples; signal types in the grid. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
