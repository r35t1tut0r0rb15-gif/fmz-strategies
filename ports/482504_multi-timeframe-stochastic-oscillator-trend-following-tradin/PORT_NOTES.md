# #482504 多时框随机震荡趋势跟踪交易策略-Multi-Timeframe-Stochastic-Oscillator-Trend-Following-Trading-Strategy -> `fmz_482504_daily_stoch_cross_ema50_atr_bracket_3h`

- FMZ source id: 482504 (lineage).
- Source: https://www.fmz.com/strategy/482504 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 17:53:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry; the daily value without look-ahead. |
| 2 | PASS | A stochastic, an EMA and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 2 % risk sizing quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `ema_len` [50, 100]: **4 trials**; defaults 1.5 / 50 (the source's); daily stochastic 14,
smoothing 3, 80 / 20 and the 2x target fixed.

## Ambiguities resolved

- `request.security("D", ...)`: the last completed broker day (17:00 America/New_York) as of each bar's close
  (house rule, #490787); the SMA 3 smoothing runs on the chart's bars as written.
- `trail_points` without `trail_offset` is inert: no trail.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
