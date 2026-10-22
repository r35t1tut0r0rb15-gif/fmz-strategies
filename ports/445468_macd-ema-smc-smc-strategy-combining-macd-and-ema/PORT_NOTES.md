# #445468 MACD与EMA结合的SMC策略SMC-Strategy-Combining-MACD-and-EMA -> `fmz_445468_macd_side_ema200_side_reversal`

- FMZ source id: 445468 (lineage).
- Source: https://www.fmz.com/strategy/445468 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 17:37:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD side with an EMA trend side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `fast` [12, 8]: **4 trials**; the slow and signal lengths fixed.

## Ambiguities resolved

- SMC inputs always true. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
