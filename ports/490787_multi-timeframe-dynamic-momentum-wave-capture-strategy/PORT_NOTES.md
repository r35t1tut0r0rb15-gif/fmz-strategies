# #490787 多时段动态动量波动捕捉策略-Multi-Timeframe-Dynamic-Momentum-Wave-Capture-Strategy -> `fmz_490787_wavetrend_extreme_hourly_channel`

- FMZ source id: 490787 (lineage).
- Source: https://www.fmz.com/strategy/490787 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-16 14:53:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the hourly close only after the hour completes. |
| 2 | PASS | Oscillator levels, EMAs and price-relative stops. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-risk quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [3.0, 1.5] x `extreme_level` [50, 60]: **4 trials**; defaults 3 / 50 (the source's); EMA 12, EMA 200 of highs /
lows, WaveTrend 9 / 12 / 3 and one confirmation bar fixed.

## Re-placed bracket (rule 2, mark `trailing_stop_pending`)

`strategy.exit(stop = longStop, limit = close + 3 x risk)` is issued on every signal bar, also while the trade is open
(the entry is then ignored), so later signal bars move the bracket to their own extreme / channel level. The port keeps
the bracket of the entry (from the signal bar, re-based on the fill).

## Ambiguities resolved

- The 60-minute security is the last completed hour's close, from the first minute of the next hour (house rule;
  TradingView shows it one minute earlier).
- An entry needs a live oversold / overbought run (math.min with na is na), as written.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`trailing_stop_pending`
