# #482779 基于KAMA与MACD的自适应趋势跟踪量化交易策略-Adaptive-Trend-Following-Strategy-Based-on-KAMA-and-MACD-Integration -> `fmz_482779_kama_cross_macd_atr_bracket_long`

- FMZ source id: 482779 (lineage).
- Source: https://www.fmz.com/strategy/482779 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:01:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | An adaptive average, MACD and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ama_len` [50, 20] x `atr_mult` [3.0, 2.0]: **4 trials**; defaults 50 / 3 (the source's); KAMA fast 3 / slow 30,
ATR 14 and MACD 26 / 52 / 18 fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit` runs every bar from the current close and ATR, so stop and target move with the price. The port
fixes them at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- KAMA recursion and warm-up as written. Long only. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1D" from the
  backtest header (the title says 4-hour). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
