# #489149 Multi Timeframe Volatility Tracking Quantitative Strategy -> `fmz_489149_ema3_8_cross_ema55_cooldown72_atr_bracket_long`

- FMZ source id: 489149 (lineage).
- Source: https://www.fmz.com/strategy/489149 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 10:50:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a trend filter, cooldown and ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized leveraged quantity and margins stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tradeInterval` [72, 10] x `slMultiplier` [1.2, 2.0]: **4 trials**; EMA 3 / 8 / 55, ATR 14, TP 2 ATR.

## Ambiguities resolved

- The interval is in bars from bar 0. Entries only from flat (a loop follows the bracket). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
