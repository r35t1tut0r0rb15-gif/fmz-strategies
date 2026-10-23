# #484091 量化交易突破策略首时段ATR止损与EMA斜率优化策略-Quantitative-Breakout-Strategy-First-Hour-ATR-Stop-Loss-with-EMA-Slope-Optimization -> `fmz_484091_first_hour_breakout_ema_vwap_cross_atr_1pct_1h_reversal`

- FMZ source id: 484091 (lineage).
- Source: https://www.fmz.com/strategy/484091 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:46:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR / 1 % bracket from the fill |
| 2 | PASS | Opening-range breakouts confirmed by an EMA / VWAP crossing |
| 3 | PASS | Exchange pair in the header only ("FnO" in the title). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 2.0] x `target` [0.01, 0.02]: **4 trials**; first hour 09:15 + 60 min, EMA 9, ATR 14.

## Ambiguities resolved

- Clock rule on UTC (venue zone); VWAP on broker days; ATR stop fixed at the signal. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range"`.

## Marks

`trailing_stop_pending`
