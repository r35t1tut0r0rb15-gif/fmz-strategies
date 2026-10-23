# #426569 Weis Wave Bollinger Band Trading Strategy -> `fmz_426569_renko_atr14_direction_bb14_breakout_reversal`

- FMZ source id: 426569 (lineage).
- Source: https://www.fmz.com/strategy/426569 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 13:55:24). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts confirmed by a Renko direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (10 % of equity) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `methodvalue` [14, 28]: **4 trials**; 2 sd.

## Ambiguities resolved

- The exits never act, as written; volume only plotted. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
