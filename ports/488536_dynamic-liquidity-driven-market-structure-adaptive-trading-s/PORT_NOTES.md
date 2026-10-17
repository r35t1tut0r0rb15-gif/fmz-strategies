# #488536 动态流动性驱动市场结构自适应交易策略-Dynamic-Liquidity-Driven-Market-Structure-Adaptive-Trading-Strategy -> `fmz_488536_liquidity_internal_shift`

- FMZ source id: 488536 (lineage).
- Source: https://www.fmz.com/strategy/488536 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:13:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked stop / target exits. |
| 2 | ADAPT | 10 / 20 ticks -> ATR multiples; candle runs and rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick levels quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mode` ["Both", "Bullish Only"] x `sl_atr` [0.001, 1.0]: **4 trials**; defaults Both / 0.001 (the source as written);
target = 2 x the stop distance (20 / 10 ticks), lookbacks 10 / 10 and ATR 14 fixed. On daily ETH_USDT (tick 0.01,
daily ATR about 100-150) 10 ticks are about 0.001 ATR (judgement, stated before any backtest); the 1 ATR variant
gives the levels room.

## Ambiguities resolved

- `lastInternalShift` is never assigned: the allow-filters always pass. The two signals cannot fall on one bar
  (a bullish shift needs a close above a bearish run's high, impossible on a bearish bar).
- Entries only from flat (the script's `entryPrice` gate): opposite entries cannot occur; an opposite signal while
  held closes the trade. The tick levels are close-checked: exit signals at the next open (rule 3), fixed at the
  entry bar's ATR. As written nearly every next close crosses one (about a one-bar hold).
- Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "market_structure_shift"`.

## Marks

`none`
