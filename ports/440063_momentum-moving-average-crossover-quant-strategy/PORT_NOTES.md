# #440063 Momentum Moving Average Crossover Quant Strategy -> `fmz_440063_sma9_21_cross_day_vs_week_volume_filter_1h_reversal`

- FMZ source id: 440063 (lineage).
- Source: https://www.fmz.com/strategy/440063 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 11:39:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a daily-versus-weekly volume filter on longs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_pct` [50, 25] x `fast` [9, 5]: **4 trials**; slow SMA 21.

## Ambiguities resolved

- Last completed day / week volume; SMA 7 over chart bars as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_filter"`.

## Marks

`none`
