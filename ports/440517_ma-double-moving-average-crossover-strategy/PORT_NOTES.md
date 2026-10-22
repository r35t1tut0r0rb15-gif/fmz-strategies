# #440517 金叉死叉双MA策略Double-Moving-Average-Crossover-Strategy -> `fmz_440517_sma5_20_cross_resent_bracket`

- FMZ source id: 440517 (lineage).
- Source: https://www.fmz.com/strategy/440517 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 11:29:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_period` [5, 10] x `long_period` [20, 50]: **4 trials**.

## Ambiguities resolved

- Re-sent bracket pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
