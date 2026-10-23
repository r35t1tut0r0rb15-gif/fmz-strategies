# #366415 HIGH LOW SAR -> `fmz_366415_sar_ema50_band_cross_fib_atr_level_reversal`

- FMZ source id: 366415 (lineage).
- Source: https://www.fmz.com/strategy/366415 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 10:33:10). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR band re-entries with ATR / Fibonacci level filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`look_back` [50, 100] x `multi` [2.2, 1.5]: **4 trials**; SAR 0.02 / 0.02 / 0.2, len 100, Fibonacci 1.618 / 4.236.

## Ambiguities resolved

- The helper averages the close whatever it is given, as written (volume not used). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
