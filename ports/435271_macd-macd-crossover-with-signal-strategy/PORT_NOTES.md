# #435271 MACD配信交叉策略MACD-Crossover-with-Signal-Strategy -> `fmz_435271_macd_signal_cross_reversal`

- FMZ source id: 435271 (lineage).
- Source: https://www.fmz.com/strategy/435271 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-13 16:58:15). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435271. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal SMA 9 fixed.

## Ambiguities resolved

- Chart resolution only; MACD == 0 na rule ignored. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
