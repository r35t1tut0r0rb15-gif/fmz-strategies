# #453661 Williams-R-动态调整止盈止损策略-Williams-R-Dynamic-TP-SL-Adjustment-Strategy -> `fmz_453661_williams_r_reentry_tick_bracket_reversal`

- FMZ source id: 453661 (lineage).
- Source: https://www.fmz.com/strategy/453661 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:52:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | %R re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 14] x `k_atr` [0.015, 1.0]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (4h ~400). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
