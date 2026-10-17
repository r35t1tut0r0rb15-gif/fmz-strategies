# #488239 灵活双均线交叉量化策略-Flexible-Moving-Average-Crossover-Quantitative-Strategy -> `fmz_488239_sma20_200_cross_direction`

- FMZ source id: 488239 (lineage).
- Source: https://www.fmz.com/strategy/488239 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-26 11:01:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`direction` ["LongShort", "Long"] x `fast` [20, 50]: **4 trials**; defaults LongShort / 20 (the source's); slow SMA
200 and the long test's SMA 200 fixed; MA types SMA (VWMA uses volume, check 8).

## Ambiguities resolved

- The long test crosses `ta.sma(close, 200)`, not the slow-MA input (the same line by default). In Long mode the
  cross down closes the long; closes act on the position at the bar's start (#430850). REVERSAL INTENDED in
  LongShort. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
