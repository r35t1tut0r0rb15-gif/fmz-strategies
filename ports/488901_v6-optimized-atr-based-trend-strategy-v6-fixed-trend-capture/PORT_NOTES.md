# #488901 优化的基于平均真实波动范围的趋势策略v6固定趋势捕捉-Optimized-ATR-Based-Trend-Strategy-v6-Fixed-Trend-Capture -> `fmz_488901_supertrend_ema_rsi_atr_lockout_bracket`

- FMZ source id: 488901 (lineage).
- Source: https://www.fmz.com/strategy/488901 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 16:50:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar; re-placed exits marked. |
| 2 | PASS | SuperTrend, EMA, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; exits via `stops()` / signals and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [5.0, 3.0] x `rsi_level` [45, 50]: **4 trials**; defaults 5 / 45 (the source's); EMA 50, SuperTrend 2 / 5,
ATR 14 / 50, stop 2.8 ATR and break-even 2 ATR fixed.

## Re-placed exits (rule 2, mark `trailing_stop_pending`)

Both exits are re-issued on every signal bar while held. "TSL/TP" gets new levels (the port keeps the entry's).
"BreakEven" (stop = fill + 2 ATR for a long) is above the price unless the trade is already 2 ATR ahead, so it fills
at the next open: ported as an exit signal on such bars; when the trade is 2 ATR ahead it is a profit-locking stop
that moves with the ATR (not emitted). `trail_offset` without `trail_points` / `trail_price` is inert.

## Ambiguities resolved

- tpHit locks entries on any flat bar after a closed trade until the next SuperTrend flip, as written; simulate()
  follows the house bracket on bars to know the position.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
