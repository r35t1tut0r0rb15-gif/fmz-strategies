# #488543 Dynamic Multi Dimensional Trend Tracking and Quantitative Trading Strategy -> `fmz_488543_supertrend08_7_dir_ema9_rsi_pct_atr_bracket_reversal`

- FMZ source id: 488543 (lineage).
- Source: https://www.fmz.com/strategy/488543 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:31:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent / ATR bracket as fractions of the fill |
| 2 | PASS | SuperTrend direction with EMA / RSI filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Capital 1000, 10 % of equity, commission 0.075 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMultiplier` [0.8, 2.0] x `tpMultiplier` [3.0, 1.5]: **4 trials**; ATR 7, EMA 9, RSI 14, SL 1 %.

## Ambiguities resolved

- The direction sign is as written. Repeat-state re-sends are pending. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
