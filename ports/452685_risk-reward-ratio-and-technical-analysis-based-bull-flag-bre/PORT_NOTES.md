# #452685 Risk Reward Ratio and Technical Analysis Based Bull Flag Breakout Strategy -> `fmz_452685_bull_flag_breakout_3r_long`

- FMZ source id: 452685 (lineage).
- Source: https://www.fmz.com/strategy/452685 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 10:47:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-bar levels as fractions; re-issued exits pending (mark) |
| 2 | PASS | Flag breakouts with a 3R target |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`flag_len` [5, 10] x `rr` [3.0, 2.0]: **4 trials**; the 0.01 buffer fixed.

## Ambiguities resolved

- Re-issued exits pending; opening levels kept. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
