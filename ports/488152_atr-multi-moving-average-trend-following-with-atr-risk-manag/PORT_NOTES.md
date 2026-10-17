# #488152 多均线趋势追踪与ATR风险管理量化交易策略-Multi-Moving-Average-Trend-Following-with-ATR-Risk-Management-Quantitative-Trading-Strategy -> `fmz_488152_sma20_50_state_atr_bracket`

- FMZ source id: 488152 (lineage).
- Source: https://www.fmz.com/strategy/488152 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 14:46:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (re-issue and trail marked). |
| 2 | PASS | Moving averages and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity and the unused lot size quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `rr` [2.0, 1.5]: **4 trials**; defaults 2 / 2 (the source's); SMA 20 / 50 and ATR 14 fixed.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written, every bar: `strategy.exit(stop = close -+ 2 ATR, limit = close +- 4 ATR)` from the CURRENT close (a moving
bracket; the port fixes it at the signal bar) and `strategy.exit(trail_price = close, trail_offset = stopLoss x 10 x
mintick)` (about 30 ticks, 0.30 USD, on daily ETH_USDT), whose activation moves with every bar's close: not
expressible in the house trail, not emitted.

## Ambiguities resolved

- Every bar with the SMA state is an entry (the engine ignores a same-side one while held and re-enters after a
  bracket exit). The lot size is computed but unused. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_state"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
