# #458044 Dynamic Adaptive Momentum Breakout Strategy -> `fmz_458044_engulfing_adaptive_momentum_timed_exit_reversal`

- FMZ source id: 458044 (lineage).
- Source: https://www.fmz.com/strategy/458044 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:36:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the time exits are bar counts |
| 2 | PASS | Engulfing bars with adaptive momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [3, 6] x `ema_len` [7, 14]: **4 trials**; the 10-40 length band and 2 % step fixed.

## Ambiguities resolved

- Per-side timers as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
