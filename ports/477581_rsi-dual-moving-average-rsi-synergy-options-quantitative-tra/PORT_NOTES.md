# #477581 双均线-RSI联动期权量化交易策略-Dual-Moving-Average-RSI-Synergy-Options-Quantitative-Trading-Strategy -> `fmz_477581_sma7_13_cross_rsi17_avg_bracket_reversal`

- FMZ source id: 477581 (lineage).
- Source: https://www.fmz.com/strategy/477581 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:24:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill; the short's wrong-side exit as written |
| 2 | PASS | SMA crossings against the RSI side with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 5] x `slow` [13, 30]: **4 trials**; RSI 17 / 64 / 43, target 4 %, stop 0.5 %.

## Ambiguities resolved

- The short's exit uses the long formulas and closes it one bar after the fill, as written.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
