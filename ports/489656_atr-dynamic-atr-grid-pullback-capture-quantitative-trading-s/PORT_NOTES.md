# #489656 动态ATR网格回撤捕捉量化交易策略-Dynamic-ATR-Grid-Pullback-Capture-Quantitative-Trading-Strategy -> `fmz_489656_wide_range_oversold_target_trail_long`

- FMZ source id: 489656 (lineage).
- Source: https://www.fmz.com/strategy/489656 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 13:47:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; moving target fixed at entry (mark); the trail a house trail. |
| 2 | PASS | ATR multiples, percentages and an oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profit_target` [0.002, 0.01] x `no_trade_zone` [0.005, 0.02]: **4 trials**; defaults 0.002 / 0.005 (the source's);
ATR 10, RSI 14 (30), trail 1 ATR and the 0.1 % activation fixed.

## Moving target and trail (marks `trailing_stop_pending`, `trailing_stop`)

As written, every bar in a trade: `strategy.exit(limit = close x 1.002, trail_price = close x 1.001,
trail_offset = ATR)`. The target follows each bar's close: fixed at 0.2 % of the fill here (`trailing_stop_pending`).
The trail (`trail_offset` in ticks but given the ATR price distance, read as a price distance, as #427592) is ported
as the house trail `{"type": "volatility", "atr_n": 10, "k": 1.0, "anchor": "high_low", "activate_after": 0.001}`;
**stated approximation:** activation measured from the fill instead of each bar's close. Promotion of a trailing
trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- close < close + 0.2 ATR is always true and close > close + 3 ATR never: long only, as written.
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop, trailing_stop_pending`
