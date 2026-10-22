# #477524 Dynamic Filtering EMA Cross Strategy for Daily Trend Analysis -> `fmz_477524_daily_0900utc_ema10_50_side_reversal`

- FMZ source id: 477524 (lineage).
- Source: https://www.fmz.com/strategy/477524 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:16:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Daily EMA comparison at a fixed UTC hour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `check_hour` [9, 14]: **4 trials**; slow EMA 50.

## Ambiguities resolved

- The 09:00 UTC bar only (no DST). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
