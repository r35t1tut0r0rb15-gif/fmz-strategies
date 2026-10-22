# #452736 FVG动量短线交易策略-FVG-Momentum-Scalping-Strategy -> `fmz_452736_fvg_continuation_signal_extreme_target_reversal`

- FMZ source id: 452736 (lineage).
- Source: https://www.fmz.com/strategy/452736 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 17:23:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target as a fraction of the signal close; the moving stop pending (mark) |
| 2 | PASS | Fair-value-gap continuation entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_tp` [1.0012, 1.01] x `short_tp` [0.994, 0.99]: **4 trials**; the 3-bar windows fixed.

## Ambiguities resolved

- Moving stop pending (not ported); targets from the signal bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
