# #435104 基于SMAEMA的量化交易策略Quantitative-Trading-Strategy-Based-on-SMA-and-EMA -> `fmz_435104_swing_trail_line_cross`

- FMZ source id: 435104 (lineage).
- Source: https://www.fmz.com/strategy/435104 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 12:31:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`no` [3, 10]: **2 trials**.

## Ambiguities resolved

- Empty exits dropped. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
