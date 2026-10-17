# #489301 量化多空趋势追踪动态止损策略-Quantitative-Long-Short-Trend-Tracking-Dynamic-Stop-Loss-Strategy -> `fmz_489301_utbot_atr_line_long`

- FMZ source id: 489301 (lineage).
- Source: https://www.fmz.com/strategy/489301 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:34:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR-scaled line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted (commission and slippage are costs). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1, 2] x `heikin` [False, True]: **4 trials**; defaults 1 / off (the source's); ATR 10 fixed.

## Ambiguities resolved

- The UT Bot line is an indicator on closes: close-based entries and exits. The Heikin-Ashi switch uses the
  source's simplified candle close (o + h + l + c) / 4.
- Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
