# #439273 Bollinger Bands Based Trend Following Strategy -> `fmz_439273_ema40_120_trend_bb_basis_side`

- FMZ source id: 439273 (lineage).
- Source: https://www.fmz.com/strategy/439273 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 16:37:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar stop pending |
| 2 | PASS | EMA trend, Bollinger basis and crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk, capital and ATR quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [40, 20] x `len2` [120, 60]: **4 trials**; Bollinger basis 20 fixed.

## Ambiguities resolved

- Per-bar ATR stop pending; adds are sizing. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
