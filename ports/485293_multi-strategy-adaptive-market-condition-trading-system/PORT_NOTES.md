# #485293 多策略自适应市场条件交易系统-Multi-Strategy-Adaptive-Market-Condition-Trading-System -> `fmz_485293_sma_cross_or_bb_rsi_extreme`

- FMZ source id: 485293 (lineage).
- Source: https://www.fmz.com/strategy/485293 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-07 09:59:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages, bands and an oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [50, 100] x `bb_mult` [2.0, 2.5]: **4 trials**; defaults 50 / 2 (the source's); SMA 10, RSI 14 (30 / 70) and BB
20 fixed.

## Ambiguities resolved

- Both signals on one bar: the short (written last) wins. The "strong buy" pattern only draws a label. REVERSAL
  INTENDED. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
