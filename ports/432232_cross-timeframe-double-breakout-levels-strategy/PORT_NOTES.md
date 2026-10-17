# #432232 Cross Timeframe Double Breakout Levels Strategy -> `fmz_432232_noro_week_day_levels`

- FMZ source id: 432232 (lineage).
- Source: https://www.fmz.com/strategy/432232 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 17:27:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed broker weeks / days |
| 2 | PASS | The bar against prior-period levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, the capital % input and the lot formula stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`antipila` [True, False] x `color_filter` [True, False]: **4 trials**; the W / D timeframes and ohlc4 fixed.

## Ambiguities resolved

- Previous broker week / day ohlc4 built from the bars. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
