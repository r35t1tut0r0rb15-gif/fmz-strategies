# #458237 双重MACD趋势确认交易系统-Dual-MACD-Trend-Confirmation-Trading-System -> `fmz_458237_macd_cross_slow_macd_hist_filter_tick_bracket_long`

- FMZ source id: 458237 (lineage).
- Source: https://www.fmz.com/strategy/458237 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:17:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | MACD cross-ups with a slow-MACD filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed 1-unit quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.01, 2.0] x `sl_atr` [0.002, 1.0]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Header's daily bars followed (comments say 5 minutes); ticks as ATR multiples (1D ~1000). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
