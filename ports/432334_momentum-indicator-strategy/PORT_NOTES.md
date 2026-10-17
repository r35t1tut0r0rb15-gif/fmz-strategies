# #432334 Momentum Indicator Strategy -> `fmz_432334_macd_signal_cross`

- FMZ source id: 432334 (lineage).
- Source: https://www.fmz.com/strategy/432334 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 15:47:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, pyramiding 3 and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 17]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Level-less exits place no order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
