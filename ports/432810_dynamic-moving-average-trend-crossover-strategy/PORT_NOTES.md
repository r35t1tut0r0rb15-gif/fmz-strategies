# #432810 Dynamic Moving Average Trend Crossover Strategy -> `fmz_432810_hpotter_macd_state`

- FMZ source id: 432810 (lineage).
- Source: https://www.fmz.com/strategy/432810 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-21 17:18:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [16, 26]: **4 trials**; signal SMA 11 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
