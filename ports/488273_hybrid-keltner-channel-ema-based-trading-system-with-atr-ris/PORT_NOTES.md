# #488273 Hybrid Keltner Channel EMA Based Trading System with ATR Risk Management -> `fmz_488273_keltner20_reversion_ema9_21_trend_ids_reversal`

- FMZ source id: 488273 (lineage).
- Source: https://www.fmz.com/strategy/488273 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 14:21:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | Keltner reversion and EMA trend entries with their own exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.0] x `length` [20, 30]: **4 trials**; EMA 9 / 21 / 50.

## Ambiguities resolved

- One id per position (pyramiding refused); the per-bar bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`trailing_stop_pending`
