# #482824 高级布林带指标组合动态趋势突破交易策略-Advanced-Bollinger-Bands-Multi-Indicator-Dynamic-Trend-Breakout-Trading-Strategy -> `fmz_482824_bb_break_rsi_mid_adx_atr_stop_trail`

- FMZ source id: 482824 (lineage).
- Source: https://www.fmz.com/strategy/482824 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:52:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop and trail set at entry. |
| 2 | PASS | Bollinger bands, RSI, a DMI / ADX and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity; the stop and trail via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `trail_k` [0.5, 1.0]: **4 trials**; defaults 1.5 / 0.5 (the source's); BB 20 / 2, DMI and ADX
14 (ADX > 25), RSI 14 (40-60) and ATR 14 fixed.

## Trailing stop (mark `trailing_stop`)

`trail_price` = close -/+ 1 ATR is already passed at the fill, so the trail runs from the entry; `trail_offset` =
0.5 ATR is a price distance given to a tick argument, read as a price distance (#427592). House trail
`{"type": "volatility", "atr_n": 14, "k": 0.5, "anchor": "high_low"}` (the house ATR updates each bar; Pine fixes the
signal bar's ATR; as #428795), with the fixed 1.5 ATR stop beside it.

## Ambiguities resolved

- DI and ADX use SMA smoothing (as written). REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop`
