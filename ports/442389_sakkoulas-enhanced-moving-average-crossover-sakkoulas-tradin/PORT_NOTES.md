# #442389 动量均线交叉-Sakkoulas-交易策略Enhanced-Moving-Average-Crossover-Sakkoulas-Trading-Strategy -> `fmz_442389_macd_cross_sar_side_atr_stop_reversal`

- FMZ source id: 442389 (lineage).
- Source: https://www.fmz.com/strategy/442389 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 15:14:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | MACD crossings on the SAR side with an ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `signal_smoothing` [5, 9]: **4 trials**; MACD 16 / 6 and the SAR fixed.

## Ambiguities resolved

- SAR parameters and MACD lengths as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
