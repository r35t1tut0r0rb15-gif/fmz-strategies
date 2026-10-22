# #440794 Ergotic Momentum Direction Convergence Trading Strategy -> `fmz_440794_ergotic_tsi_signal_daily`

- FMZ source id: 440794 (lineage).
- Source: https://www.fmz.com/strategy/440794 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-02 10:51:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Triple-smoothed TSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`s` [8, 16] x `smth_len` [3, 5]: **4 trials**; r 4 and u 6 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
