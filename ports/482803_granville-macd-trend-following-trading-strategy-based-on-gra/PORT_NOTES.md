# #482803 基于Granville与MACD多重信号确认的趋势跟踪交易策略-Trend-Following-Trading-Strategy-Based-on-Granville-and-MACD-Multiple-Signal-Confirmation -> `fmz_482803_granville_macd_staged_cross_bracket_long`

- FMZ source id: 482803 (lineage).
- Source: https://www.fmz.com/strategy/482803 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:46:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | An EMA, MACD and distances from the setup bar. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `tp_mult` [1.618, 1.0]: **4 trials**; defaults 20 / 1.618 (the source's); MACD 12 / 26 / 9
fixed.

## Trailing stop (mark `trailing_stop_pending`)

A new full signal while held is ignored by `strategy.entry` but re-issues `strategy.exit` with the new reversal low
and target. The port keeps the entry's levels.

## Ambiguities resolved

- Bracket fractions of the signal bar's close, re-based on the fill. A signal whose reversal low is not below the
  close emits no entry (zero-length trade, as L2 #491035); the stages reset anyway.
- Long only. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
