# #436994 基于斐波那契HMA的AI买卖信号策略Fibonacci-HMA-AI-Buy-Sell-Signal-Strategy -> `fmz_436994_hma_21_233_cross`

- FMZ source id: 436994 (lineage).
- Source: https://www.fmz.com/strategy/436994 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 11:24:34). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 34] x `slow` [233, 144]: **4 trials**.

## Ambiguities resolved

- Strict crossing as written; HMA 377 plotted only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
