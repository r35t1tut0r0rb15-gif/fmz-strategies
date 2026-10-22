# #443229 Double Confirmation Breakthrough Strategy -> `fmz_443229_prev_day_extreme_cross_ema_trend_reversal`

- FMZ source id: 443229 (lineage).
- Source: https://www.fmz.com/strategy/443229 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-01 10:55:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket pending |
| 2 | PASS | Previous-day extreme crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 50]: **4 trials**.

## Ambiguities resolved

- Previous-day values; the moving bracket pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`trailing_stop_pending`
