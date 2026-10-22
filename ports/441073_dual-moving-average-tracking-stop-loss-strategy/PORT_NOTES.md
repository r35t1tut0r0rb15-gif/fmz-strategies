# #441073 Dual Moving Average Tracking Stop Loss Strategy -> `fmz_441073_ema12_sma45_cross_atr_line_long`

- FMZ source id: 441073 (lineage).
- Source: https://www.fmz.com/strategy/441073 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-05 13:45:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA crossings and the ratcheting line test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [12, 20] x `delta` [6, 4]: **4 trials**; SMA 45, stop EMA 12 and the range 15 fixed.

## Ambiguities resolved

- Close-tested line as written. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
