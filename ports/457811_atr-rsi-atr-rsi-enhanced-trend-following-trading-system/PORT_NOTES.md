# #457811 ATR-RSI增强型趋势追踪交易系统-ATR-RSI-Enhanced-Trend-Following-Trading-System -> `fmz_457811_ut_bot_rsi_filter_band_exit_reversal`

- FMZ source id: 457811 (lineage).
- Source: https://www.fmz.com/strategy/457811 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 17:35:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target exits as close tests |
| 2 | PASS | UT Bot crossings with an RSI filter |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND457811. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_len` [10, 14] x `band_pct` [0.002, 0.01]: **8 trials**; the RSI 14 / 50 fixed.

## Ambiguities resolved

- No bar size (bar_size_pending); target exits as close tests. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`bar_size_pending`
