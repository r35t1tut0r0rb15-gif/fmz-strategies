# #491035 双指数移动平均趋势震荡器策略基于标准差动态调整的量化交易模型-Dual-Exponential-Moving-Average-Trend-Oscillator-Strategy-A-Standard-Deviation-Based-Dynamic-Quantitative-Trading-Model -> `fmz_491035_dema_band_oscillator_breakout`

- FMZ source id: 491035 (lineage).
- Source: https://www.fmz.com/strategy/491035 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-18 09:19:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar; the trail a house trail (approximation stated). |
| 2 | PASS | Normalised band position, band and ATR distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_dema` [40, 20] x `rr` [1.5, 3.0]: **4 trials**; defaults 40 / 1.5 (the source's); base 20, thresholds 55 / 45,
trail 2 x ATR(14) fixed.

## Trailing stop (mark `trailing_stop`)

As written, with each entry: `strategy.exit(stop = band, limit = close +- (close - band) x 1.5, trail_points =
trail_offset = 2 x ATR(14) / mintick)`, i.e. true ticks: from 2 ATR of profit a stop trails 2 ATR behind the best
price. Ported as `sl_stop` / `tp_stop` from the signal bar plus the house trail `{"type": "volatility", "atr_n": 14,
"k": 2.0, "anchor": "high_low", "activate_after": 0.012}`. **Stated approximation:** the 2-ATR activation becomes a
1.2 % gain (two hourly ATRs on TRX_USD), as #428795. Promotion of a trailing trial needs the cTrader check
(gate `trailing_ctrader_check`).

## Ambiguities resolved

- The trigger is the previous bar's condition; when the signal bar's close is already beyond the band (the stop
  would fire at once on the fill) no entry is emitted, but the direction memory flips, as written.
- Entries alternate (lastDirection) and reverse. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`trailing_stop`
