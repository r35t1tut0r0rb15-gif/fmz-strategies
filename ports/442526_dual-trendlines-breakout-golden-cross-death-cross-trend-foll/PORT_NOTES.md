# #442526 Dual Trendlines Breakout Golden Cross Death Cross Trend Following Strategy -> `fmz_442526_daily_close_range_break_sma10_cross_reversal`

- FMZ source id: 442526 (lineage).
- Source: https://www.fmz.com/strategy/442526 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 16:01:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily and weekly values from completed periods |
| 2 | PASS | Daily close-range breakouts with an SMA cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_days` [3, 5] x `sma_len` [10, 20]: **4 trials**.

## Ambiguities resolved

- Daily / weekly values from the last completed broker day / week. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
