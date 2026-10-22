# #489017 Dual EMA Trend Following Quantitative Strategy -> `fmz_489017_ema30_60_gap_atr_margin_cross_long`

- FMZ source id: 489017 (lineage).
- Source: https://www.fmz.com/strategy/489017 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:59:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA gap crossings with an ATR margin |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaMarginATRMult` [0.3, 0.6] x `emaFastLen` [30, 15]: **4 trials**; EMA 60, ATR 60.

## Ambiguities resolved

- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
