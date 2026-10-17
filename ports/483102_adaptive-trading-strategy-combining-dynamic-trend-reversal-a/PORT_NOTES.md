# #483102 动态趋势反转与随机指标结合的自适应交易策略-Adaptive-Trading-Strategy-Combining-Dynamic-Trend-Reversal-and-Stochastic-Indicator -> `fmz_483102_zigzag_reversal_line_stoch_tick_bracket`

- FMZ source id: 483102 (lineage).
- Source: https://www.fmz.com/strategy/483102 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:00:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | A percentage zigzag, a stochastic; tick distances as ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_k` [0.0004, 1.0] x `tp_k` [0.0012, 3.0]: **4 trials**; defaults 0.0004 / 0.0012 (the source's ticks on
BTC_USDT); zigzag 0.25 % (MANUAL), stochastic 9 / 3 and ATR 14 fixed.

## Tick distances (criterion 2)

100 / 300 ticks x mintick 0.01 on BTC_USDT are 1 / 3 USD against a daily ATR of about 2,500 USD: 0.0004 / 0.0012 ATR,
ported as written (the trade ends within a bar or two). The 1 / 3 ATR reading is the grid's variant.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- The zigzag is literal: both direction blocks run on one bar; the reverse range uses the previous bar's pivot (0
  before the first). The static line is the last non-na reverse line.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "zigzag"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
