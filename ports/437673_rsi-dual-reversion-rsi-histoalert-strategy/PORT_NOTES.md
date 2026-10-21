# #437673 双重反转RSI历史警报策略Dual-Reversion-RSI-HistoAlert-Strategy -> `fmz_437673_reversal123_rsi_histo_combo`

- FMZ source id: 437673 (lineage).
- Source: https://www.fmz.com/strategy/437673 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 17:17:24). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `rsi_period` [13, 21]: **4 trials**; K smoothing 1, D 3, level 50, levels -10 / 10 and 1.5 fixed; reverse off.

## Ambiguities resolved

- Overlapping RSI levels and the 123 test as written; state 0 closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
