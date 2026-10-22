# #482764 Adaptive Trend Following Strategy Based on Dual EMA Crossover System -> `fmz_482764_ema10_20_cross_close_confirm_reversal`

- FMZ source id: 482764 (lineage).
- Source: https://www.fmz.com/strategy/482764 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with close confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast_length` [10, 5] x `ema_slow_length` [20, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
