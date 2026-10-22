# #483026 Intelligent Dual SMA Crossover Risk Management Trading System -> `fmz_483026_sma9_21_cross_1_2pct_bracket_reversal`

- FMZ source id: 483026 (lineage).
- Source: https://www.fmz.com/strategy/483026 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 09:56:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (riskAmount unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_percent` [1.0, 2.0] x `short_sma` [9, 5]: **4 trials**; SMA 21, target = 2 x stop.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
