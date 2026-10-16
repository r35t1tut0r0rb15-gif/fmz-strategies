# #430772 Dual Oscillation Reversal Signal to Noise Ratio Optimization Combo Strategy -> `fmz_430772_combo_123_signal_to_noise`

- FMZ source id: 430772 (lineage).
- Source: https://www.fmz.com/strategy/430772 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 16:57:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A log ratio of inverse prices against its average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_stn` [21, 42] x `smooth_stn` [29, 15]: **4 trials**; the 123 settings fixed.

## Ambiguities resolved

- Loop bounds as written. Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
