# #482863 五分钟开盘突破ATR动态止盈止损量化交易策略-Five-Minute-Opening-Breakout-Strategy-with-Dynamic-ATR-Based-Stop-Loss-and-Take-Profit -> `fmz_482863_opening_candle_breakout_atr_range_bracket`

- FMZ source id: 482863 (lineage).
- Source: https://www.fmz.com/strategy/482863 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:33:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (marked). |
| 2 | PASS | An opening range and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/New_York"] x `tp_factor` [1.5, 1.0]: **4 trials**; defaults UTC / 1.5 (the source as
written); the 1 ATR(14) stop factor fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit` runs every bar with the current ATR, so the stop moves; the port fixes the signal bar's distances at
entry (re-based on the fill).

## Ambiguities resolved

- Clock (check 9 / C6): `timestamp()` without a zone is the chart's zone, UTC on Binance, so the opening candle is the
  09:30 UTC bar as written; the NYSE 09:30 America/New_York open (the comment's intent) is the grid's variant.
- The candle's levels persist until the next opening candle; a signal with a level on the wrong side of the close emits
  no entry (as #490798).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range_breakout"`.

## Marks

`trailing_stop_pending`
