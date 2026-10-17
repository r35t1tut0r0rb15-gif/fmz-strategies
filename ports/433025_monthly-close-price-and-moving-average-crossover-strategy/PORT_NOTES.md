# #433025 Monthly Close Price and Moving Average Crossover Strategy -> `fmz_433025_monthly_close_vs_ema`

- FMZ source id: 433025 (lineage).
- Source: https://www.fmz.com/strategy/433025 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 17:09:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; monthly values from completed months |
| 2 | PASS | A close against its moving average |
| 3 | PASS | Exchange pair in the header only (the other-ticker option is off). |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_ma` [8, 12] x `exponential` [True, False]: **4 trials**; resolution "M" fixed.

## Ambiguities resolved

- Previous completed month from broker days. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
