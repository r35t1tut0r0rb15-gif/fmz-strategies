# #482775 高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System -> `fmz_482775_rsi_cross_bb_extreme_reentry`

- FMZ source id: 482775 (lineage).
- Source: https://www.fmz.com/strategy/482775 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 1.5] x `rsi_len` [14, 7]: **4 trials**; defaults 2 / 14 (the source's); BB 20 and the 70 / 30
levels fixed.

## Ambiguities resolved

- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
