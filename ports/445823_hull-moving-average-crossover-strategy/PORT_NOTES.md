# #445823 Hull Moving Average Crossover Strategy -> `fmz_445823_ehma200_vs_2bar_cross_reversal`

- FMZ source id: 445823 (lineage).
- Source: https://www.fmz.com/strategy/445823 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 14:57:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull MA slope crossings |
| 3 | PASS | Exchange pair in the header only; the alert JSON names BTC / USDT as text only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 55]: **2 trials**; the variation Ehma fixed.

## Ambiguities resolved

- Ehma default. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
