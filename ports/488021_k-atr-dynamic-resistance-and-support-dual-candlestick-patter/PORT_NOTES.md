# #488021 动态阻力与支撑的双K线形态ATR风险控制量化交易策略-Dynamic-Resistance-and-Support-Dual-Candlestick-Pattern-ATR-Risk-Management-Quantitative-Trading-Strategy -> `fmz_488021_engulfing_sr50_atr15_bracket_2r_reversal`

- FMZ source id: 488021 (lineage).
- Source: https://www.fmz.com/strategy/488021 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 14:24:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Engulfing patterns with support / resistance filters and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMultiplier` [1.5, 2.5] x `lookback` [50, 20]: **4 trials**; ATR 14, target 2 x the stop.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "3D" (three broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
