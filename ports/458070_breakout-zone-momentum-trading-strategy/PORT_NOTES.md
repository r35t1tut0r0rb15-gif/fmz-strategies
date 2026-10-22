# #458070 Breakout Zone Momentum Trading Strategy -> `fmz_458070_sma50_close_cross_range_filter_reversal`

- FMZ source id: 458070 (lineage).
- Source: https://www.fmz.com/strategy/458070 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:00:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a range filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [50, 20] x `breaker` [20, 50]: **4 trials**.

## Ambiguities resolved

- Range filters include the current bar (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
