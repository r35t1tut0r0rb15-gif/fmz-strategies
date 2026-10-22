# #482803 基于Granville与MACD多重信号确认的趋势跟踪交易策略-Trend-Following-Trading-Strategy-Based-on-Granville-and-MACD-Multiple-Signal-Confirmation -> `fmz_482803_granville_ema20_macd_gc_breakout_recross_range_bracket_long`

- FMZ source id: 482803 (lineage).
- Source: https://www.fmz.com/strategy/482803 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:46:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; reversal-bar bracket as fractions of the fill |
| 2 | PASS | Granville / MACD sequence with a range target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [20, 50] x `tp_mult` [1.618, 2.618]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- A repeat sequence's re-sent bracket is pending. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
