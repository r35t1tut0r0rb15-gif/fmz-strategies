# #428575 Trend Bull Bear Crossover Trading Strategy -> `fmz_428575_daily_vs_monthly_ma_cross`

- FMZ source id: 428575 (lineage).
- Source: https://www.fmz.com/strategy/428575 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 09:56:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; monthly closes used only after the month ends. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gbar` [7, 14] x `abar` [5, 10]: **4 trials**; defaults 7 / 5 (the source's); SMA type fixed.

## Ambiguities resolved

- Monthly close = last completed calendar month of broker-day dates, from the next month on; the 5-bar SMA runs over daily bars, as written.
- Date filters dropped. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
