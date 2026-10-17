# #483123 趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System -> `fmz_483123_ema9_21_sma15_candle_bar_stop_4d`

- FMZ source id: 483123 (lineage).
- Source: https://www.fmz.com/strategy/483123 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:35:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, candle colours and the signal bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [4.0, 2.0] x `sma_len` [15, 30]: **4 trials**; defaults 4 / 15 (the source's); EMA 9 / 21 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A later same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's
bracket.

## Ambiguities resolved

- The stop at the signal bar's low (high) and the 4 R target become fractions of the signal close, picked by the
  signal's side, re-based on the fill; both positive under the candle conditions.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Four-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "4D":
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
