# #430285 Momentum Stacking Strategy of Different Timeframes -> `fmz_430285_pring_special_k`

- FMZ source id: 430285 (lineage).
- Source: https://www.fmz.com/strategy/430285 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-26 17:39:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rates of change. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smooth` [10, 5, 20]: **3 trials**; the twelve ROC terms fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
