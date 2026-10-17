# #483116 双均线交叉结合RSI动量优化交易策略-Dual-Moving-Average-Crossover-with-RSI-Momentum-Enhancement-Strategy -> `fmz_483116_ema9_21_cross_rsi_always_in_1d`

- FMZ source id: 483116 (lineage).
- Source: https://www.fmz.com/strategy/483116 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:57:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 26]: **4 trials**; defaults 9 / 21 (the source's); RSI 14 (70 / 30) fixed.

## Ambiguities resolved

- REVERSAL INTENDED (always in once started); no exits or stops. "Gold" in the title is a label.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
