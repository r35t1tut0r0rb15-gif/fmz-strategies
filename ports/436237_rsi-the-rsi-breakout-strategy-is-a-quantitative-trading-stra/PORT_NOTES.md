# #436237 基于相对强弱指数RSI指标的量化交易策略The-RSI-breakout-strategy-is-a-quantitative-trading-strategy -> `fmz_436237_rsi_extremes_wide_bracket`

- FMZ source id: 436237 (lineage).
- Source: https://www.fmz.com/strategy/436237 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 14:06:45). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Percent amounts in ticks -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pct` [0.5, 0.1] x `length` [14, 7]: **4 trials**; levels 30 / 70 fixed.

## Ambiguities resolved

- Dead close calls; percent-in-ticks bracket -> fractions. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
