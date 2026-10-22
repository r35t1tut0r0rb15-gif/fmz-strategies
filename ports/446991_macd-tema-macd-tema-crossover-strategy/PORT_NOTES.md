# #446991 MACD-TEMA-交叉策略-MACD-TEMA-Crossover-Strategy -> `fmz_446991_tema_macd_signal_cross_reversal`

- FMZ source id: 446991 (lineage).
- Source: https://www.fmz.com/strategy/446991 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-03 18:25:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TEMA-MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal length 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
