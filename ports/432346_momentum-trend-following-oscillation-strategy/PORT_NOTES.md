# #432346 Momentum Trend Following Oscillation Strategy -> `fmz_432346_combo_123_adxr`

- FMZ source id: 432346 (lineage).
- Source: https://www.fmz.com/strategy/432346 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 16:46:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and ADXR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `sig2` [45, 30]: **4 trials**; K smoothing 1, D 3, level 50, ADX / ADXR 14 and signal 13 fixed.

## Ambiguities resolved

- Combined state acted on every bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
