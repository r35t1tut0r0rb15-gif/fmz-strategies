# #458276 Dual Moving Average Momentum Trading Strategy Time Optimized Trend Following System -> `fmz_458276_sma10_100_cross_utc_window_point_bracket_reversal`

- FMZ source id: 458276 (lineage).
- Source: https://www.fmz.com/strategy/458276 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:50:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of the fill |
| 2 | PASS | SMA crossings in set hours with a point bracket |
| 3 | PASS | Exchange pair in the header only (gold named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 20] x `long_len` [100, 50] x `bracket` [0.00238, 0.005]: **8 trials**; the window fixed.

## Ambiguities resolved

- Second entries never fill (pyramiding 1); points as fractions of 42000. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
