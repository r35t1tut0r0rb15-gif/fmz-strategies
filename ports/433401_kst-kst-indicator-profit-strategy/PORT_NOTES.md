# #433401 KST指标获利策略KST-Indicator-Profit-Strategy -> `fmz_433401_kst_signal_cross`

- FMZ source id: 433401 (lineage).
- Source: https://www.fmz.com/strategy/433401 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 11:37:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rates of change in percent |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`siglen` [9, 5] x `roc4` [33, 50]: **4 trials**; the other ROC / SMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
