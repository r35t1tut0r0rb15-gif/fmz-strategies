# #439048 Moving Average and Super Trend Tracking Stop Loss Strategy -> `fmz_439048_supertrend_ema14_slope`

- FMZ source id: 439048 (lineage).
- Source: https://www.fmz.com/strategy/439048 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 11:46:01). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend direction and EMA slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [1.0, 2.0] x `len` [14, 30]: **4 trials**; ATR 3 fixed.

## Ambiguities resolved

- State entries. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
