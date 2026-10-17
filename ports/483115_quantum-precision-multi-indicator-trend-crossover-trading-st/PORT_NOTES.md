# #483115 量子精确多指标趋势交叉交易策略-Quantum-Precision-Multi-Indicator-Trend-Crossover-Trading-Strategy -> `fmz_483115_ema10_30_confirmation_gate_atr_rr`

- FMZ source id: 483115 (lineage).
- Source: https://www.fmz.com/strategy/483115 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:13:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, momentum, standard deviation and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 1.5] x `rr` [3.0, 2.0]: **4 trials**; defaults 2 / 3 (the source's); ATR 14, momentum 10 and the
EMA 10 / 30 / 20 / 50 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- The short requires the confirmation to be false, as written. `ta.stdev` is the population standard deviation.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h" ("Forex" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
