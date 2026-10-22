# #477511 Multi Level Multi Period EMA Crossover Dynamic Take Profit Optimization Strategy -> `fmz_477511_ema20_50_cross_range_target_reversal`

- FMZ source id: 477511 (lineage).
- Source: https://www.fmz.com/strategy/477511 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 10:50:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar target as a fraction of the fill; per-bar stop described (pending) |
| 2 | PASS | EMA crossings with a range-multiple target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The target multipliers and stop percentage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp1_mult` [0.5, 1.0, 2.0] x `slow` [50, 100]: **6 trials**; EMA 20; the per-bar stop pending.

## Ambiguities resolved

- Only the nearest of the four full-size targets acts (TP1). Per-bar stop from the latest close kept pending (trailing_stop_pending).
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
