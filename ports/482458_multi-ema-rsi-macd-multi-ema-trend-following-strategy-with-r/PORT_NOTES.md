# #482458 Multi-EMA趋势追踪型RSI-MACD动量验证策略-Multi-EMA-Trend-Following-Strategy-with-RSI-MACD-Momentum-Validation -> `fmz_482458_ema_stack_macd_zero_cross_ema34_stop_long`

- FMZ source id: 482458 (lineage).
- Source: https://www.fmz.com/strategy/482458 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:13:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | EMAs, MACD and RSI; the 3 x EMA limit is inert (long) or immediate (short). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_ema` [34, 55] x `rsi_mid` [50, 55]: **4 trials**; defaults 34 / 50 (the source's); EMA 5 / 14 / 34 / 55 stack
and MACD 12 / 26 fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit(stop = ema34)` is re-issued every bar, so the long's stop follows the EMA 34. The port fixes it at
the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- `limit = ema34 * 3`: never reached by a long; for a short it is a buy limit far above the market that fills at
  once, so shorts are zero-length (not emitted, as L2 #491035) and a short signal only closes the long (emitted as
  the long's exit).
- A long signal with the close at or under the EMA 34 emits no entry. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
