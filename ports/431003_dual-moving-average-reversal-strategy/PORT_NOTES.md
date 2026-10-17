# #431003 Dual Moving Average Reversal Strategy -> `fmz_431003_combo_2_20_ema_atr_reversed`

- FMZ source id: 431003 (lineage).
- Source: https://www.fmz.com/strategy/431003 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-03 16:51:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA and ATR states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `atr_mult` [3.5, 2.0]: **4 trials**; ATR 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
