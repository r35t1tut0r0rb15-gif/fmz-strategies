# #444975 Ichimoku Oscillator with Stochastic Momentum Index Strategy -> `fmz_444975_smi_signal_ichimoku_osc_sign_reversal`

- FMZ source id: 444975 (lineage).
- Source: https://www.fmz.com/strategy/444975 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 16:23:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMI against its signal with an oscillator filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_len` [21, 10] x `d_len` [9, 3]: **4 trials**; the oscillator lengths fixed.

## Ambiguities resolved

- Level conditions; repeats ignored. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
