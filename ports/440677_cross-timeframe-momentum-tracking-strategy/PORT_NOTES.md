# #440677 Cross Timeframe Momentum Tracking Strategy -> `fmz_440677_reversal123_macd_state_combo`

- FMZ source id: 440677 (lineage).
- Source: https://www.fmz.com/strategy/440677 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 10:21:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and MACD state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `signal_length` [11, 9]: **4 trials**; the 123 smoothing and MACD 8 / 16 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
