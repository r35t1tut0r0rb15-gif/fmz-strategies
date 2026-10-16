# #429502 Exponential Moving Average Crossover Strategy -> `fmz_429502_hourly_vs_daily_sma3`

- FMZ source id: 429502 (lineage).
- Source: https://www.fmz.com/strategy/429502 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-17 16:55:10). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days. |
| 2 | PASS | A comparison of two averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot formula and 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 5]: **2 trials**.

## Ambiguities resolved

- Daily SMA from completed broker days. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
