# #488133 季度EMA动态回撤交易系统-Quarterly-EMA-Pullback-Trading-System -> `fmz_488133_ema10_21_recross_rsi40_ema_exits_stop15pct_long`

- FMZ source id: 488133 (lineage).
- Source: https://www.fmz.com/strategy/488133 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 13:15:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop as a fraction of the fill |
| 2 | PASS | EMA pullback re-crossings with RSI filter, EMA exits and a percent stop |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_max` [40, 30] x `stop_pct` [15.0, 5.0]: **4 trials**; EMA 10 / 21, exit 8 % over the EMA 10.

## Ambiguities resolved

- A re-signal's moved stop is pending. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`
