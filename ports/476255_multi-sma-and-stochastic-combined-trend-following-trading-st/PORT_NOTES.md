# #476255 Multi SMA and Stochastic Combined Trend Following Trading Strategy -> `fmz_476255_sma74_cross_zone_quarter_candle_run_exit_reversal`

- FMZ source id: 476255 (lineage).
- Source: https://www.fmz.com/strategy/476255 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:43:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings in the range's outer quarters with candle-run exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_length` [20, 50] x `sma_length` [74, 50]: **4 trials**; the 50-unit stop fixed.

## Ambiguities resolved

- A run moves the stop to the current bar's low / high, so the run bar always closes, as written.
- The 50-unit hard stop is a price amount (fraction of 42000). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
