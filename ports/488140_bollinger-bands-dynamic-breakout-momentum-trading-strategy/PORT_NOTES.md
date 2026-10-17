# #488140 布林带动态突破加速度量化交易策略Bollinger-Bands-Dynamic-Breakout-Momentum-Trading-Strategy -> `fmz_488140_bb_upper_breakout_tolerance_exit`

- FMZ source id: 488140 (lineage).
- Source: https://www.fmz.com/strategy/488140 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 14:10:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands and bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.9, 2.5] x `tolerance` [4, 2]: **4 trials**; defaults 1.9 / 4 (the source's); BB 20 fixed.

## Ambiguities resolved

- The exit block tests `strategy.position_size` (the position at the bar's start): counting starts on the fill
  bar; the counter resets only on a close above the band or an exit, as written.
- Long only (the short entry and exit are comments): opposite entries cannot occur. "5m" in the title is a label;
  the backtest header is daily: broker days, FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
