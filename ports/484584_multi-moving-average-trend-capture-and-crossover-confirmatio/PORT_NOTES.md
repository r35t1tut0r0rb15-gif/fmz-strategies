# #484584 多重均线趋势捕捉与交叉确认交易系统-Multi-Moving-Average-Trend-Capture-and-Crossover-Confirmation-Trading-System -> `fmz_484584_ema_ribbon_flat_entries`

- FMZ source id: 484584 (lineage).
- Source: https://www.fmz.com/strategy/484584 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:11:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and ATR. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`instant` [14, 10] x `long_period` [200, 100]: **4 trials**; defaults 14 / 200 (the source's); EMA 50 / 100 and ATR 14
fixed.

## Ambiguities resolved

- The script's `in_position` flags gate entries (only from flat) and track the position; a long close followed by a
  short entry on one bar is a reversal (entry emitted alone): REVERSAL INTENDED. RSI and MACD are unused.
  FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_ribbon"`.

## Marks

`none`
