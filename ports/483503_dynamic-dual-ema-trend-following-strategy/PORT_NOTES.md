# #483503 动态双均线趋势跟踪策略-Dynamic-Dual-EMA-Trend-Following-Strategy -> `fmz_483503_ema_high_low_band_breakout_band_stop`

- FMZ source id: 483503 (lineage).
- Source: https://www.fmz.com/strategy/483503 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:50:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | EMAs of highs, lows and closes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [44, 22] x `direction` ["Both", "Long"]: **4 trials**; defaults 44 / Both (the source's); EMA 200 filter on.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit(stop = emaLow)` (`emaHigh` for shorts) runs on every bar, so the stop follows the opposite EMA band. The
port fixes the signal bar's distance at entry (re-based on the fill). No target.

## Ambiguities resolved

- A signal whose band stop is on the wrong side of the close emits no entry (as #490798).
- Every bar in the condition is an entry signal. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
