# #432967 Dual Rate of Change Momentum Indicator Trading Strategy -> `fmz_432967_movroc_kst_state`

- FMZ source id: 432967 (lineage).
- Source: https://www.fmz.com/strategy/432967 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-23 10:37:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

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

`roc1` [6, 4] x `roc4` [20, 30]: **4 trials**; ROC 10 / 15 and the four smoothings fixed.

## Ambiguities resolved

- State holds at zero. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
