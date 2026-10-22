# #441058 Super Trend Following Strategy Based on Moving Averages -> `fmz_441058_stacked_ema_trend_ema21_exit_long`

- FMZ source id: 441058 (lineage).
- Source: https://www.fmz.com/strategy/441058 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 11:10:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMAs and EMA 21 crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len2` [21, 30] x `len4` [200, 100]: **4 trials**; EMA 9 and 50 fixed.

## Ambiguities resolved

- Long only (short commented out). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
