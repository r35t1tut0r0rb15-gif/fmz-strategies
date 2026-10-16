# #430366 Multi Period Dynamic Moving Average Strategy -> `fmz_430366_close_above_sma_long`

- FMZ source id: 430366 (lineage).
- Source: https://www.fmz.com/strategy/430366 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-27 16:07:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Floor(equity / close) per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 20, 50]: **3 trials**.

## Ambiguities resolved

- Default SMA only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
