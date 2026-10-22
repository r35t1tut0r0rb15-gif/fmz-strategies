# #439372 Dual Moving Average Price Channel Trading Strategy -> `fmz_439372_g_channel_trend_ema20_pullback`

- FMZ source id: 439372 (lineage).
- Source: https://www.fmz.com/strategy/439372 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 16:44:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel crossings and an EMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_length` [20, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
