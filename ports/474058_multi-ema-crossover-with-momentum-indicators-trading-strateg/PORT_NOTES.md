# #474058 Multi EMA Crossover with Momentum Indicators Trading Strategy -> `fmz_474058_double_ema_cross_rsi_macd_bracket_from_replaced_avg`

- FMZ source id: 474058 (lineage).
- Source: https://www.fmz.com/strategy/474058 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:37:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | Double EMA crossings with RSI / MACD confirmation and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.015, 0.03] x `tp_pct` [0.03, 0.06]: **4 trials**; the EMA / RSI / MACD lengths fixed.

## Ambiguities resolved

- Bracket from the replaced position's price (na from flat), as written; repeat signals not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
