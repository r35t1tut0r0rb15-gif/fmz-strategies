# #454735 CSO Custom Signal Oscillator Strategy CSO -> `fmz_454735_open_close_oscillator_zero_cross_reversal`

- FMZ source id: 454735 (lineage).
- Source: https://www.fmz.com/strategy/454735 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:26:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-colour flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
