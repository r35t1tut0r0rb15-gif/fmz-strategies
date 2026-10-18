# #435284 Moving Average Crossover Midpoint Strategy -> `fmz_435284_ma_midpoint_cross`

- FMZ source id: 435284 (lineage).
- Source: https://www.fmz.com/strategy/435284 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 17:38:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average against a channel midpoint |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bperiod` [131, 200] x `shift` [14, 7]: **4 trials**; SMA 44, EMA 53 and the 0.06 % raise fixed.

## Ambiguities resolved

- EMA method (default); commented stops off. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
