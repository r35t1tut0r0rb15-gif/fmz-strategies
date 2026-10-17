# #488543 动态多维度趋势追踪与量化交易策略-Dynamic-Multi-Dimensional-Trend-Tracking-and-Quantitative-Trading-Strategy -> `fmz_488543_supertrend_dir_ema_rsi_bracket`

- FMZ source id: 488543 (lineage).
- Source: https://www.fmz.com/strategy/488543 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:31:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | SuperTrend, EMA, RSI, a percentage and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_factor` [0.8, 2.0] x `tp_mult` [3.0, 1.5]: **4 trials**; defaults 0.8 / 3 (the source's); ATR 7, EMA 9, RSI 14
and SL 1 % fixed.

## Re-placed bracket (rule 2, mark `trailing_stop_pending`)

The inPosition gate is cleared at the end of the signal bar (the fill comes at the next open), so it never blocks:
each condition bar re-issues the exit with new levels. The port keeps the entry's bracket.

## Ambiguities resolved

- Pine's supertrend direction is 1 in a down-trend; the source's tests are kept as written.
- REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
