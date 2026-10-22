# #443230 Moving Average Crossover Trend Following Strategy -> `fmz_443230_last_4h_sma100_200_cross_daily_reversal`

- FMZ source id: 443230 (lineage).
- Source: https://www.fmz.com/strategy/443230 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-01 10:59:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 4-hour values end with the day |
| 2 | PASS | Lower-time-frame SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [100, 50] x `slow` [200, 400]: **4 trials**.

## Ambiguities resolved

- 4-hour values as the day's last 4-hour bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
