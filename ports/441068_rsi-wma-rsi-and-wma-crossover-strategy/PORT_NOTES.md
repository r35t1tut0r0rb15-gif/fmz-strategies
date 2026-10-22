# #441068 RSI和WMA交叉策略RSI-and-WMA-Crossover-Strategy -> `fmz_441068_rsi_wma45_cross_reversal`

- FMZ source id: 441068 (lineage).
- Source: https://www.fmz.com/strategy/441068 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 12:16:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / WMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `wma_length` [45, 20]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
